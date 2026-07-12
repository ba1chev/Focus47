# Focus47

## Testing

Tests live in `tests/` (unit, integration, UI). Install dependencies first:

```bash
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium   # for UI tests
```

Run the tests:

```bash
.venv/bin/pytest              # everything
.venv/bin/pytest tests/unit   # unit only
.venv/bin/pytest -m "not ui"  # skip the browser tests
```

Tests use an isolated temporary database, so the real `focus47.db` is never touched.