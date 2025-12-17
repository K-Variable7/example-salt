from scripts import simulate

def test_simulate_report():
    pws = ['alpha','beta']
    report = simulate.simulate(pws, users_per_password=3, attacker_speeds=(1e6,))
    assert 'per_password' in report
    assert 'summary' in report
    assert report['summary']['total_passwords'] == 2
    for pw, val in report['per_password'].items():
        # rainbow should hit for inputs
        assert val['rainbow_hit_unsalted'] is True
        assert val['salted_unique_count'] == 3
        assert val['entropy_bits'] >= 0
