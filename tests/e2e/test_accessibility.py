import json
import pytest


def test_accessibility_main_page(page):
    """Run axe-core accessibility checks against the main content region.

    This uses axe via CDN and fails the test if any violations of impact
    'critical' or 'serious' are found. Developers can run it locally with
    `pytest tests/e2e/test_accessibility.py -q`.
    """
    page.goto("http://127.0.0.1:5000")
    page.wait_for_selector("#main-content")

    # Inject axe-core from CDN
    axe_url = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.2/axe.min.js"
    page.add_script_tag(url=axe_url)

    # Run axe on the main content region only
    result = page.evaluate(
        "async () => { return await axe.run(document.getElementById('main-content'), { runOnly: { type: 'tag', values: ['wcag2a','wcag2aa'] } }); }"
    )

    violations = result.get("violations", []) if isinstance(result, dict) else []
    # Filter for high-impact issues
    serious = [
        v
        for v in violations
        if any(i.get("impact") in ("critical", "serious") for i in v.get("nodes", []))
        or v.get("impact") in ("critical", "serious")
    ]

    if serious:
        report_lines = []
        for v in serious:
            report_lines.append(
                f"{v.get('id')} ({v.get('impact')}): {v.get('description')}"
            )
            for node in v.get("nodes", []):
                target = ",".join(node.get("target", []))
                report_lines.append(f"  - target: {target}")
                report_lines.append(f"    failureSummary: {node.get('failureSummary')}")

        pytest.fail("\nA11y violations found:\n" + "\n".join(report_lines))
