import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Attach the result object to the item so fixtures can inspect pass/fail
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


# Video recording disabled to reduce privacy risk and artifact size.
# Per-test Playwright traces were also disabled; CI will only collect screenshots/GIFs and redacted logs on failure.


# Tracing is disabled to avoid uploading sensitive Playwright trace archives.
# We still record per-test videos in CI via Playwright's `record_video_dir`.
