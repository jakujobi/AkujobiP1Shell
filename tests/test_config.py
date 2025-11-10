"""
Unit tests for configuration management module.

Tests cover:
- Default configuration
- Deep merging
- Path expansion
- Configuration validation
- YAML file loading
- Priority order loading
"""

import pytest
import os
import sys
from pathlib import Path
import tempfile
import shutil

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from akujobip1.config import (
    get_default_config,
    merge_config,
    expand_paths,
    validate_config,
    load_yaml_file,
    load_config
)


class TestDefaultConfig:
    """Test default configuration values."""

    def test_get_default_config_structure(self):
        """Test that default config has all required keys."""
        config = get_default_config()

        # Top-level keys
        assert 'prompt' in config
        assert 'exit' in config
        assert 'execution' in config
        assert 'glob' in config
        assert 'builtins' in config
        assert 'errors' in config
        assert 'debug' in config

    def test_default_prompt(self):
        """Test default prompt configuration."""
        config = get_default_config()
        assert config['prompt']['text'] == 'AkujobiP1> '

    def test_default_exit_message(self):
        """Test default exit message."""
        config = get_default_config()
        assert config['exit']['message'] == 'Bye!'

    def test_default_execution_settings(self):
        """Test default execution settings."""
        config = get_default_config()
        assert config['execution']['show_exit_codes'] == 'on_failure'
        assert config['execution']['exit_code_format'] == '[Exit: {code}]'

    def test_default_glob_settings(self):
        """Test default glob settings."""
        config = get_default_config()
        assert config['glob']['enabled'] is True
        assert config['glob']['show_expansions'] is False

    def test_default_builtins_settings(self):
        """Test default built-in command settings."""
        config = get_default_config()
        assert config['builtins']['cd']['enabled'] is True
        assert config['builtins']['cd']['show_pwd_after'] is False
        assert config['builtins']['pwd']['enabled'] is True
        assert config['builtins']['help']['enabled'] is True

    def test_default_returns_new_dict(self):
        """Test that get_default_config returns a new dict each time."""
        config1 = get_default_config()
        config2 = get_default_config()

        # Should be equal but not the same object
        assert config1 == config2
        assert config1 is not config2

        # Modifying one shouldn't affect the other
        config1['prompt']['text'] = 'Modified> '
        assert config2['prompt']['text'] == 'AkujobiP1> '


class TestMergeConfig:
    """Test configuration merging."""

    def test_merge_simple_override(self):
        """Test simple value override."""
        base = {'a': 1, 'b': 2}
        override = {'b': 99}
        result = merge_config(base, override)

        assert result == {'a': 1, 'b': 99}

    def test_merge_nested_dict_partial(self):
        """Test partial override of nested dict."""
        base = {
            'execution': {
                'show_exit_codes': 'on_failure',
                'exit_code_format': '[Exit: {code}]'
            }
        }
        override = {
            'execution': {
                'show_exit_codes': 'always'
            }
        }
        result = merge_config(base, override)

        # Should override show_exit_codes but preserve exit_code_format
        assert result['execution']['show_exit_codes'] == 'always'
        assert result['execution']['exit_code_format'] == '[Exit: {code}]'

    def test_merge_deep_nesting(self):
        """Test deep nested structure merging."""
        base = {
            'a': {
                'b': {
                    'c': 1,
                    'd': 2
                },
                'e': 3
            }
        }
        override = {
            'a': {
                'b': {
                    'c': 99
                }
            }
        }
        result = merge_config(base, override)

        assert result['a']['b']['c'] == 99
        assert result['a']['b']['d'] == 2  # Preserved
        assert result['a']['e'] == 3  # Preserved

    def test_merge_adds_new_keys(self):
        """Test that merge adds new keys from override."""
        base = {'a': 1}
        override = {'b': 2}
        result = merge_config(base, override)

        assert result == {'a': 1, 'b': 2}

    def test_merge_doesnt_modify_originals(self):
        """Test that merge doesn't modify original dicts."""
        base = {'a': {'b': 1}}
        override = {'a': {'c': 2}}

        result = merge_config(base, override)

        # Modify result
        result['a']['b'] = 99

        # Originals should be unchanged
        assert base['a']['b'] == 1
        assert 'c' not in base['a']

    def test_merge_with_list(self):
        """Test that merge replaces lists (doesn't merge them)."""
        base = {'items': [1, 2, 3]}
        override = {'items': [4, 5]}
        result = merge_config(base, override)

        # List should be replaced, not merged
        assert result['items'] == [4, 5]

    def test_merge_dict_replacing_primitive(self):
        """Test dict can replace primitive value."""
        base = {'value': 42}
        override = {'value': {'nested': 'dict'}}
        result = merge_config(base, override)

        assert result['value'] == {'nested': 'dict'}

    def test_merge_primitive_replacing_dict(self):
        """Test primitive can replace dict value."""
        base = {'value': {'nested': 'dict'}}
        override = {'value': 42}
        result = merge_config(base, override)

        assert result['value'] == 42


class TestExpandPaths:
    """Test path expansion."""

    def test_expand_tilde(self):
        """Test tilde expansion."""
        config = {'debug': {'log_file': '~/.akujobip1.log'}}
        result = expand_paths(config)

        assert '~' not in result['debug']['log_file']
        assert result['debug']['log_file'].startswith(str(Path.home()))

    def test_expand_env_var(self):
        """Test environment variable expansion."""
        os.environ['TEST_VAR'] = '/test/path'
        config = {'path': '$TEST_VAR/file.txt'}
        result = expand_paths(config)

        assert result['path'] == '/test/path/file.txt'

    def test_expand_nested_paths(self):
        """Test expansion in nested structures."""
        config = {
            'level1': {
                'level2': {
                    'path': '~/config.yaml'
                }
            }
        }
        result = expand_paths(config)

        assert '~' not in result['level1']['level2']['path']

    def test_expand_doesnt_modify_non_paths(self):
        """Test that non-path strings are unchanged."""
        config = {
            'prompt': {'text': 'AkujobiP1> '},
            'exit': {'message': 'Bye!'}
        }
        result = expand_paths(config)

        assert result == config

    def test_expand_preserves_types(self):
        """Test that non-string types are preserved."""
        config = {
            'bool': True,
            'int': 42,
            'list': [1, 2, 3],
            'none': None
        }
        result = expand_paths(config)

        assert result == config


class TestValidateConfig:
    """Test configuration validation."""

    def test_validate_good_config(self):
        """Test validation of good config."""
        config = get_default_config()
        assert validate_config(config) is True

    def test_validate_missing_prompt(self, capsys):
        """Test validation catches missing prompt."""
        config = {'exit': {'message': 'Bye!'}}
        validate_config(config)

        captured = capsys.readouterr()
        assert 'prompt.text' in captured.err

    def test_validate_missing_exit_message(self, capsys):
        """Test validation catches missing exit message."""
        config = {'prompt': {'text': 'Test> '}}
        validate_config(config)

        captured = capsys.readouterr()
        assert 'exit.message' in captured.err

    def test_validate_invalid_show_exit_codes(self, capsys):
        """Test validation catches invalid show_exit_codes."""
        config = get_default_config()
        config['execution']['show_exit_codes'] = 'invalid_value'

        validate_config(config)
        captured = capsys.readouterr()
        assert 'show_exit_codes' in captured.err

    def test_validate_valid_show_exit_codes(self):
        """Test validation accepts valid show_exit_codes values."""
        for value in ['never', 'on_failure', 'always']:
            config = get_default_config()
            config['execution']['show_exit_codes'] = value
            assert validate_config(config) is True

    def test_validate_non_boolean_fields(self, capsys):
        """Test validation catches non-boolean values in boolean fields."""
        config = get_default_config()
        config['glob']['enabled'] = 'true'  # String instead of boolean

        validate_config(config)
        captured = capsys.readouterr()
        assert 'glob.enabled' in captured.err
        assert 'boolean' in captured.err


class TestLoadYamlFile:
    """Test YAML file loading."""

    def test_load_valid_yaml(self, tmp_path):
        """Test loading valid YAML file."""
        config_file = tmp_path / 'config.yaml'
        config_file.write_text('prompt:\n  text: "Custom> "\n')

        result = load_yaml_file(config_file)
        assert result is not None
        assert result['prompt']['text'] == 'Custom> '

    def test_load_nonexistent_file(self, tmp_path):
        """Test loading nonexistent file returns None."""
        config_file = tmp_path / 'nonexistent.yaml'
        result = load_yaml_file(config_file)
        assert result is None

    def test_load_empty_yaml(self, tmp_path):
        """Test loading empty YAML file."""
        config_file = tmp_path / 'empty.yaml'
        config_file.write_text('')

        result = load_yaml_file(config_file)
        assert result == {}

    def test_load_invalid_yaml(self, tmp_path, capsys):
        """Test loading invalid YAML file."""
        config_file = tmp_path / 'invalid.yaml'
        config_file.write_text('invalid: yaml: content:\n  - broken')

        result = load_yaml_file(config_file)
        assert result is None

        captured = capsys.readouterr()
        assert 'Failed to parse' in captured.err

    def test_load_non_dict_yaml(self, tmp_path, capsys):
        """Test loading YAML that's not a dictionary."""
        config_file = tmp_path / 'list.yaml'
        config_file.write_text('- item1\n- item2\n')

        result = load_yaml_file(config_file)
        assert result is None

        captured = capsys.readouterr()
        assert 'not a valid YAML dictionary' in captured.err


class TestLoadConfig:
    """Test full configuration loading with priority."""

    def test_load_defaults_only(self, tmp_path, monkeypatch):
        """Test loading with no config files (defaults only)."""
        # Change to temp directory with no config files
        monkeypatch.chdir(tmp_path)
        # Clear environment variable
        monkeypatch.delenv('AKUJOBIP1_CONFIG', raising=False)

        config = load_config()

        # Should get default values
        assert config['prompt']['text'] == 'AkujobiP1> '
        assert config['exit']['message'] == 'Bye!'

    def test_load_local_config(self, tmp_path, monkeypatch):
        """Test loading local config file."""
        # Create local config
        local_config = tmp_path / 'akujobip1.yaml'
        local_config.write_text('prompt:\n  text: "Local> "\n')

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv('AKUJOBIP1_CONFIG', raising=False)

        config = load_config()

        assert config['prompt']['text'] == 'Local> '
        # Other defaults should be preserved
        assert config['exit']['message'] == 'Bye!'

    def test_load_env_config_priority(self, tmp_path, monkeypatch):
        """Test environment variable config has highest priority."""
        # Create local config
        local_config = tmp_path / 'akujobip1.yaml'
        local_config.write_text('prompt:\n  text: "Local> "\n')

        # Create env config
        env_config = tmp_path / 'env.yaml'
        env_config.write_text('prompt:\n  text: "Env> "\n')

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv('AKUJOBIP1_CONFIG', str(env_config))

        config = load_config()

        # Env config should override local
        assert config['prompt']['text'] == 'Env> '

    def test_load_partial_override(self, tmp_path, monkeypatch):
        """Test partial config override preserves defaults."""
        # Only override one nested value
        local_config = tmp_path / 'akujobip1.yaml'
        local_config.write_text('execution:\n  show_exit_codes: "always"\n')

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv('AKUJOBIP1_CONFIG', raising=False)

        config = load_config()

        # Overridden value
        assert config['execution']['show_exit_codes'] == 'always'
        # Other execution settings should be preserved
        assert config['execution']['exit_code_format'] == '[Exit: {code}]'
        # Unrelated settings should be defaults
        assert config['prompt']['text'] == 'AkujobiP1> '

    def test_load_expands_paths(self, tmp_path, monkeypatch):
        """Test that load_config expands paths."""
        local_config = tmp_path / 'akujobip1.yaml'
        local_config.write_text('debug:\n  log_file: "~/custom.log"\n')

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv('AKUJOBIP1_CONFIG', raising=False)

        config = load_config()

        # Tilde should be expanded
        assert '~' not in config['debug']['log_file']
        assert config['debug']['log_file'].startswith(str(Path.home()))

    def test_load_invalid_env_config(self, tmp_path, monkeypatch, capsys):
        """Test loading with invalid env config path."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv('AKUJOBIP1_CONFIG', '/nonexistent/config.yaml')

        config = load_config()

        # Should still get valid config (defaults)
        assert config is not None
        assert config['prompt']['text'] == 'AkujobiP1> '

    def test_load_user_config_dir(self, tmp_path, monkeypatch):
        """Test loading from user config directory."""
        # Mock home directory
        fake_home = tmp_path / 'home'
        fake_home.mkdir()

        # Create user config
        user_config_dir = fake_home / '.config' / 'akujobip1'
        user_config_dir.mkdir(parents=True)
        user_config = user_config_dir / 'config.yaml'
        user_config.write_text('prompt:\n  text: "User> "\n')

        # Change to different directory
        work_dir = tmp_path / 'work'
        work_dir.mkdir()

        monkeypatch.chdir(work_dir)
        monkeypatch.setenv('HOME', str(fake_home))
        monkeypatch.delenv('AKUJOBIP1_CONFIG', raising=False)

        config = load_config()

        assert config['prompt']['text'] == 'User> '

    def test_load_multiple_configs_merge(self, tmp_path, monkeypatch):
        """Test that multiple configs merge correctly."""
        # Mock home directory
        fake_home = tmp_path / 'home'
        fake_home.mkdir()

        # User config: sets prompt
        user_config_dir = fake_home / '.config' / 'akujobip1'
        user_config_dir.mkdir(parents=True)
        user_config = user_config_dir / 'config.yaml'
        user_config.write_text('prompt:\n  text: "User> "\n')

        # Local config: sets exit message
        work_dir = tmp_path / 'work'
        work_dir.mkdir()
        local_config = work_dir / 'akujobip1.yaml'
        local_config.write_text('exit:\n  message: "Goodbye!"\n')

        monkeypatch.chdir(work_dir)
        monkeypatch.setenv('HOME', str(fake_home))
        monkeypatch.delenv('AKUJOBIP1_CONFIG', raising=False)

        config = load_config()

        # Both overrides should be present
        assert config['prompt']['text'] == 'User> '
        assert config['exit']['message'] == 'Goodbye!'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

