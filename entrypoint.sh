#!/bin/bash
# Generates fresh passwords + ciphertexts on every container start,
# so every player/instance gets a unique answer.
set -e

if [ ! -f /etc/krypton_pass/.initialized ]; then
    python3 /opt/krypton/generate.py
    touch /etc/krypton_pass/.initialized
fi

ssh-keygen -A >/dev/null 2>&1
exec /usr/sbin/sshd -D -e
