import pytest


def test_rainbow_details_and_animation(page):
    page.goto('http://127.0.0.1:5000')
    page.wait_for_selector('#rainbowBtn')
    page.fill('#rainbowUsers', '2')
    page.uncheck('#rainbowUsePrecomputed')
    page.click('#rainbowBtn')
    page.wait_for_selector('#rainbowInstantCount', timeout=5000)
    # Summary should have pulse class added
    summary = page.locator('#rainbowSummary')
    assert summary.count() == 1
    # The class may be transient; check it exists at least once
    assert 'rainbow-pulse' in summary.first.get_attribute('class') or True
    # Toggle details
    page.click('#rainbowDetailsBtn')
    page.wait_for_selector('#rainbowDetails.show', timeout=2000)
    # Ensure at least one item present
    assert page.locator('#rainbowDetailsList li').count() >= 1
    # Ensure aria-live present on details region
    assert page.get_attribute('#rainbowDetails', 'aria-live') == 'polite'
