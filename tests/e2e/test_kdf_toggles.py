import pytest


def test_bcrypt_local_compute(page):
    page.goto('http://127.0.0.1:5000')
    page.wait_for_selector('#password')
    page.fill('#password', 'bcryptDemo123')
    page.check('#useBcryptLocal')
    # Use fewer rounds for CI speed
    page.fill('#bcryptRounds', '6')
    page.click('#demoBtn')
    # Wait until local bcrypt output appears in results
    page.wait_for_selector('text=Local bcrypt', timeout=20000)
    assert 'Local bcrypt' in page.inner_text('#demoResults')


def test_scrypt_local_compute(page):
    page.goto('http://127.0.0.1:5000')
    page.wait_for_selector('#password')
    page.fill('#password', 'scryptDemo456')
    page.check('#useScryptLocal')
    # Reduce work factor for CI
    page.fill('#scryptN', '1024')
    page.fill('#scryptR', '1')
    page.fill('#scryptP', '1')
    page.click('#demoBtn')
    page.wait_for_selector('text=Local scrypt', timeout=20000)
    assert 'Local scrypt' in page.inner_text('#demoResults')


def test_rainbow_simulator_instant_crack(page):
    page.goto('http://127.0.0.1:5000')
    page.wait_for_selector('#rainbowBtn')
    page.fill('#rainbowUsers', '10')
    page.check('#rainbowUsePrecomputed')
    page.click('#rainbowBtn')
    page.wait_for_selector('#rainbowResults')
    txt = page.inner_text('#rainbowResults')
    assert 'Unsalted (instant cracks)' in txt
