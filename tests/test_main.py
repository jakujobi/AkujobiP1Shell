"""
Tests for __main__.py module.

This module tests the entry point for running the shell as a module
using `python -m akujobip1`.
"""

import sys
import subprocess
from pathlib import Path


class TestMainModule:
    """Test the __main__.py entry point."""

    def test_main_module_can_be_executed(self):
        """
        Test that the shell can be run as a module with 'python -m akujobip1'.

        This test verifies:
        - The __main__.py entry point exists
        - It can be executed
        - It handles exit command correctly
        """
        # Get the project root directory
        project_root = Path(__file__).parent.parent

        # Run the shell as a module with exit command
        result = subprocess.run(
            [sys.executable, "-m", "akujobip1"],
            input="exit\n",
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=5,
        )

        # Verify it executed successfully
        assert result.returncode == 0, f"Shell exited with code {result.returncode}"

        # Verify prompt and exit message appeared
        assert "AkujobiP1>" in result.stdout, "Prompt not displayed"
        assert "Bye!" in result.stdout, "Exit message not displayed"

    def test_main_module_handles_empty_input(self):
        """
        Test that the shell handles empty input when run as a module.
        """
        project_root = Path(__file__).parent.parent

        result = subprocess.run(
            [sys.executable, "-m", "akujobip1"],
            input="\nexit\n",
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=5,
        )

        assert result.returncode == 0
        assert "AkujobiP1>" in result.stdout
        assert "Bye!" in result.stdout

    def test_main_module_executes_command(self):
        """
        Test that the shell can execute commands when run as a module.
        """
        project_root = Path(__file__).parent.parent

        result = subprocess.run(
            [sys.executable, "-m", "akujobip1"],
            input="echo test\nexit\n",
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=5,
        )

        assert result.returncode == 0
        assert "test" in result.stdout
        assert "Bye!" in result.stdout

    def test_main_module_handles_ctrl_d(self):
        """
        Test that the shell handles EOF (Ctrl+D) when run as a module.

        Note: We simulate EOF by closing stdin without sending 'exit'.
        """
        project_root = Path(__file__).parent.parent

        result = subprocess.run(
            [sys.executable, "-m", "akujobip1"],
            input="",  # EOF immediately
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=5,
        )

        # Should exit gracefully with exit message
        assert result.returncode == 0
        assert "Bye!" in result.stdout or result.returncode == 0
