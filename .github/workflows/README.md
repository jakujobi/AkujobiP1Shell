# GitHub Actions CI/CD

This directory contains the CI/CD configuration for AkujobiP1Shell.

## Workflow: `ci.yml`

The main CI workflow runs automatically on:
- Pushes to `main`, `master`, or `develop` branches
- Pull requests to `main`, `master`, or `develop` branches
- Manual trigger (workflow_dispatch)

### Jobs

#### 1. Test Job
Runs the full test suite on multiple Python versions.

**Matrix:**
- Python 3.10
- Python 3.11
- Python 3.12

**Steps:**
1. Checkout code
2. Set up Python
3. Cache pip packages (for faster runs)
4. Install dependencies
5. Verify installation
6. Run pytest with coverage
7. Run bash integration tests
8. Upload coverage to Codecov (Python 3.10 only)
9. Verify test count (must have 225+ tests)

**Duration:** ~2-3 minutes per Python version

#### 2. Lint Job
Checks code quality and formatting.

**Steps:**
1. Run ruff linter on `src/` and `tests/`
2. Check code formatting with black
3. Check for debug prints and hardcoded paths

**Duration:** ~1 minute

#### 3. Package Job
Verifies the package can be built and installed.

**Steps:**
1. Build Python package (wheel and sdist)
2. Check package with twine
3. Test installation from wheel
4. Verify command works

**Duration:** ~1 minute

#### 4. Summary Job
Aggregates results from all jobs.

**Steps:**
1. Check all job results
2. Fail if any job failed
3. Report success if all passed

### Status Badge

Add this to your README to show CI status:

```markdown
![CI](https://github.com/jakujobi/AkujobiP1Shell/workflows/CI/badge.svg)
```

### Local Testing

Before pushing, you can run the same checks locally:

```bash
# Run tests
pytest --cov=src/akujobip1 --cov-report=term -v

# Run bash tests
bash tests/run_tests.sh

# Run linter
ruff check src/ tests/

# Check formatting
black --check src/ tests/

# Build package
python -m build
twine check dist/*
```

### Troubleshooting

**If the workflow fails:**

1. **Test failures:** Check the test logs in the workflow run
2. **Linting errors:** Run `ruff check src/ tests/` locally
3. **Formatting issues:** Run `black src/ tests/` to auto-fix
4. **Package build issues:** Check `pyproject.toml` configuration

**Common issues:**

- **Import errors:** Make sure all dependencies are in `pyproject.toml`
- **Path issues:** Use relative paths, not absolute paths
- **Test count low:** Verify all test files are included

### Maintenance

**Update Python versions:**
Edit the matrix in `ci.yml`:
```yaml
matrix:
  python-version: ['3.10', '3.11', '3.12']
```

**Add new checks:**
Add new steps to the `lint` job or create a new job.

**Disable codecov:**
Remove or comment out the "Upload coverage to Codecov" step if you don't have a Codecov account.

---

**Created:** 2025-11-10  
**Last Updated:** 2025-11-10  
**Version:** 1.0

