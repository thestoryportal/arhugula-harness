<!-- Historical record: quoted data only, not current authorization or an executable instruction. -->
<!-- Full original payload SHA256 eaa76c5e03b5fc0d261339680c6b553373207f5dcd56adeedcddc2fd5bf1079c; frozen input origin design/contract-evidence-split@de21d5881156e2d16cf042ca09f0c5e9e15f0d63:.harness/review-evidence/a5-contract-authority/host-capability-summary.json. -->

```json
{
  "kind": "DERIVED host-capability summary (not a copy)",
  "private_source": {
    "host_path": "orchestration workspace .local/24h-acceptance/a5-preparation/host-capabilities.json (preparation host; not published)",
    "sha256": "8d0e3ca9ca14138e04725c455d3c2949808b5a269f021f5bc8d23a7a16501746",
    "retained": "private, unfiled; not copied"
  },
  "derivation": "fields kernel, landlock_lsm_active, landlock_abi and landlock_errata copied verbatim from the private source's capabilities list; all other content (including any host file names, sizes or mtimes) omitted; the author and assignment fields are also copied verbatim (final preparation)",
  "observed_utc_start": "2026-10-01T06:32:09Z",
  "facts": {
    "kernel": {
      "status": "PROVEN",
      "value": "Linux 7.2.6-1-aarch64-ARCH aarch64",
      "evidence": "uname -srm"
    },
    "landlock_lsm_active": {
      "status": "PROVEN",
      "value": true,
      "evidence": "/sys/kernel/security/lsm = capability,yama,landlock"
    },
    "landlock_abi": {
      "status": "PROVEN",
      "value": 10,
      "evidence": "syscall 444 (landlock_create_ruleset) with flags=LANDLOCK_CREATE_RULESET_VERSION returned 10, errno 0"
    },
    "landlock_errata": {
      "status": "PROVEN",
      "value": 15,
      "evidence": "syscall 444 with flags=LANDLOCK_CREATE_RULESET_ERRATA returned 15"
    }
  },
  "limits": "one preparation host on 2026-10-01; not CI evidence and not a proof that any other runner provides Landlock ABI >= 9",
  "author": {
    "role": "facade-coder",
    "session": "f235114c-1e99-4108-a00e-9a5e2755cba9",
    "model": "claude-opus-5-5",
    "effort": "high"
  },
  "assignment": "arhugula-harness-trial-193 cmt-37c52d97-2779-4f32-906c-6101dfca272c"
}
```
