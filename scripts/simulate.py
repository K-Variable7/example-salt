#!/usr/bin/env python3
"""Simulation script for Salt vs No-Salt Demonstrator

Usage:
  python scripts/simulate.py --input data/sample_passwords.txt --users 100 --out data/sim_report.json

This script performs the following:
- Loads a password list (sample or provided)
- Computes unsalted SHA-256 for each password
- Simulates `users` users sharing the same password to compute salted hashes (CSPRNG salts)
- Builds a small 'rainbow table' of known passwords (from the input) and checks if unsalted hashes would be found instantly
- Estimates brute-force crack time from estimated entropy bits and chosen attacker speed
- Writes a JSON report with summary stats
"""

import argparse
import hashlib
import json
import os
import secrets
import time
from collections import Counter, defaultdict


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def estimate_entropy_bits(password: str) -> int:
    if not password:
        return 0
    charset = 0
    if any(c.islower() for c in password):
        charset += 26
    if any(c.isupper() for c in password):
        charset += 26
    if any(c.isdigit() for c in password):
        charset += 10
    if any(not c.isalnum() for c in password):
        charset += 32
    if charset == 0:
        charset = 26
    import math
    bits = math.log2(charset) * len(password)
    return int(round(bits))


def read_passwords(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def simulate(passwords, users_per_password=100, attacker_speeds=(1e7, 1e9)):
    report = {
        'total_passwords': len(passwords),
        'per_password': {},
        'summary': {}
    }

    # Precompute unsalted for rainbow table simulation (we'll use all passwords as 'known')
    rainbow = {sha256_hex(p.encode('utf-8')): p for p in passwords}

    per_pw = {}

    for pw in passwords:
        unsalted = sha256_hex(pw.encode('utf-8'))
        # simulate multiple users and create salted hashes
        salts = [secrets.token_bytes(16) for _ in range(users_per_password)]
        salted_hashes = [sha256_hex(s + pw.encode('utf-8')) for s in salts]
        unique_salted = len(set(salted_hashes))
        unique_unsalted = 1  # same password yields same unsalted

        # rainbow table hit (unsalted only)
        rainbow_hit = unsalted in rainbow

        # entropy estimate
        entropy = estimate_entropy_bits(pw)

        # estimate crack times
        crack_times = {}
        for speed in attacker_speeds:
            guesses = 2 ** entropy if entropy > 0 else 1
            seconds = guesses / float(speed)
            crack_times[str(int(speed))] = seconds

        per_pw[pw] = {
            'unsalted_sha256': unsalted,
            'salted_unique_count': unique_salted,
            'rainbow_hit_unsalted': rainbow_hit,
            'entropy_bits': entropy,
            'crack_times_sec': crack_times
        }

    report['per_password'] = per_pw

    # summary stats
    total_rainbow_hits = sum(1 for v in per_pw.values() if v['rainbow_hit_unsalted'])
    avg_entropy = sum(v['entropy_bits'] for v in per_pw.values()) / len(per_pw) if per_pw else 0

    report['summary'] = {
        'total_passwords': len(passwords),
        'total_rainbow_hits_unsalted': total_rainbow_hits,
        'avg_entropy_bits': avg_entropy,
        'users_simulated_per_password': users_per_password
    }

    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', default='data/sample_passwords.txt')
    parser.add_argument('--users', '-u', type=int, default=100)
    parser.add_argument('--out', '-o', default='data/sim_report.json')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print('Input file not found:', args.input)
        raise SystemExit(1)

    pws = read_passwords(args.input)
    start = time.time()
    report = simulate(pws, users_per_password=args.users)
    elapsed = time.time() - start

    if args.pretty:
        print('Simulation completed in %.2fs' % elapsed)
        print('Total passwords:', report['summary']['total_passwords'])
        print('Rainbow hits (unsalted):', report['summary']['total_rainbow_hits_unsalted'])
        print('Avg entropy bits:', report['summary']['avg_entropy_bits'])
        print('Sample entry (first password):')
        first = next(iter(report['per_password'].items()))
        print(' ', first[0])
        print(' ', first[1])

    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print('Wrote report to', args.out)


if __name__ == '__main__':
    main()
