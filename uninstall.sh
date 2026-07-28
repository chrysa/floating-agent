#!/usr/bin/env bash
set -euo pipefail

data_home="${XDG_DATA_HOME:-$HOME/.local/share}"
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
bin_home="${XDG_BIN_HOME:-$HOME/.local/bin}"

install_root="$data_home/floating-agent"
venv_dir="$install_root/venv"
manifest_file="$install_root/install-manifest.json"
desktop_file="$data_home/applications/floating-agent.desktop"
service_file="$config_home/systemd/user/floating-agent.service"
env_file="$config_home/floating-agent/install.env"
launcher="$bin_home/floating-agent"

if command -v systemctl >/dev/null 2>&1; then
  systemctl --user stop floating-agent.service >/dev/null 2>&1 || true
  systemctl --user disable floating-agent.service >/dev/null 2>&1 || true
  systemctl --user daemon-reload >/dev/null 2>&1 || true
fi

rm -f "$launcher" "$desktop_file" "$service_file" "$env_file" "$manifest_file"
rm -rf "$venv_dir"

printf 'removed launcher and service files; data root left in place: %s\n' "$install_root"
