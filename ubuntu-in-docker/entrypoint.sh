#!/bin/bash
set -e

echo "Starting SSH Daemon..."
# Start SSH in the background
/usr/sbin/sshd

echo "Starting Cloudflare Tunnel..."
# Run cloudflared directly with the token
# This is preferred over 'service install' in Docker as we want the process to run in the foreground (or be managed here)
# and we don't have systemd in a standard container.
cloudflared tunnel run --token eyJhIjoiYjE5OTY2YmVjODMzMTEyZGZjY2JjNjAyYzkyM2NmY2YiLCJ0IjoiNzVmZTMwM2EtZDA0ZS00NDUxLWI4ZmItMmEyOTc1ZjZmNzY5IiwicyI6IlltRXdaV1U1T0dZdFltWmpOeTAwWVRneUxUa3pNVFl0WkRrNVl6YzJPRFJrTTJSayJ9