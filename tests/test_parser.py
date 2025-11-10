"""
Tests for parser module (Phase 2.2).

This module contains comprehensive tests for command parsing and wildcard expansion.
Tests cover normal operation, edge cases, error handling, and configuration integration.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

from akujobip1.parser import parse_command, expand_wildcards, _contains_wildcard


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def default_config():
    """Provide a default configuration for testing."""
    return {"glob": {"enabled": True, "show_expansions": False}}


@pytest.fixture
def config_glob_disabled():
    """Provide configuration with glob expansion disabled."""
    return {"glob": {"enabled": False, "show_expansions": False}}


@pytest.fixture
def temp_dir_with_files():
    """
    Create a temporary directory with test files for glob testing.

    Creates:
    - file1.txt
    - file2.txt
    - test1.py
    - test2.py
    - data.json
    - readme.md
    """
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    old_cwd = os.getcwd()

    try:
        # Change to temp directory
        os.chdir(temp_dir)

        # Create test files
        Path("file1.txt").touch()
        Path("file2.txt").touch()
        Path("test1.py").touch()
        Path("test2.py").touch()
        Path("data.json").touch()
        Path("readme.md").touch()

        yield temp_dir
    finally:
        # Restore original directory and clean up
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================================
# Test parse_command() - Basic Functionality
# ============================================================================


class TestParseCommandBasic:
    """Test basic command parsing functionality."""

    def test_simple_command(self, default_config):
        """Test parsing a simple command without arguments."""
        result = parse_command("ls", default_config)
        assert result == ["ls"]

    def test_command_with_single_argument(self, default_config):
        """Test parsing a command with one argument."""
        result = parse_command("ls -l", default_config)
        assert result == ["ls", "-l"]

    def test_command_with_multiple_arguments(self, default_config):
        """Test parsing a command with multiple arguments."""
        result = parse_command("cp file1.txt file2.txt", default_config)
        assert result == ["cp", "file1.txt", "file2.txt"]

    def test_command_with_many_arguments(self, default_config):
        """Test parsing a command with many arguments (>3)."""
        result = parse_command("echo a b c d e f g", default_config)
        assert result == ["echo", "a", "b", "c", "d", "e", "f", "g"]

    def test_command_with_flags(self, default_config):
        """Test parsing a command with various flags."""
        result = parse_command("ls -la -h --color=auto", default_config)
        assert result == ["ls", "-la", "-h", "--color=auto"]


# ============================================================================
# Test parse_command() - Quoted Arguments
# ============================================================================


class TestParseCommandQuotes:
    """Test parsing commands with quoted arguments."""

    def test_double_quoted_argument(self, default_config):
        """Test parsing an argument with double quotes."""
        result = parse_command('echo "hello world"', default_config)
        assert result == ["echo", "hello world"]

    def test_single_quoted_argument(self, default_config):
        """Test parsing an argument with single quotes."""
        result = parse_command("echo 'hello world'", default_config)
        assert result == ["echo", "hello world"]

    def test_multiple_quoted_arguments(self, default_config):
        """Test parsing multiple quoted arguments."""
        result = parse_command('printf "%s %s" "arg1" "arg2"', default_config)
        assert result == ["printf", "%s %s", "arg1", "arg2"]

    def test_mixed_quoted_and_unquoted(self, default_config):
        """Test parsing mix of quoted and unquoted arguments."""
        result = parse_command("cmd arg1 \"arg 2\" arg3 'arg 4'", default_config)
        assert result == ["cmd", "arg1", "arg 2", "arg3", "arg 4"]

    def test_empty_quoted_string(self, default_config):
        """Test parsing empty quoted strings."""
        result = parse_command("echo \"\" ''", default_config)
        assert result == ["echo", "", ""]

    def test_quotes_with_special_chars(self, default_config):
        """Test parsing quoted strings with special characters."""
        result = parse_command("echo \"test$HOME\" 'test$HOME'", default_config)
        assert result == ["echo", "test$HOME", "test$HOME"]

    def test_escaped_quotes(self, default_config):
        """Test parsing escaped quotes."""
        result = parse_command('echo "say \\"hello\\""', default_config)
        assert result == ["echo", 'say "hello"']


# ============================================================================
# Test parse_command() - Empty and Whitespace Input
# ============================================================================


class TestParseCommandEmpty:
    """Test parsing empty and whitespace-only input."""

    def test_empty_string(self, default_config):
        """Test parsing an empty string."""
        result = parse_command("", default_config)
        assert result == []

    def test_whitespace_only_spaces(self, default_config):
        """Test parsing string with only spaces."""
        result = parse_command("   ", default_config)
        assert result == []

    def test_whitespace_only_tabs(self, default_config):
        """Test parsing string with only tabs."""
        result = parse_command("\t\t\t", default_config)
        assert result == []

    def test_whitespace_only_mixed(self, default_config):
        """Test parsing string with mixed whitespace."""
        result = parse_command("  \t  \n  ", default_config)
        assert result == []

    def test_command_with_extra_whitespace(self, default_config):
        """Test parsing command with excessive whitespace."""
        result = parse_command("  ls   -l   file.txt  ", default_config)
        assert result == ["ls", "-l", "file.txt"]


# ============================================================================
# Test parse_command() - Error Handling
# ============================================================================


class TestParseCommandErrors:
    """Test error handling in command parsing."""

    def test_unclosed_double_quote(self, default_config, capsys):
        """Test handling of unclosed double quote."""
        result = parse_command('echo "hello', default_config)
        assert result == []
        # Check that error was printed to stderr
        captured = capsys.readouterr()
        assert "Parse error" in captured.err

    def test_unclosed_single_quote(self, default_config, capsys):
        """Test handling of unclosed single quote."""
        result = parse_command("echo 'hello", default_config)
        assert result == []
        captured = capsys.readouterr()
        assert "Parse error" in captured.err

    def test_mismatched_quotes(self, default_config, capsys):
        """Test handling of mismatched quotes."""
        result = parse_command("echo \"hello'", default_config)
        assert result == []
        captured = capsys.readouterr()
        assert "Parse error" in captured.err


# ============================================================================
# Test expand_wildcards() - Basic Functionality
# ============================================================================


class TestExpandWildcardsBasic:
    """Test basic wildcard expansion functionality."""

    def test_no_wildcards(self, default_config):
        """Test that arguments without wildcards are unchanged."""
        args = ["ls", "-l", "file.txt"]
        result = expand_wildcards(args, default_config)
        assert result == ["ls", "-l", "file.txt"]

    def test_star_wildcard_with_matches(self, default_config, temp_dir_with_files):
        """Test * wildcard expansion with matches."""
        args = ["ls", "*.txt"]
        result = expand_wildcards(args, default_config)
        # Should expand to file1.txt and file2.txt (sorted)
        assert result == ["ls", "file1.txt", "file2.txt"]

    def test_star_wildcard_no_matches(self, default_config, temp_dir_with_files):
        """Test * wildcard with no matches keeps literal."""
        args = ["ls", "*.xyz"]
        result = expand_wildcards(args, default_config)
        # No matches, should keep literal
        assert result == ["ls", "*.xyz"]

    def test_question_mark_wildcard(self, default_config, temp_dir_with_files):
        """Test ? wildcard expansion."""
        args = ["cat", "file?.txt"]
        result = expand_wildcards(args, default_config)
        assert result == ["cat", "file1.txt", "file2.txt"]

    def test_bracket_wildcard(self, default_config, temp_dir_with_files):
        """Test [...] wildcard expansion."""
        args = ["cat", "file[12].txt"]
        result = expand_wildcards(args, default_config)
        assert result == ["cat", "file1.txt", "file2.txt"]

    def test_multiple_wildcards_same_arg(self, default_config, temp_dir_with_files):
        """Test multiple wildcard types in same argument."""
        args = ["ls", "file*.???"]
        result = expand_wildcards(args, default_config)
        # Should match file1.txt and file2.txt
        assert "file1.txt" in result
        assert "file2.txt" in result

    def test_multiple_wildcard_arguments(self, default_config, temp_dir_with_files):
        """Test multiple arguments with wildcards."""
        args = ["cp", "*.txt", "*.py"]
        result = expand_wildcards(args, default_config)
        # Should expand both wildcards
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "test1.py" in result
        assert "test2.py" in result


# ============================================================================
# Test expand_wildcards() - Configuration Integration
# ============================================================================


class TestExpandWildcardsConfig:
    """Test wildcard expansion with different configurations."""

    def test_glob_disabled(self, config_glob_disabled, temp_dir_with_files):
        """Test that wildcards are not expanded when glob is disabled."""
        args = ["ls", "*.txt"]
        result = expand_wildcards(args, config_glob_disabled)
        # Should NOT expand, keep literal
        assert result == ["ls", "*.txt"]

    def test_glob_disabled_no_wildcards(self, config_glob_disabled):
        """Test that normal args work when glob is disabled."""
        args = ["ls", "-l", "file.txt"]
        result = expand_wildcards(args, config_glob_disabled)
        assert result == ["ls", "-l", "file.txt"]

    def test_missing_glob_config_defaults_enabled(self, temp_dir_with_files):
        """Test that missing glob config defaults to enabled."""
        config = {}  # No glob section
        args = ["ls", "*.txt"]
        result = expand_wildcards(args, config)
        # Should still expand (default behavior)
        assert "file1.txt" in result
        assert "file2.txt" in result

    def test_partial_glob_config(self, temp_dir_with_files):
        """Test with partial glob configuration."""
        config = {"glob": {}}  # Empty glob section
        args = ["ls", "*.txt"]
        result = expand_wildcards(args, config)
        # Should default to enabled
        assert "file1.txt" in result
        assert "file2.txt" in result


# ============================================================================
# Test expand_wildcards() - Edge Cases
# ============================================================================


class TestExpandWildcardsEdgeCases:
    """Test edge cases in wildcard expansion."""

    def test_empty_args_list(self, default_config):
        """Test expanding empty arguments list."""
        result = expand_wildcards([], default_config)
        assert result == []

    def test_wildcard_in_middle_of_arg(self, default_config, temp_dir_with_files):
        """Test wildcard in middle of argument."""
        args = ["cat", "file*.txt"]
        result = expand_wildcards(args, default_config)
        assert "file1.txt" in result
        assert "file2.txt" in result

    def test_wildcard_at_beginning(self, default_config, temp_dir_with_files):
        """Test wildcard at beginning of argument."""
        args = ["cat", "*.txt"]
        result = expand_wildcards(args, default_config)
        assert "file1.txt" in result
        assert "file2.txt" in result

    def test_wildcard_at_end(self, default_config, temp_dir_with_files):
        """Test wildcard at end of argument."""
        args = ["cat", "file*"]
        result = expand_wildcards(args, default_config)
        assert "file1.txt" in result
        assert "file2.txt" in result

    def test_multiple_stars(self, default_config, temp_dir_with_files):
        """Test multiple * wildcards in one argument."""
        args = ["ls", "*.*"]
        result = expand_wildcards(args, default_config)
        # Should match all files with extensions
        assert len(result) > 1
        assert "ls" not in result[1:]  # ls is command, not a match

    def test_sorted_expansion(self, default_config, temp_dir_with_files):
        """Test that wildcard expansion is sorted."""
        args = ["cat", "*.txt"]
        result = expand_wildcards(args, default_config)
        # Should be sorted alphabetically
        txt_files = [f for f in result if f.endswith(".txt")]
        assert txt_files == sorted(txt_files)


# ============================================================================
# Test _contains_wildcard() Helper
# ============================================================================


class TestContainsWildcard:
    """Test the _contains_wildcard() helper function."""

    def test_star_wildcard(self):
        """Test detection of * wildcard."""
        assert _contains_wildcard("*.txt") is True

    def test_question_mark_wildcard(self):
        """Test detection of ? wildcard."""
        assert _contains_wildcard("file?.txt") is True

    def test_bracket_wildcard(self):
        """Test detection of [...] wildcard."""
        assert _contains_wildcard("file[12].txt") is True

    def test_no_wildcards(self):
        """Test that regular strings return False."""
        assert _contains_wildcard("regular_file.txt") is False

    def test_empty_string(self):
        """Test empty string returns False."""
        assert _contains_wildcard("") is False

    def test_multiple_wildcards(self):
        """Test string with multiple wildcard types."""
        assert _contains_wildcard("file*?.txt") is True

    def test_wildcard_like_but_not(self):
        """Test that similar but non-wildcard chars don't trigger."""
        # These don't contain *, ?, or [
        assert _contains_wildcard("file.txt") is False
        assert _contains_wildcard("test123") is False


# ============================================================================
# Test Integration - parse_command() with Wildcard Expansion
# ============================================================================


class TestParseCommandIntegration:
    """Test parse_command() integration with wildcard expansion."""

    def test_parse_with_wildcard_expansion(self, default_config, temp_dir_with_files):
        """Test that parse_command expands wildcards by default."""
        result = parse_command("ls *.txt", default_config)
        # Should parse and expand
        assert result[0] == "ls"
        assert "file1.txt" in result
        assert "file2.txt" in result

    def test_parse_with_glob_disabled(self, config_glob_disabled, temp_dir_with_files):
        """Test that parse_command respects glob disabled."""
        result = parse_command("ls *.txt", config_glob_disabled)
        # Should NOT expand
        assert result == ["ls", "*.txt"]

    def test_parse_quoted_wildcard_expansion(self, default_config, temp_dir_with_files):
        """
        Test wildcard expansion with quoted wildcards.

        Note: shlex removes quotes before wildcard expansion, so quoted
        wildcards are still expanded. This is a known limitation - full
        bash-like quote handling would require more complex parsing.
        For this assignment's scope, this behavior is acceptable.
        """
        result = parse_command('echo "*.txt"', default_config)
        # After shlex processes, quotes are removed and wildcard is expanded
        assert result[0] == "echo"
        assert "file1.txt" in result
        assert "file2.txt" in result

    def test_parse_complex_command_with_wildcards(
        self, default_config, temp_dir_with_files
    ):
        """Test parsing complex command with multiple wildcards."""
        result = parse_command("cp *.txt *.py /backup/", default_config)
        assert result[0] == "cp"
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "test1.py" in result
        assert "test2.py" in result
        assert "/backup/" in result

    def test_parse_empty_with_wildcard_config(self, default_config):
        """Test that empty input still returns empty with wildcard config."""
        result = parse_command("", default_config)
        assert result == []

    def test_parse_whitespace_with_wildcard_config(self, default_config):
        """Test that whitespace returns empty with wildcard config."""
        result = parse_command("   ", default_config)
        assert result == []


# ============================================================================
# Test Real-World Scenarios
# ============================================================================


class TestRealWorldScenarios:
    """Test real-world command parsing scenarios."""

    def test_ls_with_flags_and_wildcards(self, default_config, temp_dir_with_files):
        """Test ls command with flags and wildcards."""
        result = parse_command("ls -la *.txt", default_config)
        assert result[0] == "ls"
        assert "-la" in result
        assert "file1.txt" in result
        assert "file2.txt" in result

    def test_grep_with_quoted_pattern(self, default_config):
        """Test grep with quoted pattern."""
        result = parse_command('grep "hello world" file.txt', default_config)
        assert result == ["grep", "hello world", "file.txt"]

    def test_find_command_with_complex_args(self, default_config, temp_dir_with_files):
        """
        Test find command with complex arguments.

        Note: Quoted wildcards are still expanded due to shlex quote removal.
        In real usage, users would pass literal wildcards to find by escaping them.
        """
        result = parse_command('find . -name "*.txt" -type f', default_config)
        assert result[0] == "find"
        assert "." in result
        assert "-name" in result
        # The *.txt will be expanded because shlex removes quotes first
        assert "-type" in result
        assert "f" in result

    def test_printf_with_format_string(self, default_config):
        """Test printf with format string and arguments."""
        result = parse_command('printf "%s %s\\n" arg1 arg2', default_config)
        assert result[0] == "printf"
        # shlex preserves the backslash-n as \\n in the output
        assert result[1] == "%s %s\\n"
        assert result[2] == "arg1"
        assert result[3] == "arg2"

    def test_command_with_absolute_path(self, default_config):
        """Test command with absolute path."""
        result = parse_command("/usr/bin/python3 script.py", default_config)
        assert result == ["/usr/bin/python3", "script.py"]

    def test_command_with_relative_path(self, default_config):
        """Test command with relative path."""
        result = parse_command("./my_script.sh arg1 arg2", default_config)
        assert result == ["./my_script.sh", "arg1", "arg2"]
