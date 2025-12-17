import pytest


def test_kdf_tooltips_show_on_focus(page):
    page.goto("http://127.0.0.1:5000")
    page.wait_for_selector("#password")
    # Argon2 time tooltip exists and becomes visible on focus
    tooltip_host = page.locator('span[aria-describedby="tip-argonTime"]')
    assert tooltip_host.count() == 1
    tooltip_host.focus()
    # The tooltip text should become visible
    page.wait_for_selector('#tip-argonTime', timeout=2000)
    assert page.is_visible('#tip-argonTime')
