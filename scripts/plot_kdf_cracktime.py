#!/usr/bin/env python3
"""Generate plots showing how estimated crack time grows with KDF parameters.

This script uses the benchmark helpers in `scripts/benchmark_kdfs.py` to measure
per-hash times for small, demo-friendly parameter values and then multiplies by
guesses=2^entropy to estimate total crack times. Outputs PNG files in `plots/`.
"""
import os
import math
import argparse
import matplotlib.pyplot as plt
from scripts.benchmark_kdfs import bench_bcrypt, bench_scrypt, bench_argon


def guesses_from_entropy(bits):
    return 2 ** bits


def safe_time(res):
    if not res:
        return None
    return res['avg']


def plot_bcrypt(password='demo', rounds_range=range(6, 13), entropy_bits=60, out='plots/bcrypt_cracktime.png'):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    times = []
    for r in rounds_range:
        res = bench_bcrypt(password, rounds=r)
        t = safe_time(res) or 0
        times.append(t * guesses_from_entropy(entropy_bits))
    plt.figure(figsize=(8,4))
    plt.plot(list(rounds_range), times, marker='o')
    plt.yscale('log')
    plt.xlabel('bcrypt rounds')
    plt.ylabel('Estimated crack time (seconds, log scale)')
    plt.title(f'bcrypt crack-time (entropy={entropy_bits} bits)')
    plt.grid(True, which='both', ls='--', alpha=0.6)
    plt.savefig(out, dpi=150)
    print('Wrote', out)


def plot_argon(password='demo', time_vals=[1,2,3,4], mem_kb=16384, entropy_bits=60, out='plots/argon_cracktime.png'):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    times = []
    for tcost in time_vals:
        res = bench_argon(password, time_cost=tcost, memory_cost=mem_kb)
        t = safe_time(res) or 0
        times.append(t * guesses_from_entropy(entropy_bits))
    plt.figure(figsize=(8,4))
    plt.plot(time_vals, times, marker='o')
    plt.yscale('log')
    plt.xlabel('Argon2 time cost (iterations)')
    plt.ylabel('Estimated crack time (seconds, log scale)')
    plt.title(f'Argon2 crack-time (mem={mem_kb}KB, entropy={entropy_bits} bits)')
    plt.grid(True, which='both', ls='--', alpha=0.6)
    plt.savefig(out, dpi=150)
    print('Wrote', out)


def plot_scrypt(password='demo', n_vals=[1024,4096,16384], r=1, p=1, entropy_bits=60, out='plots/scrypt_cracktime.png'):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    times = []
    for N in n_vals:
        res = bench_scrypt(password, n=N, r=r, p=p)
        t = safe_time(res) or 0
        times.append(t * guesses_from_entropy(entropy_bits))
    plt.figure(figsize=(8,4))
    plt.plot(n_vals, times, marker='o')
    plt.xscale('log', base=2)
    plt.yscale('log')
    plt.xlabel('scrypt N (log scale)')
    plt.ylabel('Estimated crack time (seconds, log scale)')
    plt.title(f'scrypt crack-time (r={r}, p={p}, entropy={entropy_bits} bits)')
    plt.grid(True, which='both', ls='--', alpha=0.6)
    plt.savefig(out, dpi=150)
    print('Wrote', out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--entropy', type=int, default=60)
    args = parser.parse_args()

    plot_bcrypt(entropy_bits=args.entropy)
    plot_argon(entropy_bits=args.entropy)
    plot_scrypt(entropy_bits=args.entropy)


if __name__ == '__main__':
    main()
