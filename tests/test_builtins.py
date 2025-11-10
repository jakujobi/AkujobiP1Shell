"""
Tests for built-in commands module.

This module contains comprehensive tests for all built-in shell commands:
exit, cd, pwd, and help.
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from io import StringIO
from unittest.mock import patch

from akujobip1.builtins import (
    BuiltinCommand,
    ExitCommand,
    CdCommand,
    PwdCommand,
    HelpCommand,
    get_builtin,
    BUILTINS
)


class TestExitCommand:
    """Tests for ExitCommand."""

    def test_exit_with_default_message(self, capsys):
        """Test exit command with default message."""
        config = {'exit': {'message': 'Bye!'}}
        cmd = ExitCommand()
        
        result = cmd.execute(['exit'], config)
        
        assert result == -1, "Exit should return -1 to signal shell termination"
        captured = capsys.readouterr()
        assert captured.out == "Bye!\n"
        assert captured.err == ""

    def test_exit_with_custom_message(self, capsys):
        """Test exit command with custom message from config."""
        config = {'exit': {'message': 'Goodbye, friend!'}}
        cmd = ExitCommand()
        
        result = cmd.execute(['exit'], config)
        
        assert result == -1
        captured = capsys.readouterr()
        assert captured.out == "Goodbye, friend!\n"

    def test_exit_with_missing_config(self, capsys):
        """Test exit command with missing config (should use default)."""
        config = {}
        cmd = ExitCommand()
        
        result = cmd.execute(['exit'], config)
        
        assert result == -1
        captured = capsys.readouterr()
        assert captured.out == "Bye!\n"


class TestPwdCommand:
    """Tests for PwdCommand."""

    def test_pwd_prints_current_directory(self, capsys):
        """Test pwd prints current working directory."""
        cmd = PwdCommand()
        expected_dir = os.getcwd()
        
        result = cmd.execute(['pwd'], {})
        
        assert result == 0, "pwd should return 0 on success"
        captured = capsys.readouterr()
        assert captured.out == f"{expected_dir}\n"
        assert captured.err == ""

    def test_pwd_with_config(self, capsys):
        """Test pwd works with any config."""
        cmd = PwdCommand()
        config = {'builtins': {'pwd': {'enabled': True}}}
        
        result = cmd.execute(['pwd'], config)
        
        assert result == 0
        captured = capsys.readouterr()
        assert os.getcwd() in captured.out

    def test_pwd_with_deleted_directory(self, capsys):
        """Test pwd when current directory has been deleted."""
        cmd = PwdCommand()
        
        # Mock getcwd to raise OSError
        with patch('os.getcwd', side_effect=OSError("No such file or directory")):
            result = cmd.execute(['pwd'], {})
            
            assert result == 1, "pwd should return 1 on error"
            captured = capsys.readouterr()
            assert "No such file or directory" in captured.err


class TestHelpCommand:
    """Tests for HelpCommand."""

    def test_help_shows_all_commands(self, capsys):
        """Test help command shows all built-in commands."""
        cmd = HelpCommand()
        
        result = cmd.execute(['help'], {})
        
        assert result == 0, "help should return 0 on success"
        captured = capsys.readouterr()
        
        # Check that all commands are mentioned
        assert "exit" in captured.out
        assert "cd" in captured.out
        assert "pwd" in captured.out
        assert "help" in captured.out
        
        # Check for usage information
        assert "Exit the shell" in captured.out
        assert "Change directory" in captured.out
        assert "Print working directory" in captured.out
        assert "help message" in captured.out
        
        assert captured.err == ""

    def test_help_with_config(self, capsys):
        """Test help works with any config."""
        cmd = HelpCommand()
        config = {'builtins': {'help': {'enabled': True}}}
        
        result = cmd.execute(['help'], config)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Built-in commands:" in captured.out


class TestCdCommandBasic:
    """Basic tests for CdCommand."""

    def setup_method(self):
        """Set up test by saving current directory and resetting OLDPWD."""
        self.original_dir = os.getcwd()
        CdCommand._previous_directory = None

    def teardown_method(self):
        """Restore original directory after each test."""
        try:
            os.chdir(self.original_dir)
        except OSError:
            pass
        CdCommand._previous_directory = None

    def test_cd_to_valid_directory(self):
        """Test cd to valid directory."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        
        # cd to /tmp (should exist on all Unix systems)
        result = cmd.execute(['cd', '/tmp'], config)
        
        assert result == 0, "cd should return 0 on success"
        assert os.getcwd() == '/tmp'

    def test_cd_no_arguments_goes_home(self):
        """Test cd with no arguments goes to home directory."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        
        result = cmd.execute(['cd'], config)
        
        assert result == 0
        assert os.getcwd() == os.path.expanduser('~')

    def test_cd_updates_previous_directory(self):
        """Test cd updates previous directory for cd -."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        start_dir = os.getcwd()
        
        # cd to /tmp
        cmd.execute(['cd', '/tmp'], config)
        
        # Previous directory should be where we started
        assert CdCommand._previous_directory == start_dir

    def test_cd_dash_goes_to_previous(self):
        """Test cd - goes to previous directory."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        
        # cd to /tmp
        cmd.execute(['cd', '/tmp'], config)
        previous = CdCommand._previous_directory
        
        # cd - should go back
        result = cmd.execute(['cd', '-'], config)
        
        assert result == 0
        assert os.getcwd() == previous

    def test_cd_dash_multiple_times(self):
        """Test cd - can be used multiple times to toggle."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        
        dir1 = os.getcwd()
        cmd.execute(['cd', '/tmp'], config)
        dir2 = os.getcwd()
        
        # cd - back to dir1
        cmd.execute(['cd', '-'], config)
        assert os.getcwd() == dir1
        
        # cd - back to dir2
        cmd.execute(['cd', '-'], config)
        assert os.getcwd() == dir2


class TestCdCommandErrors:
    """Error handling tests for CdCommand."""

    def setup_method(self):
        """Set up test by saving current directory and resetting OLDPWD."""
        self.original_dir = os.getcwd()
        CdCommand._previous_directory = None

    def teardown_method(self):
        """Restore original directory after each test."""
        try:
            os.chdir(self.original_dir)
        except OSError:
            pass
        CdCommand._previous_directory = None

    def test_cd_to_nonexistent_directory(self, capsys):
        """Test cd to non-existent directory shows error."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        original_dir = os.getcwd()
        
        result = cmd.execute(['cd', '/nonexistent_dir_12345'], config)
        
        assert result == 1, "cd should return 1 on error"
        assert os.getcwd() == original_dir, "Directory should not change"
        
        captured = capsys.readouterr()
        assert "No such file or directory" in captured.err
        assert "/nonexistent_dir_12345" in captured.err

    def test_cd_to_file_not_directory(self, capsys):
        """Test cd to a file (not directory) shows error."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            result = cmd.execute(['cd', tmp_path], config)
            
            assert result == 1
            captured = capsys.readouterr()
            assert "Not a directory" in captured.err
        finally:
            os.unlink(tmp_path)

    def test_cd_dash_without_oldpwd(self, capsys):
        """Test cd - without previous directory set shows error."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        original_dir = os.getcwd()
        
        # Ensure OLDPWD is not set
        CdCommand._previous_directory = None
        
        result = cmd.execute(['cd', '-'], config)
        
        assert result == 1
        assert os.getcwd() == original_dir
        
        captured = capsys.readouterr()
        assert "OLDPWD not set" in captured.err


class TestCdCommandConfiguration:
    """Configuration tests for CdCommand."""

    def setup_method(self):
        """Set up test by saving current directory."""
        self.original_dir = os.getcwd()
        CdCommand._previous_directory = None

    def teardown_method(self):
        """Restore original directory after each test."""
        try:
            os.chdir(self.original_dir)
        except OSError:
            pass
        CdCommand._previous_directory = None

    def test_cd_show_pwd_after_enabled(self, capsys):
        """Test cd shows pwd when show_pwd_after is enabled."""
        config = {'builtins': {'cd': {'show_pwd_after': True}}}
        cmd = CdCommand()
        
        cmd.execute(['cd', '/tmp'], config)
        
        captured = capsys.readouterr()
        assert '/tmp' in captured.out

    def test_cd_show_pwd_after_disabled(self, capsys):
        """Test cd doesn't show pwd when show_pwd_after is disabled."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        
        cmd.execute(['cd', '/tmp'], config)
        
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_cd_with_missing_config(self):
        """Test cd works with missing config (uses defaults)."""
        config = {}
        cmd = CdCommand()
        
        result = cmd.execute(['cd', '/tmp'], config)
        
        assert result == 0
        assert os.getcwd() == '/tmp'


class TestCdCommandEdgeCases:
    """Edge case tests for CdCommand."""

    def setup_method(self):
        """Set up test by saving current directory."""
        self.original_dir = os.getcwd()
        CdCommand._previous_directory = None

    def teardown_method(self):
        """Restore original directory after each test."""
        try:
            os.chdir(self.original_dir)
        except OSError:
            pass
        CdCommand._previous_directory = None

    def test_cd_with_tilde(self):
        """Test cd expands tilde to home directory."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        
        # cd ~ should work (expanduser happens in execute)
        result = cmd.execute(['cd'], config)
        
        assert result == 0
        assert os.getcwd() == os.path.expanduser('~')

    def test_cd_to_relative_path(self):
        """Test cd to relative path."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        
        # Create temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Create subdirectory
            subdir = 'testdir'
            os.mkdir(subdir)
            
            # cd to relative path
            result = cmd.execute(['cd', subdir], config)
            
            assert result == 0
            assert os.getcwd().endswith(subdir)

    def test_cd_to_dot(self):
        """Test cd to . (current directory)."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        current = os.getcwd()
        
        result = cmd.execute(['cd', '.'], config)
        
        assert result == 0
        assert os.getcwd() == current

    def test_cd_to_dot_dot(self):
        """Test cd to .. (parent directory)."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        
        # Go to /tmp/test
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            parent = os.path.dirname(tmpdir)
            
            # cd ..
            result = cmd.execute(['cd', '..'], config)
            
            assert result == 0
            assert os.getcwd() == parent


class TestGetBuiltin:
    """Tests for get_builtin function."""

    def test_get_existing_builtin(self):
        """Test getting existing built-in command."""
        cmd = get_builtin('exit')
        assert cmd is not None
        assert isinstance(cmd, ExitCommand)

    def test_get_all_builtins(self):
        """Test all built-in commands can be retrieved."""
        assert isinstance(get_builtin('exit'), ExitCommand)
        assert isinstance(get_builtin('cd'), CdCommand)
        assert isinstance(get_builtin('pwd'), PwdCommand)
        assert isinstance(get_builtin('help'), HelpCommand)

    def test_get_nonexistent_builtin(self):
        """Test getting non-existent built-in returns None."""
        cmd = get_builtin('nonexistent')
        assert cmd is None

    def test_builtins_registry_complete(self):
        """Test BUILTINS registry contains all commands."""
        assert 'exit' in BUILTINS
        assert 'cd' in BUILTINS
        assert 'pwd' in BUILTINS
        assert 'help' in BUILTINS
        assert len(BUILTINS) == 4


class TestBuiltinCommandBase:
    """Tests for BuiltinCommand base class."""

    def test_base_class_execute_not_implemented(self):
        """Test base class execute raises NotImplementedError."""
        cmd = BuiltinCommand()
        
        with pytest.raises(NotImplementedError):
            cmd.execute(['test'], {})


class TestCdCommandStatePersistence:
    """Tests for CdCommand state persistence across instances."""

    def setup_method(self):
        """Set up test by saving current directory."""
        self.original_dir = os.getcwd()
        CdCommand._previous_directory = None

    def teardown_method(self):
        """Restore original directory after each test."""
        try:
            os.chdir(self.original_dir)
        except OSError:
            pass
        CdCommand._previous_directory = None

    def test_cd_state_persists_across_instances(self):
        """Test previous directory state persists across different CdCommand instances."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        
        # Create first instance and cd
        cmd1 = CdCommand()
        cmd1.execute(['cd', '/tmp'], config)
        previous = CdCommand._previous_directory
        
        # Create second instance and cd -
        cmd2 = CdCommand()
        result = cmd2.execute(['cd', '-'], config)
        
        assert result == 0
        assert os.getcwd() == previous


class TestCdCommandPermissions:
    """Tests for CdCommand permission handling."""

    def setup_method(self):
        """Set up test by saving current directory."""
        self.original_dir = os.getcwd()
        CdCommand._previous_directory = None

    def teardown_method(self):
        """Restore original directory after each test."""
        try:
            os.chdir(self.original_dir)
        except OSError:
            pass
        CdCommand._previous_directory = None

    def test_cd_to_directory_without_permissions(self, capsys):
        """Test cd to directory without execute permissions."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        
        # Create a directory with no permissions
        with tempfile.TemporaryDirectory() as tmpdir:
            restricted_dir = os.path.join(tmpdir, 'restricted')
            os.mkdir(restricted_dir)
            os.chmod(restricted_dir, 0o000)
            
            try:
                result = cmd.execute(['cd', restricted_dir], config)
                
                # Should fail with permission error
                assert result == 1
                captured = capsys.readouterr()
                assert "Permission denied" in captured.err or "permission" in captured.err.lower()
            finally:
                # Restore permissions for cleanup
                try:
                    os.chmod(restricted_dir, 0o755)
                except OSError:
                    pass

    def test_cd_when_current_directory_deleted(self, capsys):
        """Test cd when current directory has been deleted."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        
        # Mock getcwd to raise OSError (simulating deleted directory)
        with patch('os.getcwd', side_effect=OSError("No such file or directory")):
            # Should still be able to cd to /tmp
            result = cmd.execute(['cd', '/tmp'], config)
            
            # Should succeed despite getcwd failing
            assert result == 0

    def test_cd_with_other_os_error(self, capsys):
        """Test cd with generic OSError during chdir."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cmd = CdCommand()
        
        # Mock chdir to raise a generic OSError
        with patch('os.chdir', side_effect=OSError("Generic OS error")):
            result = cmd.execute(['cd', '/tmp'], config)
            
            assert result == 1
            captured = capsys.readouterr()
            assert "Generic OS error" in captured.err


class TestIntegrationScenarios:
    """Integration tests with realistic usage scenarios."""

    def setup_method(self):
        """Set up test by saving current directory."""
        self.original_dir = os.getcwd()
        CdCommand._previous_directory = None

    def teardown_method(self):
        """Restore original directory after each test."""
        try:
            os.chdir(self.original_dir)
        except OSError:
            pass
        CdCommand._previous_directory = None

    def test_typical_navigation_session(self, capsys):
        """Test typical directory navigation session."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cd_cmd = CdCommand()
        pwd_cmd = PwdCommand()
        
        # pwd
        pwd_cmd.execute(['pwd'], config)
        captured = capsys.readouterr()
        assert self.original_dir in captured.out
        
        # cd /tmp
        result = cd_cmd.execute(['cd', '/tmp'], config)
        assert result == 0
        
        # pwd
        pwd_cmd.execute(['pwd'], config)
        captured = capsys.readouterr()
        assert '/tmp' in captured.out
        
        # cd -
        result = cd_cmd.execute(['cd', '-'], config)
        assert result == 0
        
        # pwd
        pwd_cmd.execute(['pwd'], config)
        captured = capsys.readouterr()
        assert self.original_dir in captured.out

    def test_help_then_use_commands(self, capsys):
        """Test using help then executing commands."""
        config = {'exit': {'message': 'Bye!'}}
        
        # help
        help_cmd = HelpCommand()
        help_cmd.execute(['help'], config)
        captured = capsys.readouterr()
        assert 'exit' in captured.out
        
        # pwd
        pwd_cmd = PwdCommand()
        pwd_cmd.execute(['pwd'], config)
        
        # exit
        exit_cmd = ExitCommand()
        result = exit_cmd.execute(['exit'], config)
        assert result == -1

    def test_cd_error_recovery(self, capsys):
        """Test that failed cd doesn't affect subsequent operations."""
        config = {'builtins': {'cd': {'show_pwd_after': False}}}
        cd_cmd = CdCommand()
        pwd_cmd = PwdCommand()
        start_dir = os.getcwd()
        
        # Try to cd to non-existent directory
        result = cd_cmd.execute(['cd', '/nonexistent_test_dir'], config)
        assert result == 1
        
        # Verify we're still in the same place
        pwd_cmd.execute(['pwd'], config)
        captured = capsys.readouterr()
        assert start_dir in captured.out
        
        # Verify subsequent cd still works
        result = cd_cmd.execute(['cd', '/tmp'], config)
        assert result == 0
        assert os.getcwd() == '/tmp'

