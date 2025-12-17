from app import app


def test_tooltip_elements_present_in_index():
    client = app.test_client()
    rv = client.get('/')
    assert rv.status_code == 200
    html = rv.get_data(as_text=True)

    tooltip_ids = [
        'tip-argonTime', 'tip-argonMem', 'tip-argonParallel',
        'tip-bcryptRounds', 'tip-scryptN', 'tip-scryptR', 'tip-scryptP'
    ]

    for tid in tooltip_ids:
        assert f'id="{tid}"' in html, f"Missing tooltip id {tid} in index.html"
        assert f'id="{tid}" role="tooltip"' in html, f"Tooltip {tid} missing role=tooltip"

    # Ensure tooltip hosts link to the tooltip via aria-describedby
    for tid in tooltip_ids:
        assert f'aria-describedby="{tid}"' in html, f"Tooltip host for {tid} missing aria-describedby"
