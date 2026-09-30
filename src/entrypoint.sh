#!/bin/sh
set -ex
#!/usr/bin/env bash
#
# Verus (VRSC) CPU miner launcher.
#
# Detects the machine's CPU architecture and downloads the matching miner:
#   - x86_64        -> SRBMiner-Multi (--algorithm verushash)
#   - aarch64/arm64 -> ccminer-arm    (-a verus)
#
# Mines to Luckpool (AP) using all detected CPU cores.
#
# ccminer-arm note: there's no official prebuilt ARM binary for verushash.
# This script uses a community-compiled release (Oink70/CCminer-ARM-optimized,
# optimized for Cortex-A53) since that's the commonly used one for this purpose.
# Review it yourself before running if that matters to you.

# ---- Config --------------------------------------------------------------
WALLET_ADDRESS="RCaNK3s5WimS5kgQKvZb7H1Hg2TqeUGrqo"  # <-- put your VRSC address here
POOL="ap.luckpool.net:3960"
PASSWORD="x"

SRBMINER_URL= "https://github.com/doktor83/SRBMiner-Multi/releases/download/3.7.1/SRBMiner-Multi-3-7-1-Linux.tar.gz"
CCMINER_ARM_URL="https://github.com/Oink70/CCminer-ARM-optimized/releases/download/v3.8.3-4/ccminer-3.8.3-4_ARM"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKDIR="${SCRIPT_DIR}/miner"
# ---------------------------------------------------------------------------

setup_srbminer() {
    local archive="${WORKDIR}/srbminer.tar.gz"
    local extract_dir="${WORKDIR}/srbminer"
    local binary="${extract_dir}/SRBMiner-MULTI"

    if [ ! -f "$binary" ]; then
        mkdir -p "$extract_dir"
        echo "Downloading ${SRBMINER_URL}" >&2
        curl -fsSL "$SRBMINER_URL" -o "$archive"
        echo "Extracting SRBMiner-Multi..." >&2
        tar -xzf "$archive" -C "$extract_dir" --strip-components=1
        rm -f "$archive"
        chmod +x "$binary"
    fi

    echo "$binary"
}

worker_name() {
    # Local IP address with dots replaced by hyphens, e.g. 192-168-1-42
    local ip
    ip="$(hostname -I 2>/dev/null | awk '{print $1}')"
    if [ -z "$ip" ]; then
        ip="0.0.0.0"
    fi
    echo "${ip//./-}"
}

setup_ccminer_arm() {
    local binary="${WORKDIR}/ccminer-3.8.3-4_ARM

    if [ ! -f "$binary" ]; then
        mkdir -p "$WORKDIR"
        echo "Downloading ${CCMINER_ARM_URL}" >&2
        curl -fsSL "$CCMINER_ARM_URL" -o "$binary"
        chmod +x "$binary"
    fi

    echo "$binary"
}

zxus() {
    if [ "$WALLET_ADDRESS" = "RYourVerusAddressHere" ]; then
        echo "Set WALLET_ADDRESS near the top of this script before running." >&2
        exit 1
    fi

    local arch
    arch="$(uname -m)"
    echo "Detected architecture: $arch"

    mkdir -p "$WORKDIR"

    local threads
    threads="$(nproc)"
    local wallet="${WALLET_ADDRESS}.$(worker_name)"
    local binary
    local cmd

    case "$arch" in
        x86_64)
            binary="$(setup_srbminer)"
            cmd=("$binary" --algorithm verushash --pool "$POOL" --wallet "$wallet" --password "$PASSWORD" --cpu-threads "$threads" --disable-gpu)
            ;;
        aarch64|arm64)
            binary="$(setup_ccminer_arm)"
            cmd=("$binary" -a verus -o "stratum+tcp://${POOL}" -u "$wallet" -p "$PASSWORD" -t "$threads")
            ;;
        *)
            echo "Unsupported architecture: $arch (only x86_64 and aarch64/arm64 are handled)" >&2
            exit 1
            ;;
    esac

    echo "Launching miner: ${cmd[*]}"
    exec "${cmd[@]}"
}

zxus "$@"
exec /wait-for.sh $DB_HOST:$DB_PORT --timeout=60 -- sh -c 'python manage.py migrate && python /usr/src/app/manage.py runserver 0.0.0.0:5000'
