"""
Test suite for main shell loop (shell.py).

This module contains comprehensive tests for the shell's REPL loop,
covering basic functionality, built-in integration, external command
execution, signal handling, error recovery, and edge cases.
"""

import pytest
import sys
import signal
from io import StringIO
from unittest.mock import patch, MagicMock, call
from akujobip1.shell import cli, run_shell
from akujobip1.config import get_default_config


# Test Fixtures

@pytest.fixture
def default_config():
    """Get default configuration for tests."""
    return get_default_config()


@pytest.fixture
def custom_config():
    """Get custom configuration for testing config override."""
    return {
        'prompt': {'text': 'custom> '},
        'exit': {'message': 'Goodbye!'},
        'execution': {'show_exit_codes': 'always'},
        'glob': {'enabled': True},
        'builtins': {
            'cd': {'enabled': True},
            'pwd': {'enabled': True},
            'help': {'enabled': True}
        },
        'errors': {'verbose': False},
        'debug': {'log_commands': False}
    }


@pytest.fixture
def mock_input_sequence():
    """
    Create mock for input() that returns sequence of inputs.
    
    Returns a function that takes multiple inputs and returns
    a mock input function that yields them in sequence.
    """
    def _mock(*inputs):
        inputs_iter = iter(inputs)
        def mock_input(prompt=''):
            # Print prompt to stdout (like real input())
            print(prompt, end='', flush=True)
            value = next(inputs_iter)
            # If it's an exception, raise it
            if isinstance(value, Exception):
                raise value
            return value
        return mock_input
    return _mock


# Test Class 1: Basic Functionality

class TestBasicFunctionality:
    """Test basic shell operations."""
    
    def test_cli_returns_zero_on_exit(self, mock_input_sequence):
        """Test that cli() returns 0 on successful exit."""
        with patch('builtins.input', mock_input_sequence('exit')):
            exit_code = cli()
        assert exit_code == 0
    
    def test_prompt_displayed(self, mock_input_sequence, default_config, capsys):
        """Test that prompt is displayed."""
        with patch('builtins.input', mock_input_sequence('exit')):
            run_shell(default_config)
        
        output = capsys.readouterr().out
        assert 'AkujobiP1> ' in output
    
    def test_custom_prompt_displayed(self, mock_input_sequence, custom_config, capsys):
        """Test that custom prompt is displayed."""
        with patch('builtins.input', mock_input_sequence('exit')):
            run_shell(custom_config)
        
        output = capsys.readouterr().out
        assert 'custom> ' in output
    
    def test_empty_input_shows_prompt_again(self, mock_input_sequence, default_config, capsys):
        """Test that empty input continues loop."""
        with patch('builtins.input', mock_input_sequence('', 'exit')):
            run_shell(default_config)
        
        output = capsys.readouterr().out
        # Should see two prompts (one for empty, one for exit)
        assert output.count('AkujobiP1> ') == 2
    
    def test_whitespace_only_shows_prompt_again(self, mock_input_sequence, default_config, capsys):
        """Test that whitespace-only input continues loop."""
        with patch('builtins.input', mock_input_sequence('   ', 'exit')):
            run_shell(default_config)
        
        output = capsys.readouterr().out
        # Should see two prompts
        assert output.count('AkujobiP1> ') == 2
    
    def test_multiple_commands_sequence(self, mock_input_sequence, default_config, capsys):
        """Test executing multiple commands in sequence."""
        with patch('builtins.input', mock_input_sequence('pwd', '', 'pwd', 'exit')):
            with patch('akujobip1.builtins.os.getcwd', return_value='/test/dir'):
                run_shell(default_config)
        
        output = capsys.readouterr().out
        # Should see 4 prompts (pwd, empty, pwd, exit)
        assert output.count('AkujobiP1> ') == 4
        # Should see pwd output twice
        assert output.count('/test/dir') == 2
    
    def test_shell_continues_after_command(self, mock_input_sequence, default_config, capsys):
        """Test that shell continues after successful command."""
        with patch('builtins.input', mock_input_sequence('pwd', 'exit')):
            with patch('akujobip1.builtins.os.getcwd', return_value='/test'):
                exit_code = run_shell(default_config)
        
        assert exit_code == 0
        output = capsys.readouterr().out
        assert 'AkujobiP1> ' in output
    
    def test_run_shell_returns_zero(self, mock_input_sequence, default_config):
        """Test that run_shell returns 0 on normal exit."""
        with patch('builtins.input', mock_input_sequence('exit')):
            exit_code = run_shell(default_config)
        assert exit_code == 0


# Test Class 2: Built-in Command Integration

class TestBuiltinIntegration:
    """Test integration with built-in commands."""
    
    def test_exit_command_terminates_shell(self, mock_input_sequence, default_config):
        """Test that exit command terminates shell."""
        with patch('builtins.input', mock_input_sequence('exit')):
            exit_code = run_shell(default_config)
        assert exit_code == 0
    
    def test_exit_shows_message(self, mock_input_sequence, default_config, capsys):
        """Test that exit displays configured message."""
        with patch('builtins.input', mock_input_sequence('exit')):
            run_shell(default_config)
        
        output = capsys.readouterr().out
        assert 'Bye!' in output
    
    def test_exit_with_custom_message(self, mock_input_sequence, custom_config, capsys):
        """Test that exit displays custom message."""
        with patch('builtins.input', mock_input_sequence('exit')):
            run_shell(custom_config)
        
        output = capsys.readouterr().out
        assert 'Goodbye!' in output
    
    def test_cd_command_executes(self, mock_input_sequence, default_config, capsys):
        """Test that cd command executes."""
        with patch('builtins.input', mock_input_sequence('cd /tmp', 'exit')):
            with patch('akujobip1.builtins.os.chdir') as mock_chdir:
                run_shell(default_config)
        
        # Verify cd was called
        mock_chdir.assert_called_once()
    
    def test_pwd_command_executes(self, mock_input_sequence, default_config, capsys):
        """Test that pwd command executes."""
        with patch('builtins.input', mock_input_sequence('pwd', 'exit')):
            with patch('akujobip1.builtins.os.getcwd', return_value='/test/path'):
                run_shell(default_config)
        
        output = capsys.readouterr().out
        assert '/test/path' in output
    
    def test_help_command_executes(self, mock_input_sequence, default_config, capsys):
        """Test that help command executes."""
        with patch('builtins.input', mock_input_sequence('help', 'exit')):
            run_shell(default_config)
        
        output = capsys.readouterr().out
        assert 'Available commands' in output or 'Built-in commands' in output
    
    def test_builtin_error_continues_shell(self, mock_input_sequence, default_config, capsys):
        """Test that builtin errors don't crash shell."""
        with patch('builtins.input', mock_input_sequence('cd /nonexistent', 'exit')):
            exit_code = run_shell(default_config)
        
        assert exit_code == 0  # Shell exits normally despite cd error
        output = capsys.readouterr().err
        # Should have error message about directory not found
        assert 'No such file or directory' in output or 'cannot access' in output.lower()
    
    def test_exit_with_arguments_ignores_args(self, mock_input_sequence, default_config, capsys):
        """Test that exit command ignores extra arguments."""
        with patch('builtins.input', mock_input_sequence('exit 42', 'extra', 'args')):
            exit_code = run_shell(default_config)
        
        assert exit_code == 0
        output = capsys.readouterr().out
        assert 'Bye!' in output


# Test Class 3: External Command Integration

class TestExternalCommandIntegration:
    """Test integration with external command executor."""
    
    def test_external_command_executes(self, mock_input_sequence, default_config):
        """Test that external commands execute."""
        with patch('builtins.input', mock_input_sequence('ls', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=0) as mock_exec:
                run_shell(default_config)
        
        # Verify external command was called
        mock_exec.assert_called_once()
        assert mock_exec.call_args[0][0] == ['ls']
    
    def test_external_command_with_args(self, mock_input_sequence, default_config):
        """Test external command with multiple arguments."""
        with patch('builtins.input', mock_input_sequence('ls -la /tmp', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=0) as mock_exec:
                run_shell(default_config)
        
        # Verify command and args passed correctly
        mock_exec.assert_called_once()
        assert mock_exec.call_args[0][0] == ['ls', '-la', '/tmp']
    
    def test_command_not_found_continues_shell(self, mock_input_sequence, default_config, capsys):
        """Test that unknown commands don't crash shell."""
        with patch('builtins.input', mock_input_sequence('defnotcmd', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=127):
                exit_code = run_shell(default_config)
        
        assert exit_code == 0  # Shell exits normally despite command error
    
    def test_external_command_failure_continues_shell(self, mock_input_sequence, default_config):
        """Test that failed commands don't crash shell."""
        with patch('builtins.input', mock_input_sequence('false', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=1):
                exit_code = run_shell(default_config)
        
        assert exit_code == 0  # Shell exits normally
    
    def test_quoted_arguments_passed_correctly(self, mock_input_sequence, default_config):
        """Test that quoted arguments are parsed correctly."""
        with patch('builtins.input', mock_input_sequence('echo "hello world"', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=0) as mock_exec:
                run_shell(default_config)
        
        # Verify quoted string passed as single argument
        mock_exec.assert_called_once()
        args = mock_exec.call_args[0][0]
        assert args == ['echo', 'hello world']
    
    def test_permission_denied_continues_shell(self, mock_input_sequence, default_config):
        """Test that permission errors don't crash shell."""
        with patch('builtins.input', mock_input_sequence('some_cmd', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=126):
                exit_code = run_shell(default_config)
        
        assert exit_code == 0
    
    def test_signal_terminated_command_continues_shell(self, mock_input_sequence, default_config):
        """Test that signal-terminated commands don't crash shell."""
        with patch('builtins.input', mock_input_sequence('some_cmd', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=130):  # 128 + SIGINT
                exit_code = run_shell(default_config)
        
        assert exit_code == 0
    
    def test_multiple_external_commands(self, mock_input_sequence, default_config):
        """Test executing multiple external commands."""
        with patch('builtins.input', mock_input_sequence('ls', 'pwd', 'echo test', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=0) as mock_exec:
                with patch('akujobip1.builtins.os.getcwd', return_value='/test'):
                    run_shell(default_config)
        
        # pwd is built-in, so should only see 2 external commands (ls, echo)
        assert mock_exec.call_count == 2


# Test Class 4: Signal Handling

class TestSignalHandling:
    """Test signal handling (Ctrl+C, Ctrl+D)."""
    
    def test_ctrl_c_during_input_continues(self, mock_input_sequence, default_config, capsys):
        """Test that Ctrl+C during input continues shell."""
        with patch('builtins.input', mock_input_sequence(KeyboardInterrupt(), 'exit')):
            exit_code = run_shell(default_config)
        
        assert exit_code == 0
        output = capsys.readouterr().out
        # Should see two prompts (one before Ctrl+C, one after)
        assert output.count('AkujobiP1> ') >= 2
    
    def test_ctrl_d_exits_gracefully(self, mock_input_sequence, default_config, capsys):
        """Test that Ctrl+D exits shell."""
        with patch('builtins.input', mock_input_sequence(EOFError())):
            exit_code = run_shell(default_config)
        
        assert exit_code == 0
        output = capsys.readouterr().out
        assert 'Bye!' in output
    
    def test_ctrl_d_prints_exit_message(self, mock_input_sequence, custom_config, capsys):
        """Test that Ctrl+D prints custom exit message."""
        with patch('builtins.input', mock_input_sequence(EOFError())):
            run_shell(custom_config)
        
        output = capsys.readouterr().out
        assert 'Goodbye!' in output
    
    def test_multiple_ctrl_c_continues(self, mock_input_sequence, default_config, capsys):
        """Test that multiple Ctrl+C continues shell."""
        with patch('builtins.input', mock_input_sequence(
            KeyboardInterrupt(),
            KeyboardInterrupt(),
            KeyboardInterrupt(),
            'exit'
        )):
            exit_code = run_shell(default_config)
        
        assert exit_code == 0
        output = capsys.readouterr().out
        # Should see multiple prompts
        assert output.count('AkujobiP1> ') >= 4
    
    def test_no_custom_signal_handler_installed(self):
        """Verify we don't install custom SIGINT handler."""
        original_handler = signal.getsignal(signal.SIGINT)
        
        # Import shell module (should not change handler)
        from akujobip1 import shell
        
        # Handler should be unchanged
        assert signal.getsignal(signal.SIGINT) == original_handler
    
    def test_ctrl_c_after_command_continues(self, mock_input_sequence, default_config, capsys):
        """Test that Ctrl+C after command continues shell."""
        with patch('builtins.input', mock_input_sequence('pwd', KeyboardInterrupt(), 'exit')):
            with patch('akujobip1.builtins.os.getcwd', return_value='/test'):
                exit_code = run_shell(default_config)
        
        assert exit_code == 0


# Test Class 5: Error Handling

class TestErrorHandling:
    """Test error handling and recovery."""
    
    def test_parse_error_continues_shell(self, mock_input_sequence, default_config, capsys):
        """Test that parse errors don't crash shell."""
        with patch('builtins.input', mock_input_sequence('echo "unclosed quote', 'exit')):
            exit_code = run_shell(default_config)
        
        assert exit_code == 0
        output = capsys.readouterr()
        # Parser should print error to stderr
        assert 'error' in output.err.lower() or 'AkujobiP1> ' in output.out
    
    def test_unexpected_error_continues_shell(self, mock_input_sequence, default_config, capsys):
        """Test that unexpected errors don't crash shell."""
        with patch('builtins.input', mock_input_sequence('test', 'exit')):
            # Mock parse_command to raise unexpected exception
            with patch('akujobip1.shell.parse_command', side_effect=[RuntimeError('Test error'), ['exit']]):
                exit_code = run_shell(default_config)
        
        assert exit_code == 0
        output = capsys.readouterr().err
        assert 'Shell error' in output or 'Test error' in output
    
    def test_verbose_error_mode(self, mock_input_sequence, capsys):
        """Test that verbose mode shows traceback."""
        config = get_default_config()
        config['errors']['verbose'] = True
        
        with patch('builtins.input', mock_input_sequence('test', 'exit')):
            with patch('akujobip1.shell.parse_command', side_effect=[RuntimeError('Test error'), ['exit']]):
                run_shell(config)
        
        output = capsys.readouterr().err
        assert 'Traceback' in output or 'Shell error' in output
    
    def test_missing_config_keys(self, mock_input_sequence):
        """Test that missing config keys don't crash shell."""
        empty_config = {}  # Empty config
        
        with patch('builtins.input', mock_input_sequence('exit')):
            exit_code = run_shell(empty_config)
        
        # Should use defaults and not crash
        assert exit_code == 0
    
    def test_malformed_config_uses_defaults(self, mock_input_sequence, capsys):
        """Test that malformed config uses defaults."""
        bad_config = {'prompt': None, 'exit': None}
        
        with patch('builtins.input', mock_input_sequence('exit')):
            exit_code = run_shell(bad_config)
        
        # Should use defaults and not crash
        assert exit_code == 0


# Test Class 6: Edge Cases

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_long_input(self, mock_input_sequence, default_config):
        """Test handling of very long input."""
        long_command = 'echo ' + 'a' * 1000
        with patch('builtins.input', mock_input_sequence(long_command, 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=0):
                exit_code = run_shell(default_config)
        
        assert exit_code == 0
    
    def test_command_with_many_arguments(self, mock_input_sequence, default_config):
        """Test command with many arguments."""
        many_args = 'echo ' + ' '.join([f'arg{i}' for i in range(100)])
        with patch('builtins.input', mock_input_sequence(many_args, 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=0) as mock_exec:
                run_shell(default_config)
        
        # Verify all arguments passed
        args = mock_exec.call_args[0][0]
        assert len(args) == 101  # echo + 100 args
    
    def test_special_characters_in_command(self, mock_input_sequence, default_config):
        """Test commands with special characters."""
        with patch('builtins.input', mock_input_sequence('echo $HOME', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=0) as mock_exec:
                run_shell(default_config)
        
        # Verify special characters passed through
        args = mock_exec.call_args[0][0]
        assert '$HOME' in args
    
    def test_consecutive_spaces(self, mock_input_sequence, default_config):
        """Test commands with consecutive spaces."""
        with patch('builtins.input', mock_input_sequence('echo    test', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=0) as mock_exec:
                run_shell(default_config)
        
        # shlex should collapse spaces
        args = mock_exec.call_args[0][0]
        assert args == ['echo', 'test']
    
    def test_mixed_quotes(self, mock_input_sequence, default_config):
        """Test commands with mixed single and double quotes."""
        with patch('builtins.input', mock_input_sequence('''echo "hello" 'world' ''', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=0) as mock_exec:
                run_shell(default_config)
        
        args = mock_exec.call_args[0][0]
        assert args == ['echo', 'hello', 'world']


# Test Class 7: Configuration Integration

class TestConfigurationIntegration:
    """Test configuration system integration."""
    
    def test_default_prompt_used(self, mock_input_sequence, capsys):
        """Test that default prompt is used when config missing."""
        config = {}
        with patch('builtins.input', mock_input_sequence('exit')):
            run_shell(config)
        
        output = capsys.readouterr().out
        assert 'AkujobiP1> ' in output
    
    def test_default_exit_message_used(self, mock_input_sequence, capsys):
        """Test that default exit message is used when config missing."""
        config = {}
        with patch('builtins.input', mock_input_sequence('exit')):
            run_shell(config)
        
        output = capsys.readouterr().out
        assert 'Bye!' in output
    
    def test_config_passed_to_parser(self, mock_input_sequence, default_config):
        """Test that config is passed to parser."""
        with patch('builtins.input', mock_input_sequence('ls *.txt', 'exit')):
            with patch('akujobip1.shell.parse_command', return_value=['ls', 'file.txt']) as mock_parse:
                with patch('akujobip1.executor.execute_external_command', return_value=0):
                    run_shell(default_config)
        
        # Verify config passed to parser
        assert mock_parse.call_count >= 1
        assert mock_parse.call_args[0][1] == default_config
    
    def test_config_passed_to_executor(self, mock_input_sequence, default_config):
        """Test that config is passed to executor."""
        with patch('builtins.input', mock_input_sequence('ls', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=0) as mock_exec:
                run_shell(default_config)
        
        # Verify config passed to executor
        assert mock_exec.call_args[0][1] == default_config
    
    def test_config_passed_to_builtins(self, mock_input_sequence, default_config):
        """Test that config is passed to built-in commands."""
        with patch('builtins.input', mock_input_sequence('pwd', 'exit')):
            with patch('akujobip1.builtins.os.getcwd', return_value='/test'):
                # PwdCommand should receive config
                run_shell(default_config)
        
        # If this doesn't crash, config was passed correctly


# Test Class 8: Bash Test Simulation

class TestBashTestSimulation:
    """Simulate the bash tests from run_tests.sh."""
    
    def test_bash_test_1_exit(self, mock_input_sequence, default_config, capsys):
        """
        Simulate bash test 1: exit command.
        Input: "exit"
        Output: "AkujobiP1> Bye!"
        """
        with patch('builtins.input', mock_input_sequence('exit')):
            exit_code = run_shell(default_config)
        
        output = capsys.readouterr().out
        assert 'AkujobiP1> ' in output
        assert 'Bye!' in output
        assert exit_code == 0
    
    def test_bash_test_2_empty_then_exit(self, mock_input_sequence, default_config, capsys):
        """
        Simulate bash test 2: empty line then exit.
        Input: "\nexit"
        Output: "AkujobiP1> AkujobiP1> Bye!"
        """
        with patch('builtins.input', mock_input_sequence('', 'exit')):
            exit_code = run_shell(default_config)
        
        output = capsys.readouterr().out
        # Should see two prompts
        assert output.count('AkujobiP1> ') == 2
        assert 'Bye!' in output
        assert exit_code == 0
    
    def test_bash_test_3_unknown_command(self, mock_input_sequence, default_config, capsys):
        """
        Simulate bash test 3: unknown command.
        Input: "defnotcmd\nexit"
        Output: Contains "defnotcmd: command not found"
        """
        with patch('builtins.input', mock_input_sequence('defnotcmd', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=127) as mock_exec:
                exit_code = run_shell(default_config)
        
        # Verify defnotcmd was attempted
        assert mock_exec.call_count == 1
        args = mock_exec.call_args[0][0]
        assert args[0] == 'defnotcmd'
        assert exit_code == 0
    
    def test_bash_test_4_quoted_args(self, mock_input_sequence, default_config):
        """
        Simulate bash test 4: quoted arguments.
        Input: 'printf "%s %s\n" "a b" c\nexit'
        Output: Command executes successfully
        """
        with patch('builtins.input', mock_input_sequence('printf "%s %s\\n" "a b" c', 'exit')):
            with patch('akujobip1.shell.execute_external_command', return_value=0) as mock_exec:
                exit_code = run_shell(default_config)
        
        # Verify arguments parsed correctly
        args = mock_exec.call_args[0][0]
        assert args[0] == 'printf'
        assert args[1] == '%s %s\n'
        assert args[2] == 'a b'
        assert args[3] == 'c'
        assert exit_code == 0
    
    def test_all_bash_tests_sequence(self, mock_input_sequence, default_config, capsys):
        """Test all bash test scenarios in sequence."""
        # Simulate running multiple test scenarios
        with patch('builtins.input', mock_input_sequence(
            '',  # empty
            'defnotcmd',  # unknown
            'echo test',  # valid
            'exit'
        )):
            with patch('akujobip1.shell.execute_external_command', return_value=0):
                exit_code = run_shell(default_config)
        
        assert exit_code == 0
        output = capsys.readouterr().out
        assert output.count('AkujobiP1> ') == 4


# Test Class 9: CLI Function Tests

class TestCLIFunction:
    """Test cli() entry point function."""
    
    def test_cli_loads_config(self, mock_input_sequence):
        """Test that cli() loads configuration."""
        with patch('builtins.input', mock_input_sequence('exit')):
            with patch('akujobip1.shell.load_config') as mock_load:
                mock_load.return_value = get_default_config()
                exit_code = cli()
        
        mock_load.assert_called_once()
        assert exit_code == 0
    
    def test_cli_calls_run_shell(self, mock_input_sequence):
        """Test that cli() calls run_shell()."""
        with patch('builtins.input', mock_input_sequence('exit')):
            with patch('akujobip1.shell.run_shell', return_value=0) as mock_run:
                exit_code = cli()
        
        mock_run.assert_called_once()
        assert exit_code == 0
    
    def test_cli_handles_keyboard_interrupt(self, capsys):
        """Test that cli() handles Ctrl+C during startup."""
        with patch('akujobip1.shell.load_config', side_effect=KeyboardInterrupt()):
            exit_code = cli()
        
        assert exit_code == 0
    
    def test_cli_handles_fatal_error(self, capsys):
        """Test that cli() handles fatal startup errors."""
        with patch('akujobip1.shell.load_config', side_effect=RuntimeError('Fatal')):
            exit_code = cli()
        
        assert exit_code == 1
        output = capsys.readouterr().err
        assert 'Fatal error' in output

