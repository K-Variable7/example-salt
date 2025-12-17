## Contributing & Debugging: capturing videos & Playwright traces (maintainers only)

Thanks for helping improve this demo — for privacy reasons CI does not record or
upload full Playwright traces or videos by default. If you are a maintainer and
need richer artifacts to diagnose a flaky E2E failure locally, follow the steps
below.

Summary (short)
- To reproduce full artifacts locally: temporarily enable debug artifacts, run the
  failing E2E test locally, then revert the change when done.
- Use `scripts/record_demo.py` to record short MP4 demos without touching tests.

Quick steps (recommended)
1. Create a temporary branch (or work in a disposable local change):

   git checkout -b debug/e2e-trace

2. Edit `tests/e2e/conftest.py` and add the small snippet below (or replace the
   file contents with it). This enables per-test video + Playwright tracing when
   the environment variable `ENABLE_DEBUG_ARTIFACTS` is set.

```py
import os
from pathlib import Path
import pytest


def pytest_configure(config):
    if os.getenv("ENABLE_DEBUG_ARTIFACTS"):
        Path("videos").mkdir(exist_ok=True)
        Path("traces").mkdir(exist_ok=True)


@pytest.fixture
def browser_context_args(browser_context_args):
    if os.getenv("ENABLE_DEBUG_ARTIFACTS"):
        browser_context_args.update({
            "record_video_dir": os.path.abspath("videos"),
            "record_video_size": (1280, 720),
        })
    return browser_context_args


@pytest.fixture(autouse=True)
def trace_on_failure(request, page, tmp_path):
    ci_debug = os.getenv("ENABLE_DEBUG_ARTIFACTS")
    ctx = page.context
    trace_path = None
    if ci_debug:
        ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
        trace_path = tmp_path / f"{request.node.name}.zip"
    yield
    rep_call = getattr(request.node, "rep_call", None)
    if ci_debug and rep_call and rep_call.failed:
        ctx.tracing.stop(path=str(trace_path))
        Path("traces").mkdir(exist_ok=True)
        trace_path.replace(Path("traces") / trace_path.name)
    else:
        try:
            ctx.tracing.stop()
        except Exception:
            pass
```

3. Install Playwright browsers (if not already installed):

```bash
python -m pip install -r requirements.txt
python -m playwright install
```

4. Run the failing test locally with the flag enabled:

```bash
ENABLE_DEBUG_ARTIFACTS=1 pytest tests/e2e -k "not flaky" -q -k <testname>
```

5. Inspect `videos/` and `traces/` in your workspace. Traces can be opened
   using Playwright's trace viewer (`npx playwright show-trace traces/<file>.zip`).

6. When done, revert the temporary changes (do not leave tracing enabled on main branches):

```bash
git checkout main && git branch -D debug/e2e-trace
```

Alternative: record a short demo MP4 without changing tests

```bash
python scripts/record_demo.py --out videos/demo.mp4 --duration 8
ffmpeg -ss 0 -t 8 -i videos/demo.mp4 -vf "fps=15,scale=640:-1:flags=lanczos" -loop 0 demo.gif
```

Security & privacy notes (important)
- Only enable tracing on trusted machines; traces and videos can contain request
  bodies, headers and visible typed values. Never run these against production
  endpoints or with real credentials.
- Keep this workflow local and temporary; do not push traces/videos to branches
  that will be uploaded by CI (we purposely disabled trace uploads in CI).

Thanks — if you'd like, I can also add a small helper script that toggles the
conftest change for you (apply/revert) to make debugging even quicker.
