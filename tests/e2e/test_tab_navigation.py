import pytest


def tab_until(page, target_id, max_tabs=30):
    # Press Tab up to max_tabs until document.activeElement.id == target_id
    for _ in range(max_tabs):
        active = page.evaluate('document.activeElement && document.activeElement.id')
        if active == target_id:
            return True
        page.keyboard.press('Tab')
        page.wait_for_timeout(40)
    return False


def test_main_controls_reachable_by_tab(page):
    page.goto('http://127.0.0.1:5000')
    page.wait_for_selector('#password')
    targets = ['password', 'showPwd', 'generate', 'showTutorialBtn', 'demoBtn', 'localOnly', 'useArgonLocal', 'rainbowBtn']
    for tid in targets:
        assert tab_until(page, tid), f"Could not reach {tid} via Tab within limit"
