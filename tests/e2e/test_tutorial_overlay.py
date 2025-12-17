import pytest


def test_tutorial_shows_and_persists(page):
    page.goto("http://127.0.0.1:5000")
    # Wait for overlay to appear
    page.wait_for_selector('#tutorialOverlay[aria-hidden="false"]', timeout=5000)
    assert page.is_visible('#tutorialOverlay')
    # Click 'Got it' to dismiss and persist
    page.click('#dismissTutorial')
    # Overlay should be hidden (wait briefly for DOM updates)
    page.wait_for_timeout(300)
    assert page.is_hidden('#tutorialOverlay')
    # Reload page; overlay should not reappear
    page.reload()
    # Wait briefly and assert overlay not visible
    page.wait_for_timeout(500)
    assert page.is_hidden('#tutorialOverlay')
