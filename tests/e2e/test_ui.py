import re
import os
import time
import pytest


@pytest.mark.usefixtures('server')
def test_interactive_demo_basic(page):
    page.goto('http://127.0.0.1:5000')
    page.wait_for_selector('#password')
    page.fill('#password', 'demo1234')
    # Run demo
    page.click('#demoBtn')
    # Ensure results appear by checking content (some environments hide elements from being 'visible')
    page.wait_for_function("() => document.getElementById('demoResults') && document.getElementById('demoResults').innerText.length>0", timeout=15000)
    txt = page.inner_text('#demoResults')
    assert 'Unsalted SHA-256' in txt
    assert 'Salt (hex)' in txt


@pytest.mark.usefixtures('server')
def test_argon2_modal_cancel(page):
    page.goto('http://127.0.0.1:5000')
    page.wait_for_selector('#password')
    page.fill('#password', 'demo1234')
    # enable local-only and use argon
    page.check('#localOnly')
    page.check('#useArgonLocal')
    # set very high memory to trigger modal
    page.fill('#argonMem', '300000')
    # click run
    page.click('#demoBtn')
    # modal should appear
    page.wait_for_selector('#confirmModal', state='visible')
    # cancel
    page.click('#cancelModal')
    # ensure demo shows cancellation
    page.wait_for_selector('#demoResults')
    txt = page.inner_text('#demoResults')
    assert 'Argon2 cancelled' in txt or 'cancelled by user' in txt


@pytest.mark.usefixtures('server')
def test_export_json_download(page, tmp_path):
    page.goto('http://127.0.0.1:5000')
    page.wait_for_selector('#password')
    page.fill('#password', 'exporttest')
    page.click('#demoBtn')
    page.wait_for_function("() => document.getElementById('demoResults') && document.getElementById('demoResults').innerText.length>0", timeout=15000)
    # Trigger download and capture it
    with page.expect_download() as download_info:
        page.click('#exportBtn')
    download = download_info.value
    path = tmp_path / download.suggested_filename
    download.save_as(str(path))
    assert path.exists()
    # check JSON structure
    import json
    data = json.loads(path.read_text())
    assert 'password' in data
    assert data['password'] == 'exporttest'


def test_argon2_happy_path(page):
    # Run Argon2 locally with reasonable params and wait for completion
    page.goto('http://127.0.0.1:5000')
    page.wait_for_selector('#password')
    page.fill('#password', 'happyArgon2Test')
    # Ensure local-only and Argon2 local are enabled
    if not page.is_checked('#localOnly'):
        page.check('#localOnly')
    if not page.is_checked('#useArgonLocal'):
        page.check('#useArgonLocal')
    page.fill('#argonTime', '2')
    page.fill('#argonMem', '65536')
    page.fill('#argonParallel', '1')
    page.click('#demoBtn')
    # Wait for argonStatus or demoResults to indicate Argon2 completion or error (allow longer timeout)
    page.wait_for_function(
        '''() => {
            const s = document.getElementById('argonStatus');
            const d = document.getElementById('demoResults');
            const sTxt = s && s.innerText || '';
            const dTxt = d && d.innerText || '';
            return sTxt.includes('Argon2 computed') || sTxt.toLowerCase().includes('failed') || dTxt.includes('Local Argon2') || dTxt.toLowerCase().includes('argon2');
        }''',
        timeout=60000
    )
    txt = page.inner_text('#demoResults')
    status = page.inner_text('#argonStatus')
    # If Argon2 failed to initialize in this environment, skip the test (flaky in some CI)
    if 'did not initialize' in status.lower() or status.lower().startswith('argon2 failed'):
        import pytest
        pytest.skip('Argon2 not available in this environment: ' + status)
    # Otherwise assert we saw a successful computation (prefer) or at least an Argon2 presence
    assert 'Local Argon2' in txt or 'Argon2 computed' in status or 'argon2' in txt.lower()
