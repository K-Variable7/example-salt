#!/usr/bin/env python3
"""Benchmark basic KDFs (Argon2, bcrypt, scrypt) with demo-friendly params.

Usage examples:
  python scripts/benchmark_kdfs.py --password demoPass
  python scripts/benchmark_kdfs.py --argon-time 2 --argon-mem 32768

This script is intended for demos/teaching and uses low-cost defaults so it runs
quickly in CI; do not use shown parameters for production.
"""
import argparse
import json
import time
import os
import sys
import hashlib

try:
    from argon2 import PasswordHasher
except Exception:
    PasswordHasher = None

try:
    import bcrypt
except Exception:
    bcrypt = None


def measure(func, repeats=3):
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        func()
        t1 = time.perf_counter()
        times.append(t1 - t0)
    return {"min": min(times), "avg": sum(times) / len(times), "max": max(times)}


def bench_argon(password, time_cost=1, memory_cost=32768, parallelism=1):
    if PasswordHasher is None:
        return None
    ph = PasswordHasher(time_cost=time_cost, memory_cost=memory_cost, parallelism=parallelism)
    def f():
        ph.hash(password)
    return measure(f)


def bench_bcrypt(password, rounds=10):
    if bcrypt is None:
        return None
    pw = password.encode('utf-8')
    def f():
        salt = bcrypt.gensalt(rounds)
        bcrypt.hashpw(pw, salt)
    return measure(f)


def bench_scrypt(password, n=16384, r=8, p=1, dklen=32):
    pw = password.encode('utf-8')
    salt = os.urandom(16)
    def f():
        hashlib.scrypt(pw, salt=salt, n=n, r=r, p=p, dklen=dklen)
    return measure(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--password', '-p', default='demoPass123!', help='Password to benchmark')
    parser.add_argument('--repeats', '-r', type=int, default=3)
    parser.add_argument('--argon-time', type=int, default=1)
    parser.add_argument('--argon-mem', type=int, default=32768, help='Argon2 memory in KB')
    parser.add_argument('--argon-par', type=int, default=1)
    parser.add_argument('--bcrypt-rounds', type=int, default=10)
    parser.add_argument('--scrypt-n', type=int, default=16384)
    parser.add_argument('--scrypt-r', type=int, default=8)
    parser.add_argument('--scrypt-p', type=int, default=1)
    parser.add_argument('--json', action='store_true', help='Output JSON')
    args = parser.parse_args()

    out = {"password": args.password}

    # Argon2
    if PasswordHasher is not None:
        print(f'Benchmarking Argon2: time={args.argon_time}, mem={args.argon_mem}KB, par={args.argon_par}...')
        res = bench_argon(args.password, time_cost=args.argon_time, memory_cost=args.argon_mem, parallelism=args.argon_par)
        out['argon2'] = res
        print('  ', res)
    else:
        print('Argon2 (argon2-cffi) not available; skipping Argon2')

    # bcrypt
    if bcrypt is not None:
        print(f'Benchmarking bcrypt: rounds={args.bcrypt_rounds}...')
        res = bench_bcrypt(args.password, rounds=args.bcrypt_rounds)
        out['bcrypt'] = res
        print('  ', res)
    else:
        print('bcrypt not available; skipping bcrypt (install `bcrypt` to enable)')

    # scrypt
    print(f'Benchmarking scrypt: N={args.scrypt_n}, r={args.scrypt_r}, p={args.scrypt_p}...')
    try:
        res = bench_scrypt(args.password, n=args.scrypt_n, r=args.scrypt_r, p=args.scrypt_p)
        out['scrypt'] = res
        print('  ', res)
    except Exception as e:
        out['scrypt_error'] = str(e)
        print('scrypt failed:', e)

    if args.json:
        print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
