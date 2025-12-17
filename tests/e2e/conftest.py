import os
from pathlib import Path
import pytest


def pytest_configure(config):
    # Ensure directories exist when running in CI
    if os.getenv("CI"):
        Path("videos").mkdir(exist_ok=True)


@pytest.fixture
def browser_context_args(browser_context_args):
    """Add video recording args to Playwright contexts when running under CI."""
    if os.getenv("CI"):
        browser_context_args.update(
            {
                "record_video_dir": os.path.abspath("videos"),
                # Smaller default size to limit artifact size
                "record_video_size": (800, 600),
            }
        )
    return browser_context_args


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Attach the result object to the item so fixtures can inspect pass/fail
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


# Tracing is disabled to avoid uploading sensitive Playwright trace archives.
# We still record per-test videos in CI via Playwright's `record_video_dir`.
