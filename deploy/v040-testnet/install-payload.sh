#!/bin/sh
set -eu

SRC="${1:-}"
DEST="${2:-/opt/hashburst-tep-testnet}"

if [ -z "$SRC" ] || [ ! -d "$SRC" ]; then
  echo "source directory required" >&2
  exit 64
fi

test "$(id -u)" -eq 0
test "$DEST" = "/opt/hashburst-tep-testnet"
test -d /var/lib/hashburst-testnet
test "$(stat -c '%U:%G:%a' /var/lib/hashburst-testnet)" = "hashburst-testnet:hashburst-testnet:700"

for rel in tools/testnet_peer_v040.py tools/testnet_multihost_probe_v040.py deploy/systemd/hashburst-tep-testnet.service deploy/v040-testnet/PROVENANCE; do
  test -f "$SRC/$rel"
done

grep -Fxq 'PROTOCOL_BASELINE=a97a17833074e9e44820fe8e90c151e8b22f37ad' "$SRC/deploy/v040-testnet/PROVENANCE"
grep -Fxq 'MULTIHOST_TOOLING_BASELINE=0194b15f01c19d32765b804bc10d5f76da1e890c' "$SRC/deploy/v040-testnet/PROVENANCE"

stage="$(mktemp -d /opt/.hashburst-tep-testnet.XXXXXX)"
trap 'rm -rf "$stage"' EXIT HUP INT TERM

install -d -m 0755 "$stage/tools" "$stage/deploy/systemd" "$stage/deploy/v040-testnet"
install -m 0644 "$SRC/tools/testnet_peer_v040.py" "$stage/tools/testnet_peer_v040.py"
install -m 0644 "$SRC/tools/testnet_multihost_probe_v040.py" "$stage/tools/testnet_multihost_probe_v040.py"
install -m 0644 "$SRC/deploy/systemd/hashburst-tep-testnet.service" "$stage/deploy/systemd/hashburst-tep-testnet.service"
install -m 0644 "$SRC/deploy/v040-testnet/PROVENANCE" "$stage/deploy/v040-testnet/PROVENANCE"

python3 -m venv --system-site-packages "$stage/venv"
"$stage/venv/bin/python" - <<'PY'
import cryptography
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
assert Ed25519PrivateKey.generate()
print("cryptography=" + cryptography.__version__)
PY

printf '%s\n' "${DEPLOYMENT_REVISION:-unknown}" > "$stage/deploy/v040-testnet/DEPLOYMENT_REVISION"

if [ -e "$DEST/venv" ] || [ -e "$DEST/tools/testnet_peer_v040.py" ]; then
  echo "existing payload detected; refusing destructive replacement" >&2
  exit 65
fi

cp -a "$stage/." "$DEST/"
chown -R root:root "$DEST"
chmod 0755 "$DEST" "$DEST/tools" "$DEST/deploy" "$DEST/deploy/systemd" "$DEST/deploy/v040-testnet"
install -m 0644 "$DEST/deploy/systemd/hashburst-tep-testnet.service" /etc/systemd/system/hashburst-tep-testnet.service
systemctl daemon-reload

echo "PAYLOAD_INSTALL_OK"
