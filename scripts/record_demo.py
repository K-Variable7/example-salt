#!/usr/bin/env python3
"""Record a short demo video using Playwright and save to `videos/`.

Requires: playwright installed and browsers installed (see README).

Usage:
  python scripts/record_demo.py --out videos/demo.mp4 --duration 8

This will open a headed browser, navigate to the demo, perform a short demo run, and save the recorded video.
"""
from playwright.sync_api import sync_playwright
import time
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--out', '-o', default='videos/demo.mp4')
parser.add_argument('--duration', '-d', type=int, default=8)
args = parser.parse_args()

os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)

with sync_playwright() as p:
    # Use headless mode for CI/environment compatibility
    # Try launching with no-sandbox flags to avoid environment issues
    browser = p.chromium.launch(headless=True, args=['--no-sandbox','--disable-setuid-sandbox'])
    try:
        context = browser.new_context(record_video_dir='videos', record_video_size={'width': 800, 'height': 600})
        page = context.new_page()
        page.goto('http://127.0.0.1:5000', timeout=30000)
        # simple demo flow
        page.fill('#password', 'playwright-demo')
        page.click('#demoBtn')
        # wait a bit for demo to run
        time.sleep(args.duration)
        # close context to flush video
        context.close()
    except Exception as e:
        print('Recording failed:', e)
        raise
    finally:
        try:
            browser.close()
        except Exception:
            pass

# find the latest file in videos
import glob
files = glob.glob('videos/*')
if not files:
    print('No video produced')
else:
    latest = max(files, key=os.path.getctime)
    print('Recorded video:', latest)
    try:
        os.replace(latest, args.out)
        print('Saved to', args.out)
    except Exception as e:
        print('Could not move video:', e)