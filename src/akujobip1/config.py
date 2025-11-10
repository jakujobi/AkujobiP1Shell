"""
Configuration management module.

This module handles loading and managing configuration from YAML files
with support for environment variables and multiple config locations.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import copy

try:
    import yaml
except ImportError:
    print("Warning: PyYAML not installed. Using defaults only.", file=sys.stderr)
    yaml = None


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration values.

    Returns:
        Default configuration dictionary with all settings.
    """
    return {
        'prompt': {
            'text': 'AkujobiP1> '
        },
        'exit': {
            'message': 'Bye!'
        },
        'execution': {
            'show_exit_codes': 'on_failure',  # Options: never, on_failure, always
            'exit_code_format': '[Exit: {code}]'
        },
        'glob': {
            'enabled': True,
            'show_expansions': False
        },
        'builtins': {
            'cd': {
                'enabled': True,
                'show_pwd_after': False
            },
            'pwd': {
                'enabled': True
            },
            'help': {
                'enabled': True
            }
        },
        'errors': {
            'verbose': False
        },
        'debug': {
            'log_commands': False,
            'log_file': '~/.akujobip1.log',
            'show_fork_pids': False
        }
    }


def merge_config(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two configuration dictionaries.

    Recursively merges override into base, preserving nested structure.
    Override values take precedence over base values.

    Args:
        base: Base configuration (defaults)
        override: Override configuration (user settings)

    Returns:
        Merged configuration (new dict, originals unchanged)

    Example:
        >>> base = {'a': {'b': 1, 'c': 2}}
        >>> override = {'a': {'b': 99}}
        >>> merge_config(base, override)
        {'a': {'b': 99, 'c': 2}}  # 'c' is preserved
    """
    # Create a deep copy to avoid modifying original
    result = copy.deepcopy(base)

    # Recursively merge override into result
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Both are dictionaries - merge recursively
            result[key] = merge_config(result[key], value)
        else:
            # Override value (primitive, list, or dict replacing non-dict)
            result[key] = copy.deepcopy(value)

    return result


def expand_paths(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Expand tilde (~) and environment variables in path strings.

    Recursively walks the config dict and expands any string values
    that look like paths (contain ~ or $).

    Args:
        config: Configuration dictionary

    Returns:
        Configuration with expanded paths (new dict)
    """
    result = {}

    for key, value in config.items():
        if isinstance(value, dict):
            # Recursively expand nested dicts
            result[key] = expand_paths(value)
        elif isinstance(value, str):
            # Expand tilde and environment variables in strings
            if '~' in value or '$' in value:
                expanded = os.path.expanduser(value)
                expanded = os.path.expandvars(expanded)
                result[key] = expanded
            else:
                result[key] = value
        else:
            # Keep other types as-is
            result[key] = value

    return result


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure and values.

    Checks for:
    - Required keys exist
    - Enum values are valid
    - Types are correct

    Prints warnings for invalid values but always returns True
    (we use defaults for invalid values rather than failing).

    Args:
        config: Configuration to validate

    Returns:
        True (always, but prints warnings for issues)
    """
    valid = True

    # Check required keys
    if 'prompt' not in config or 'text' not in config.get('prompt', {}):
        print("Warning: prompt.text not found in config, using default", file=sys.stderr)
        valid = False

    if 'exit' not in config or 'message' not in config.get('exit', {}):
        print("Warning: exit.message not found in config, using default", file=sys.stderr)
        valid = False

    # Validate show_exit_codes enum
    if 'execution' in config:
        show_mode = config['execution'].get('show_exit_codes')
        if show_mode not in ['never', 'on_failure', 'always']:
            print(
                f"Warning: Invalid show_exit_codes value '{show_mode}', "
                "must be 'never', 'on_failure', or 'always'",
                file=sys.stderr
            )
            valid = False

    # Validate boolean fields
    bool_paths = [
        ('glob', 'enabled'),
        ('glob', 'show_expansions'),
        ('errors', 'verbose'),
        ('debug', 'log_commands'),
        ('debug', 'show_fork_pids'),
    ]

    for path in bool_paths:
        value = config
        try:
            for key in path:
                value = value[key]
            if not isinstance(value, bool):
                print(
                    f"Warning: {'.'.join(path)} should be boolean, got {type(value).__name__}",
                    file=sys.stderr
                )
                valid = False
        except (KeyError, TypeError):
            # Key doesn't exist - that's okay, we have defaults
            pass

    return valid


def load_yaml_file(filepath: Path) -> Optional[Dict[str, Any]]:
    """
    Load a YAML file and return its contents.

    Args:
        filepath: Path to YAML file

    Returns:
        Dictionary from YAML file, or None if file doesn't exist or is invalid
    """
    if yaml is None:
        return None

    if not filepath.exists():
        return None

    try:
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
            if data is None:
                # Empty file
                return {}
            if not isinstance(data, dict):
                print(f"Warning: Config file {filepath} is not a valid YAML dictionary", file=sys.stderr)
                return None
            return data
    except yaml.YAMLError as e:
        print(f"Warning: Failed to parse YAML file {filepath}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Warning: Failed to read config file {filepath}: {e}", file=sys.stderr)
        return None


def load_config() -> Dict[str, Any]:
    """
    Load configuration from files with priority order:
    1. Start with built-in defaults
    2. Merge ~/.config/akujobip1/config.yaml (user config)
    3. Merge ./akujobip1.yaml (current directory)
    4. Merge $AKUJOBIP1_CONFIG (environment variable, highest priority)

    Later configs override earlier ones. Missing files are silently skipped.

    Returns:
        Configuration dictionary (always valid, uses defaults for missing/invalid values)
    """
    # Start with default configuration
    config = get_default_config()

    # Priority 1 (lowest): User config directory
    user_config_dir = Path.home() / '.config' / 'akujobip1'
    user_config_file = user_config_dir / 'config.yaml'
    if user_data := load_yaml_file(user_config_file):
        config = merge_config(config, user_data)

    # Priority 2: Current directory
    local_config_file = Path.cwd() / 'akujobip1.yaml'
    if local_data := load_yaml_file(local_config_file):
        config = merge_config(config, local_data)

    # Priority 3 (highest): Environment variable
    if env_config_path := os.environ.get('AKUJOBIP1_CONFIG'):
        env_config_file = Path(env_config_path).expanduser()
        if env_data := load_yaml_file(env_config_file):
            config = merge_config(config, env_data)
        elif env_config_file.exists():
            print(f"Warning: Could not load config from $AKUJOBIP1_CONFIG: {env_config_path}", file=sys.stderr)

    # Expand paths (~ and environment variables)
    config = expand_paths(config)

    # Validate final configuration (prints warnings but doesn't fail)
    validate_config(config)

    return config
