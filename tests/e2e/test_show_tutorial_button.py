import pytest


def test_show_tutorial_button_opens_overlay(page):
    page.goto('http://127.0.0.1:5000')
    page.wait_for_selector('#password')
    # Simulate a persisted dismissal
    page.evaluate("() => localStorage.setItem('saltDemo_tutorial_dismissed','true')")
    page.reload()
    page.wait_for_selector('#password')
    # Ensure overlay is not visible
    assert page.is_hidden('#tutorialOverlay')
    # Click show tutorial button
    page.click('#showTutorialBtn')
    # Overlay should appear
    page.wait_for_selector('#tutorialOverlay[aria-hidden="false"]', timeout=2000)
    assert page.is_visible('#tutorialOverlay')
