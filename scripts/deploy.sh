#!/usr/bin/env bash
set -euo pipefail

git pull --rebase
bash scripts/restart.sh
