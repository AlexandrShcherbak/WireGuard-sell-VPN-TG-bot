#!/usr/bin/env bash
set -euo pipefail

mkdir -p backups
cp vpn_bot.db "backups/vpn_bot-$(date +%Y%m%d-%H%M%S).db"
