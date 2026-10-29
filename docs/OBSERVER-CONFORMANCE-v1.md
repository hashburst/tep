# TEP Observer Conformance Probe v1

Read-only non-secret snapshot of a deployed TEP runtime and comparison with the immutable v2.2.0 legacy baseline.

## Safety boundary

The probe does not read private keys, PEM files, environment files, databases, SQLite files, peer-state files, anti-replay state, logs, or process environments. It does not restart, reload, signal, write to, or mutate services. systemd inspection requests only Id, state, FragmentPath and ExecStart.

IDENTICAL means exact SHA-256 equality. DIFFERENT means the module is observed but differs. NOT OBSERVABLE means it was not found. COMPATIBLE is never inferred from hashes and requires later behavioral interoperability testing.

## Observer command

Run from a checkout of hashburst/tep containing this probe:

    sudo python3 tools/tep_observer_probe_v1.py --output /tmp/tep-observer-v1.json && python3 tools/compare_observer_v1.py /tmp/tep-observer-v1.json > /tmp/tep-observer-conformance-v1.json && sha256sum /tmp/tep-observer-v1.json /tmp/tep-observer-conformance-v1.json

Retain both JSON files and their SHA-256 values. Review the JSON before transferring it off the observer.
