import pytest


def test_rainbow_ui_counts_update(page):
    page.goto('http://127.0.0.1:5000')
    page.wait_for_selector('#rainbowBtn')
    # Use sample fallback list to make results deterministic
    page.fill('#rainbowUsers', '5')
    page.uncheck('#rainbowUsePrecomputed')
    page.click('#rainbowBtn')
    # Wait for results to complete
    page.wait_for_selector('#rainbowInstantCount', timeout=5000)
    # sample list has 6 passwords by default
    instant = int(page.inner_text('#rainbowInstantCount'))
    assert instant == 6 * 5
    # Also check chart updated (dataset value present)
    # Chart updates asynchronously; give brief pause
    page.wait_for_timeout(200)
    assert 'Unsalted (instant cracks)' in page.inner_text('#rainbowResults')
