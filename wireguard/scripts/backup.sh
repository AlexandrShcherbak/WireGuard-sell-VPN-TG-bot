#!/usr/bin/env bash
set -euo pipefail

mkdir -p backups/wireguard-configs
cp -r storage/configs backups/wireguard-configs/"$(date +%Y%m%d-%H%M%S)"
