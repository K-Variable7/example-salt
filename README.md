# Salt vs. No-Salt Demonstrator

A small demo web app that shows the difference between unsalted and salted password hashing. Intended for educational and local use only.

## Quick start

1. Create a virtual environment and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the app:

```bash
python app.py
```

3. Open http://127.0.0.1:5000 and paste a few passwords to see the hashes.

## Security notes
- Use only synthetic or permissioned datasets. Do not upload real leaked passwords.
- The demo shows both insecure SHA-256 (unsalted) and salted variants for demonstration. For production, use Argon2/bcrypt/scrypt via well-tested libraries.
- **Local-only mode:** The interactive demo supports a "Local-only" toggle (checked by default). When enabled, all hashing and analysis happen in the browser and **no plaintext is sent to the server**. This is recommended for privacy and demos.

## Next steps
- Add visualizations (crack-time comparisons) — now implemented using Chart.js for crack-time and collision charts
- Add tests and CI (pytest + a GitHub Actions workflow added)
- Visual polish: improved styling (Bulma + custom CSS), icons (Font Awesome), logo, button animations, and result fade-ins

### Running tests locally

Install dev deps: `pip install -r requirements.txt` (includes `pytest` and Playwright tooling).

Run tests:

```bash
pytest -q
```

E2E (Playwright) tests

Install Playwright browsers locally (required for E2E tests):

```bash
python -m playwright install
```

Run E2E tests:

```bash
pytest tests/e2e -q
```

Recording a demo video (for GIF)

You can record a short demo using Playwright and convert the resulting MP4 to GIF via ffmpeg:

1. Record mp4 using the helper script:

```bash
python scripts/record_demo.py --out videos/demo.mp4 --duration 8
```

2. Convert to GIF (requires ffmpeg):

```bash
ffmpeg -ss 0 -t 8 -i videos/demo.mp4 -vf "fps=15,scale=640:-1:flags=lanczos" -loop 0 demo.gif
```

Below is a short demo of the app (Local-only mode). **Privacy note:** the GIF uses synthetic demo passwords and may show them visibly — do not record or commit real passwords. If you prefer, regenerate the GIF with placeholder text.

**Better preview (MP4):** click to open the preview (GitHub renders MP4 inline in the file viewer).

<video controls width="640">
  <source src="videos/demo_preview.mp4" type="video/mp4">
  Your browser does not support the video tag — view the MP4 directly: [videos/demo_preview.mp4](videos/demo_preview.mp4)
</video>


![Demo of Salt vs No-Salt Demonstrator](demo.gif)

- Add Argon2 WASM client-side option for stronger local KDF demonstration (implemented). The demo uses a lazy-loaded CDN build of `argon2-browser` when you enable "Use Argon2 (local)" in Local-only mode.
- Added a confirmation modal which warns and requires consent for high Argon2 resource settings (e.g., memory > 256MB).
- Added an export button that downloads the current demo output and chart data as a JSON file.

## Simulation script
A CLI helper is available at `scripts/simulate.py`.

Example usage:

```bash
python scripts/simulate.py --input data/sample_passwords.txt --users 100 --out data/sim_report.json --pretty
```

This will compute unsalted vs salted behavior and write a JSON report to `data/sim_report.json`.
