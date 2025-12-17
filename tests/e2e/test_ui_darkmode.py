import pytest

@pytest.mark.usefixtures('server')
def test_dark_mode_toggle(page):
    page.goto('http://127.0.0.1:5000')
    page.wait_for_selector('#darkToggle')
    # Ensure it's unchecked initially (could be true depending on system prefs)
    initial = page.is_checked('#darkToggle')
    page.click('#darkToggle')
    assert page.is_checked('#darkToggle') != initial
    # Body should toggle 'dark' class
    assert ('dark' in page.evaluate("() => document.body.classList.value"))


@pytest.mark.usefixtures('server')
def test_show_password_toggle(page):
    page.goto('http://127.0.0.1:5000')
    page.wait_for_selector('#password')
    page.fill('#password', 'showme')
    # ensure default type=password
    assert page.get_attribute('#password', 'type') == 'password'
    page.check('#showPwd')
    assert page.get_attribute('#password', 'type') == 'text'
    page.uncheck('#showPwd')
    assert page.get_attribute('#password', 'type') == 'password'
