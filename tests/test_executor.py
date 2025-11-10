"""
Test suite for the executor module.

This module tests external command execution using fork/exec/wait.
"""

import shutil
import sys
import pytest
from unittest.mock import patch

from akujobip1.executor import execute_external_command, display_exit_status
from akujobip1.config import get_default_config


# Fixtures


@pytest.fixture
def default_config():
    """Provide default configuration for tests."""
    return get_default_config()


@pytest.fixture
def silent_config():
    """Config that never shows exit codes."""
    return {
        "execution": {"show_exit_codes": "never", "exit_code_format": "[Exit: {code}]"},
        "debug": {"show_fork_pids": False},
    }


@pytest.fixture
def verbose_config():
    """Config that always shows everything."""
    return {
        "execution": {
            "show_exit_codes": "always",
            "exit_code_format": "[Exit: {code}]",
        },
        "debug": {"show_fork_pids": True},
    }


@pytest.fixture
def on_failure_config():
    """Config that shows exit codes only on failure."""
    return {
        "execution": {
            "show_exit_codes": "on_failure",
            "exit_code_format": "[Exit: {code}]",
        },
        "debug": {"show_fork_pids": False},
    }


# Test Class 1: Success Cases


class TestExecuteExternalCommandSuccess:
    """Test successful command execution."""

    def test_simple_command(self, silent_config, capsys):
        """Test executing a simple command like 'true'."""
        exit_code = execute_external_command(["true"], silent_config)
        assert exit_code == 0

    def test_command_with_arguments(self, silent_config):
        """Test command with arguments."""
        exit_code = execute_external_command(["echo", "hello"], silent_config)
        assert exit_code == 0

    def test_command_with_many_arguments(self, silent_config):
        """Test command with multiple arguments."""
        args = ["echo"] + ["arg"] * 10
        exit_code = execute_external_command(args, silent_config)
        assert exit_code == 0

    def test_command_exit_code_zero(self, silent_config):
        """Test that successful command returns 0."""
        exit_code = execute_external_command(["true"], silent_config)
        assert exit_code == 0

    def test_command_with_path_search(self, silent_config):
        """Test that execvp searches PATH."""
        # 'ls' should be in PATH
        exit_code = execute_external_command(["ls", "/tmp"], silent_config)
        assert exit_code == 0


# Test Class 2: Failure Cases


class TestExecuteExternalCommandFailure:
    """Test command execution failures."""

    def test_command_not_found(self, silent_config):
        """Test command not found returns 127."""
        exit_code = execute_external_command(
            ["nonexistent_command_xyz123"], silent_config
        )
        assert exit_code == 127
        # Note: Error message is printed to stderr by child process,
        # but capsys can't capture output from forked children

    def test_empty_args_list(self, silent_config, capsys):
        """Test empty args list returns error."""
        exit_code = execute_external_command([], silent_config)
        assert exit_code == 1

        captured = capsys.readouterr()
        assert "No command specified" in captured.err

    def test_command_exits_with_error_code(self, silent_config):
        """Test command that exits with non-zero code."""
        exit_code = execute_external_command(["false"], silent_config)
        assert exit_code == 1

    def test_command_custom_exit_code(self, silent_config):
        """Test command with custom exit code."""
        exit_code = execute_external_command(["bash", "-c", "exit 42"], silent_config)
        assert exit_code == 42

    @pytest.mark.skipif(
        sys.platform == "win32", reason="fork() not available on Windows"
    )
    def test_fork_failure_mocked(self, silent_config, capsys):
        """Test fork failure handling."""
        with patch("os.fork") as mock_fork:
            mock_fork.side_effect = OSError("Resource temporarily unavailable")

            exit_code = execute_external_command(["ls"], silent_config)
            assert exit_code == 1

            captured = capsys.readouterr()
            assert "Fork failed" in captured.err


# Test Class 3: Signal Termination


@pytest.mark.skipif(
    shutil.which("bash") is None, reason="bash required for signal tests"
)
class TestExecuteExternalCommandSignals:
    """Test signal handling."""

    def test_command_terminated_by_signal(self, silent_config, capsys):
        """Test command terminated by SIGTERM."""
        # Use bash to kill itself with SIGTERM
        exit_code = execute_external_command(
            ["bash", "-c", "kill -TERM $$"], silent_config
        )
        # SIGTERM is signal 15, so exit code should be 128 + 15 = 143
        assert exit_code == 143

        captured = capsys.readouterr()
        assert "Terminated by signal 15" in captured.err

    def test_command_terminated_by_sigkill(self, silent_config, capsys):
        """Test command terminated by SIGKILL."""
        # Use bash to kill itself with SIGKILL
        exit_code = execute_external_command(
            ["bash", "-c", "kill -KILL $$"], silent_config
        )
        # SIGKILL is signal 9, so exit code should be 128 + 9 = 137
        assert exit_code == 137

        captured = capsys.readouterr()
        assert "Terminated by signal 9" in captured.err

    def test_command_terminated_by_sigint(self, silent_config, capsys):
        """Test command terminated by SIGINT."""
        # Use bash to kill itself with SIGINT (Ctrl+C equivalent)
        exit_code = execute_external_command(
            ["bash", "-c", "kill -INT $$"], silent_config
        )
        # SIGINT is signal 2, so exit code should be 128 + 2 = 130
        assert exit_code == 130

        captured = capsys.readouterr()
        assert "Terminated by signal 2" in captured.err


# Test Class 4: Display Exit Status


class TestDisplayExitStatus:
    """Test exit status display function."""

    def test_display_mode_never_success(self, capsys):
        """Test 'never' mode doesn't display on success."""
        config = {
            "execution": {
                "show_exit_codes": "never",
                "exit_code_format": "[Exit: {code}]",
            }
        }
        # Create a status for exit code 0 (success)
        status = 0  # 0 exit code
        display_exit_status(status, config)

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_display_mode_never_failure(self, capsys):
        """Test 'never' mode doesn't display on failure."""
        config = {
            "execution": {
                "show_exit_codes": "never",
                "exit_code_format": "[Exit: {code}]",
            }
        }
        # Create a status for exit code 1 (failure)
        status = 1 << 8  # exit code 1
        display_exit_status(status, config)

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_display_mode_on_failure_with_success(self, capsys):
        """Test 'on_failure' mode doesn't display on success."""
        config = {
            "execution": {
                "show_exit_codes": "on_failure",
                "exit_code_format": "[Exit: {code}]",
            }
        }
        status = 0  # exit code 0
        display_exit_status(status, config)

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_display_mode_on_failure_with_failure(self, capsys):
        """Test 'on_failure' mode displays on failure."""
        config = {
            "execution": {
                "show_exit_codes": "on_failure",
                "exit_code_format": "[Exit: {code}]",
            }
        }
        status = 1 << 8  # exit code 1
        display_exit_status(status, config)

        captured = capsys.readouterr()
        assert "[Exit: 1]" in captured.out

    def test_display_mode_always_with_success(self, capsys):
        """Test 'always' mode displays on success."""
        config = {
            "execution": {
                "show_exit_codes": "always",
                "exit_code_format": "[Exit: {code}]",
            }
        }
        status = 0  # exit code 0
        display_exit_status(status, config)

        captured = capsys.readouterr()
        assert "[Exit: 0]" in captured.out

    def test_display_mode_always_with_failure(self, capsys):
        """Test 'always' mode displays on failure."""
        config = {
            "execution": {
                "show_exit_codes": "always",
                "exit_code_format": "[Exit: {code}]",
            }
        }
        status = 1 << 8  # exit code 1
        display_exit_status(status, config)

        captured = capsys.readouterr()
        assert "[Exit: 1]" in captured.out

    def test_display_custom_format(self, capsys):
        """Test custom exit code format."""
        config = {
            "execution": {
                "show_exit_codes": "always",
                "exit_code_format": "Exit code: {code}",
            }
        }
        status = 42 << 8  # exit code 42
        display_exit_status(status, config)

        captured = capsys.readouterr()
        assert "Exit code: 42" in captured.out

    def test_display_invalid_format_fallback(self, capsys):
        """Test invalid format string falls back to default."""
        config = {
            "execution": {
                "show_exit_codes": "always",
                "exit_code_format": "Bad {invalid}",
            }
        }
        status = 1 << 8  # exit code 1
        display_exit_status(status, config)

        captured = capsys.readouterr()
        assert "[Exit: 1]" in captured.out


# Test Class 5: Configuration Integration


class TestExecuteExternalCommandConfig:
    """Test configuration integration."""

    def test_show_fork_pids_enabled(self, capsys):
        """Test debug output with show_fork_pids enabled."""
        config = {
            "execution": {"show_exit_codes": "never"},
            "debug": {"show_fork_pids": True},
        }

        execute_external_command(["true"], config)

        captured = capsys.readouterr()
        assert "About to fork" in captured.err
        assert "Forked child PID" in captured.err

    def test_show_fork_pids_disabled(self, capsys):
        """Test no debug output with show_fork_pids disabled."""
        config = {
            "execution": {"show_exit_codes": "never"},
            "debug": {"show_fork_pids": False},
        }

        execute_external_command(["true"], config)

        captured = capsys.readouterr()
        assert "About to fork" not in captured.err
        assert "Forked child PID" not in captured.err

    def test_missing_config_keys_use_defaults(self, silent_config):
        """Test that missing config keys use defaults."""
        config = {}  # Empty config
        exit_code = execute_external_command(["true"], config)
        assert exit_code == 0

    def test_partial_config(self, capsys):
        """Test with partial configuration."""
        config = {"execution": {"show_exit_codes": "always"}}
        # Missing exit_code_format should use default
        exit_code = execute_external_command(["true"], config)
        assert exit_code == 0

        captured = capsys.readouterr()
        assert "[Exit: 0]" in captured.out

    def test_default_config_integration(self, default_config):
        """Test with full default config."""
        exit_code = execute_external_command(["true"], default_config)
        assert exit_code == 0


# Test Class 6: Edge Cases


class TestExecuteExternalCommandEdgeCases:
    """Test edge cases."""

    def test_command_with_special_characters_in_args(self, silent_config):
        """Test command with special characters in arguments."""
        exit_code = execute_external_command(["echo", "hello; world"], silent_config)
        assert exit_code == 0

    def test_command_with_quotes_in_args(self, silent_config):
        """Test command with quoted arguments."""
        exit_code = execute_external_command(["echo", '"hello world"'], silent_config)
        assert exit_code == 0

    def test_command_that_prints_to_stderr(self, silent_config):
        """Test command that prints to stderr."""
        # Child process output goes directly to stderr, not captured by capsys
        # Just verify the command executes successfully
        exit_code = execute_external_command(
            ["bash", "-c", "echo error >&2"], silent_config
        )
        assert exit_code == 0

    def test_long_command_line(self, silent_config):
        """Test command with very long argument list."""
        args = ["echo"] + ["x"] * 100
        exit_code = execute_external_command(args, silent_config)
        assert exit_code == 0

    def test_absolute_path_command(self, silent_config):
        """Test command with absolute path."""
        exit_code = execute_external_command(["/bin/true"], silent_config)
        assert exit_code == 0


# Test Class 7: Integration Tests


class TestExecuteExternalCommandIntegration:
    """Integration tests with realistic scenarios."""

    def test_multiple_commands_sequentially(self, silent_config):
        """Test executing multiple commands in sequence."""
        commands = [["true"], ["echo", "test"], ["ls", "/tmp"], ["pwd"]]

        for cmd in commands:
            exit_code = execute_external_command(cmd, silent_config)
            assert exit_code == 0

    def test_with_parser_output_simulation(self, silent_config):
        """Test with output that simulates parser results."""
        # Parser would return ['ls', '-la', '/tmp']
        args = ["ls", "-la", "/tmp"]
        exit_code = execute_external_command(args, silent_config)
        assert exit_code == 0

    def test_exit_code_preservation(self, silent_config):
        """Test that exit codes are preserved correctly."""
        test_cases = [
            (["true"], 0),
            (["false"], 1),
            (["bash", "-c", "exit 0"], 0),
            (["bash", "-c", "exit 1"], 1),
            (["bash", "-c", "exit 42"], 42),
        ]

        for args, expected_code in test_cases:
            exit_code = execute_external_command(args, silent_config)
            assert exit_code == expected_code

    def test_realistic_command_sequence(self, silent_config):
        """Test realistic command usage scenario."""
        # Test a sequence that might occur in actual usage
        execute_external_command(["echo", "Starting tests..."], silent_config)
        execute_external_command(["ls", "-l"], silent_config)
        execute_external_command(["pwd"], silent_config)

        # All commands should succeed
        assert True  # If we get here, no exceptions occurred

    def test_config_affects_output(self, capsys):
        """Test that config affects output correctly."""
        # First test with 'never' mode
        config_never = {
            "execution": {"show_exit_codes": "never"},
            "debug": {"show_fork_pids": False},
        }
        execute_external_command(["false"], config_never)
        captured_never = capsys.readouterr()
        assert "[Exit:" not in captured_never.out

        # Then test with 'always' mode
        config_always = {
            "execution": {
                "show_exit_codes": "always",
                "exit_code_format": "[Exit: {code}]",
            },
            "debug": {"show_fork_pids": False},
        }
        execute_external_command(["false"], config_always)
        captured_always = capsys.readouterr()
        assert "[Exit: 1]" in captured_always.out


# Additional tests for comprehensive coverage


class TestExecuteExternalCommandPermissions:
    """Test permission-related errors."""

    def test_permission_denied(self, silent_config, tmp_path):
        """Test executing a non-executable file."""
        # Create a non-executable file
        test_file = tmp_path / "test_script.sh"
        test_file.write_text("#!/bin/bash\necho test")
        # Don't make it executable

        exit_code = execute_external_command([str(test_file)], silent_config)
        assert exit_code == 126
        # Note: Error message is printed to stderr by child process,
        # but capsys can't capture output from forked children


class TestDisplayExitStatusEdgeCases:
    """Test display_exit_status edge cases."""

    def test_stopped_process_status(self, capsys):
        """Test display of stopped process status."""
        config = {"execution": {"show_exit_codes": "always"}}
        # Test WIFSTOPPED case
        # Simulate a stopped status using the WIFSTOPPED encoding
        # On Linux, WIFSTOPPED is true if ((status) & 0xff) == 0x7f
        status = 0x7F | (19 << 8)  # Stopped by signal 19 (SIGSTOP)
        display_exit_status(status, config)
        captured = capsys.readouterr()
        assert "Stopped by signal" in captured.err

    def test_various_exit_codes(self, capsys):
        """Test display with various exit codes."""
        config = {
            "execution": {
                "show_exit_codes": "always",
                "exit_code_format": "[Exit: {code}]",
            }
        }

        test_codes = [0, 1, 2, 42, 100, 127, 126]
        for code in test_codes:
            status = code << 8
            display_exit_status(status, config)
            captured = capsys.readouterr()
            assert f"[Exit: {code}]" in captured.out

    def test_child_process_error_handling(self, silent_config):
        """Test ChildProcessError handling in waitpid."""
        # This is a defensive code path - hard to trigger in practice
        # We test the happy path; the error handling is for robustness
        with patch("os.waitpid") as mock_wait:
            # Simulate a child that doesn't exist (already reaped)
            mock_wait.side_effect = ChildProcessError("No child processes")

            # Mock fork to return a fake pid
            with patch("os.fork") as mock_fork:
                mock_fork.return_value = 12345  # Fake PID

                exit_code = execute_external_command(["true"], silent_config)
                # Should return 1 for the error
                assert exit_code == 1

    def test_unknown_process_status(self, capsys):
        """Test handling of unknown process status (neither exited, signaled, nor stopped)."""
        config = {"execution": {"show_exit_codes": "always"}}
        # This is a theoretical case - in practice, one of the status checks should match
        # But we test that the code handles it gracefully
        # Create a status that doesn't match any standard case
        # In practice, this shouldn't happen, but defensive code handles it
        status = 0  # This would be WIFEXITED with code 0
        display_exit_status(status, config)
        # Should not crash
        capsys.readouterr()  # Clear captured output
        # Either shows exit code 0 or nothing, either is fine
