# Bug Fixes - Version 0.8.1

**Date:** 2025-11-10  
**Status:** FIXED  
**Version:** 0.8.1

---

## Summary

Fixed three critical configuration robustness issues that could cause crashes or test failures in edge cases. All fixes add defensive programming to handle malformed configuration values gracefully.

---

## Issues Fixed

### Issue #1: Tests fail on systems without bash

**Problem:**
- Signal termination tests use `bash -c "kill $$"` to test signal handling
- On slim Docker images (e.g., `python:3.12-slim`), bash is not installed
- Tests fail with exit code 127 (command not found)
- Tests marked as failed even though the executor works correctly

**Solution:**
```python
@pytest.mark.skipif(shutil.which("bash") is None, reason="bash required for signal tests")
class TestExecuteExternalCommandSignals:
    ...
```

**Impact:**
- Tests skip gracefully on systems without bash
- No false failures on minimal/slim environments
- Test suite remains reliable across all environments

**Files Changed:**
- `tests/test_executor.py` - Added `import shutil` and skipif decorator

---

### Issue #2: Non-string exit code format crashes shell

**Problem:**
- If user sets `execution.exit_code_format: null` in YAML config
- The value becomes `None` in Python
- Code calls `format_str.format(code=exit_code)`
- Raises `AttributeError: 'NoneType' object has no attribute 'format'`
- Exception bubbles to `run_shell`, prints error after every external command
- Shell becomes noisy and unusable

**Example Bad Config:**
```yaml
execution:
  exit_code_format: null  # or missing, or int, etc.
```

**Solution:**
```python
# Guard against non-string format values (None, int, etc.)
if not isinstance(format_str, str):
    format_str = "[Exit: {code}]"

# Handle format errors gracefully
try:
    message = format_str.format(code=exit_code)
    print(message)
except (KeyError, ValueError, AttributeError):
    # Format string is invalid - use default
    print(f"[Exit: {exit_code}]")
```

**Impact:**
- Handles None, int, list, or any non-string value
- Falls back to default format automatically
- No crashes, no error messages
- Shell remains fully functional

**Files Changed:**
- `src/akujobip1/executor.py` - Added type guard and AttributeError to exception list

---

### Issue #3: Non-string prompt crashes shell

**Problem:**
- If user sets `prompt.text: null` in YAML config
- The value becomes `None` in Python
- Code calls `input(prompt)` where prompt is None
- Raises `TypeError: write() argument must be str, not None`
- Exception caught by outer loop, shell keeps printing error
- Shell never shows prompt again, effectively broken

**Example Bad Config:**
```yaml
prompt:
  text: null  # or 123, or [], etc.
exit:
  message: null  # same issue
```

**Solution:**
```python
prompt = prompt_config.get("text", "AkujobiP1> ")
# Guard against non-string prompt values (None, int, etc.)
if not isinstance(prompt, str):
    prompt = "AkujobiP1> "

exit_message = exit_config.get("message", "Bye!")
# Guard against non-string exit message values
if not isinstance(exit_message, str):
    exit_message = "Bye!"
```

**Impact:**
- Handles None, int, list, or any non-string value
- Falls back to correct defaults automatically
- No crashes, no error messages
- Shell works perfectly with malformed config

**Files Changed:**
- `src/akujobip1/shell.py` - Added type guards for prompt and exit_message

---

## Testing

All fixes tested and verified:

### Unit Tests
```bash
$ pytest -q
229 passed in 0.81s
```

### Bash Integration Tests
```bash
$ bash tests/run_tests.sh
PASSED: exit
PASSED: empty_then_exit
PASSED: unknown_command
PASSED: quoted_args_smoke
```

### Code Quality
```bash
$ ruff check src/ tests/
All checks passed!

$ black --check src/ tests/
All done! ✨ 🍰 ✨
13 files would be left unchanged.
```

---

## Root Cause Analysis

**Why did these issues exist?**

1. **Optimistic assumptions about config values:**
   - Code assumed YAML parsing always returns strings
   - But YAML allows `null`, numbers, lists, etc.
   - No type validation after parsing

2. **Missing defensive checks:**
   - No `isinstance()` checks before using values
   - Relied on exceptions being caught by outer handlers
   - But exceptions made shell unusable

3. **Test environment assumptions:**
   - Assumed bash is always available
   - Not all Python environments include bash
   - Slim images prioritize minimal size

**Why weren't these caught earlier?**

- Config validation focused on structure, not types
- Default config uses proper string values
- Tests didn't cover malformed config scenarios
- Development environment has bash installed

---

## Prevention Strategy

**How to prevent similar issues:**

1. **Type validation:**
   - Always use `isinstance()` before string operations
   - Validate types after YAML parsing
   - Provide sensible defaults

2. **Defensive programming:**
   - Don't assume user input is well-formed
   - Always have fallbacks
   - Test with malformed inputs

3. **Environment flexibility:**
   - Use `shutil.which()` to check for external tools
   - Skip tests that need unavailable tools
   - Don't assume tools are installed

---

## Impact Summary

**Before fixes:**
- ❌ Tests fail on slim Docker images
- ❌ Shell crashes with malformed config
- ❌ Prompt broken with null values
- ❌ Exit code display broken with null format

**After fixes:**
- ✅ Tests skip gracefully without bash
- ✅ Shell handles malformed config
- ✅ Always shows valid prompt
- ✅ Always shows valid exit codes
- ✅ 100% backward compatible
- ✅ More robust and production-ready

---

## Version History

- **0.8.0:** Phase 5 CI/CD complete
- **0.8.1:** Bug fixes for configuration robustness ← **CURRENT**

---

## Checklist

✅ All issues fixed  
✅ All tests passing (229/229)  
✅ Bash tests passing (4/4)  
✅ No linting errors  
✅ Code formatted with black  
✅ Changelog updated  
✅ Version bumped to 0.8.1  
✅ Documentation created

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-10  
**Status:** Complete

