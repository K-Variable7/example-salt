#!/usr/bin/env python3
"""Record a short demo by taking screenshots and composing a GIF using ffmpeg.

Usage:
  python scripts/record_screenshots.py --out demo.gif

This uses Playwright headless to capture key frames and converts them to an animated GIF.
"""
from playwright.sync_api import sync_playwright
import os, time, argparse, glob, subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--out', '-o', default='demo.gif')
parser.add_argument('--tmpdir', '-t', default='videos/frames')
args = parser.parse_args()

os.makedirs(args.tmpdir, exist_ok=True)

frames = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox','--disable-setuid-sandbox'])
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto('http://127.0.0.1:5000', timeout=30000)
    # initial state
    p1 = os.path.join(args.tmpdir, 'frame01.png')
    page.screenshot(path=p1, full_page=True)
    frames.append(p1)

    # fill password and show strength
    page.fill('#password', 'demoGif123')
    time.sleep(0.2)
    p2 = os.path.join(args.tmpdir, 'frame02.png')
    page.screenshot(path=p2, full_page=True)
    frames.append(p2)

    # click run and wait for results
    page.click('#demoBtn')
    page.wait_for_function("() => document.getElementById('demoResults') && document.getElementById('demoResults').innerText.length>0", timeout=15000)
    time.sleep(0.5)
    p3 = os.path.join(args.tmpdir, 'frame03.png')
    page.screenshot(path=p3, full_page=True)
    frames.append(p3)

    # toggle dark mode and show results
    try:
        page.click('#darkToggle')
        time.sleep(0.3)
        p4 = os.path.join(args.tmpdir, 'frame04.png')
        page.screenshot(path=p4, full_page=True)
        frames.append(p4)
    except Exception:
        pass

    ctx.close()
    browser.close()

# Make GIF using ffmpeg (if available)
if not frames:
    raise SystemExit('No frames captured')

# Create palette
palette = os.path.join(args.tmpdir, 'palette.png')
cmd1 = ['ffmpeg', '-y', '-i', os.path.join(args.tmpdir, 'frame%02d.png'), '-vf', 'palettegen', palette]
cmd2 = ['ffmpeg', '-y', '-i', os.path.join(args.tmpdir, 'frame%02d.png'), '-i', palette, '-lavfi', 'paletteuse', args.out]

print('Frames:', frames)
try:
    subprocess.check_call(cmd1)
    subprocess.check_call(cmd2)
    print('Saved GIF to', args.out)
except Exception as e:
    print('Failed to create GIF:', e)
    print('Frames are in', args.tmpdir)
