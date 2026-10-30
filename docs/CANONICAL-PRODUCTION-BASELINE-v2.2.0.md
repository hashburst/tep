# Canonical TEP v2.2 Production Baseline

The canonical executable baseline for migration is the TEP tree deployed at /opt/hashburst-tep on observer 64.31.4.9.

Observer evidence established:

- hashburst-tep.service runs python3 -m tep.hb_tep_runtime_v220 from the deployed TEP environment.
- all 12 tracked files under /opt/hashburst-tep/tep are SHA-256 identical to legacy/node-installer-v2.2.0/tep imported from hashburst/node-installer commit 034d29603a5dcd4d38bbcf403c31d0d2d7eb734a.
- the source repository history contains later hardening/evolution commits for selected TEP modules through 2026-09-20.
- /opt/node-installer-v220-blockchainapi/tep is a historical/deployment snapshot and diverges for selected files. It is retained as migration evidence, not promoted over the active canonical tree.

Therefore no GitHub source replacement is required: hashburst/tep already contains the exact currently observed production runtime baseline. Future migration work MUST preserve the divergent installer snapshot as historical evidence where captured, and MUST NOT overwrite the canonical baseline in legacy/.

This decision concerns provenance and migration baseline only. It does not declare every v2.2 behavior normative for TEP v0.2.0-rc1.
