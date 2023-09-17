#!/usr/bin/env bash

echo '[+] Migrating database'
alembic upgrade head

echo '[+] Starting main application'
python3 main.py