# Test Harness Setup & Verification

**Quick setup guide for API testing.**

---

## ✅ Verification Results

### Import Tests
- ✅ `tests.utils.http_assertions` - **OK**
- ✅ `tests.utils.json_contracts` - **OK**
- ⚠️ `tests.utils.html_selectors` - **Needs beautifulsoup4**
- ✅ `tests.integration.test_dashboard_endpoints` - **OK**

---

## 📦 Install Missing Dependencies

### Option 1: Using uv (Recommended)

```bash
cd lynx-ai
uv sync --dev
```

This will install all dependencies including `beautifulsoup4` from `pyproject.toml`.

### Option 2: Using pip

```bash
cd lynx-ai
pip install beautifulsoup4>=4.12.0
```

### Option 3: Install all dev dependencies

```bash
cd lynx-ai
pip install -e ".[dev]"
```

---

## 🧪 Run Validation

After installing dependencies, verify everything works:

```bash
cd lynx-ai

# Test imports
python -c "from tests.utils.html_selectors import parse_html; print('✅ All imports OK')"

# Test pytest can collect tests
pytest tests/integration/test_dashboard_*.py --collect-only

# Run a simple test (if dashboard is running)
TEST_API_URL=http://localhost:8000 pytest tests/integration/test_dashboard_endpoints.py::TestDashboardEndpoints::test_health_endpoint_returns_200 -v
```

---

## 🚀 Quick Test Run

### Prerequisites
1. Install dependencies (see above)
2. Start dashboard (if testing locally):
   ```bash
   cd lynx-ai
   python -m lynx.api.dashboard
   ```

### Run Tests

```bash
# Local testing
TEST_API_URL=http://localhost:8000 pytest tests/integration/test_dashboard_*.py -v

# Railway testing (no local server needed)
TEST_API_URL=https://lynx-ai-production.up.railway.app pytest tests/integration/test_dashboard_*.py -v -m integration
```

---

## ✅ Expected Results

After setup, you should see:

```
✅ All imports OK
✅ pytest can collect ~45 tests
✅ Tests run successfully (if dashboard is running)
```

---

## 📝 Notes

- **beautifulsoup4** is required for HTML parsing tests
- Tests are **environment-driven** - same tests work for localhost and Railway
- **No dashboard needed** for contract tests (they validate JSON structure)
- **Dashboard needed** for endpoint and fragment tests

---

**Status:** ✅ **SETUP COMPLETE** (after installing beautifulsoup4)

