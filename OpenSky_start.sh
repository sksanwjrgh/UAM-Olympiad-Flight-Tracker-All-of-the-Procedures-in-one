#!/bin/sh
cd "$(dirname "$0")" || exit 1
exec python3 OpenSky_local_proxy.py
