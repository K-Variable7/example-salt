import pytest
from scripts import simulate


def test_simulate_empty_list():
    report = simulate.simulate([], users_per_password=10)
    assert report['summary']['total_passwords'] == 0
    assert report['per_password'] == {}


def test_simulate_single_user():
    pws = ['s']
    report = simulate.simulate(pws, users_per_password=1, attacker_speeds=(1e6,))
    assert report['summary']['total_passwords'] == 1
    v = next(iter(report['per_password'].values()))
    assert v['salted_unique_count'] == 1


def test_simulate_high_users_unique_counts():
    pws = ['alpha']
    report = simulate.simulate(pws, users_per_password=50)
    v = report['per_password']['alpha']
    assert v['salted_unique_count'] == 50


def test_entropy_zero_for_empty_password():
    pws = ['']
    report = simulate.simulate(pws, users_per_password=3)
    v = report['per_password']['']
    assert v['entropy_bits'] == 0
