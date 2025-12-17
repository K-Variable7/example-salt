import os
from pathlib import Path
import pytest


def pytest_configure(config):
    # Ensure directories exist when running in CI
    if os.getenv("CI"):
        Path("videos").mkdir(exist_ok=True)
        Path("traces").mkdir(exist_ok=True)


@pytest.fixture
def browser_context_args(browser_context_args):
    """Add video recording args to Playwright contexts when running under CI."""
    if os.getenv("CI"):
        browser_context_args.update({
            "record_video_dir": os.path.abspath("videos"),
            # Smaller default size to limit artifact size
            "record_video_size": (800, 600),
        })
    return browser_context_args


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Attach the result object to the item so fixtures can inspect pass/fail
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def _trace_on_failure(request, page, tmp_path):
    """Start a Playwright trace for a test and save it only if the test fails.

    This keeps tracing off-by-default locally, but provides rich traces for CI failures.
    """
    ci = os.getenv("CI")
    ctx = page.context
    trace_path = None
    if ci:
        # Start tracing (captures snapshots, screenshots, and source files)
        ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
        trace_path = tmp_path / f"{request.node.name}.zip"

    yield

    # After test: if it failed, stop tracing and save; otherwise stop without saving
    rep_call = getattr(request.node, "rep_call", None)
    if ci and rep_call is not None:
        try:
            if rep_call.failed:
                ctx.tracing.stop(path=str(trace_path))
                # move trace into traces/ for CI artifact collection
                dest = Path("traces") / trace_path.name
                trace_path.replace(dest)
            else:
                ctx.tracing.stop()
        except Exception:
            # Best-effort; don't fail the test teardown if tracing blows up
            try:
                ctx.tracing.stop()
            except Exception:
                pass