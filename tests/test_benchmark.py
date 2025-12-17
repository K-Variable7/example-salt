import subprocess
import sys
import os


def test_benchmark_script_runs_quickly():
    """Run the benchmark script with small params to ensure it executes without error."""
    root = os.path.dirname(os.path.dirname(__file__))
    script = os.path.join(root, 'scripts', 'benchmark_kdfs.py')
    cmd = [sys.executable, script, '--password', 'test', '--argon-time', '1', '--argon-mem', '8', '--bcrypt-rounds', '4', '--scrypt-n', '1024', '--scrypt-r', '1', '--scrypt-p', '1']
    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, f"Benchmark script failed: {proc.stderr}\n{proc.stdout}"
    assert 'Benchmarking' in proc.stdout
