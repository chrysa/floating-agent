#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
data_home="${XDG_DATA_HOME:-$HOME/.local/share}"
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
bin_home="${XDG_BIN_HOME:-$HOME/.local/bin}"
state_home="${XDG_STATE_HOME:-$HOME/.local/state}"

install_root="$data_home/floating-agent"
venv_dir="$install_root/venv"
desktop_dir="$data_home/applications"
systemd_dir="$config_home/systemd/user"
config_dir="$config_home/floating-agent"
launcher="$bin_home/floating-agent"
desktop_file="$desktop_dir/floating-agent.desktop"
service_file="$systemd_dir/floating-agent.service"
env_file="$config_dir/install.env"
manifest_file="$install_root/install-manifest.json"
desktop_template="$repo_root/packaging/desktop/floating-agent.desktop"
service_template="$repo_root/packaging/systemd/floating-agent.service"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'missing dependency: %s\n' "$1" >&2
    exit 1
  fi
}

require_command uv

mkdir -p "$install_root" "$desktop_dir" "$systemd_dir" "$config_dir" "$bin_home" "$state_home/floating-agent"

UV_PROJECT_ENVIRONMENT="$venv_dir" uv sync --frozen

cat >"$launcher" <<EOF
#!/usr/bin/env bash
set -euo pipefail
exec "$venv_dir/bin/floating-agent" "\$@"
EOF
chmod 755 "$launcher"

install -Dm644 "$desktop_template" "$desktop_file"
install -Dm644 "$service_template" "$service_file"

cat >"$env_file" <<EOF
FLOATING_AGENT_REPO_ROOT=$repo_root
FLOATING_AGENT_INSTALL_ROOT=$install_root
FLOATING_AGENT_VENV=$venv_dir
EOF

cat >"$manifest_file" <<EOF
{
  "repo_root": "$repo_root",
  "install_root": "$install_root",
  "venv_dir": "$venv_dir",
  "launcher": "$launcher",
  "desktop_file": "$desktop_file",
  "service_file": "$service_file"
}
EOF

printf 'installed launcher: %s\n' "$launcher"
printf 'desktop file: %s\n' "$desktop_file"
printf 'systemd user service: %s\n' "$service_file"
printf 'run: %s --doctor\n' "$launcher"
