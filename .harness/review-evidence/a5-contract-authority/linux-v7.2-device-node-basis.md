# Linux v7.2 source basis for the plan v2.66 device-node case

Plan v2.66 criterion 1's device-node case says that in upstream Linux v7.2 `filename_mknodat`
calls the security hook before `vfs_mknod`'s `CAP_MKNOD` check. Two upstream files at tag `v7.2`
support that ordering: Landlock answers a character- or block-device `mknod` before the
capability check runs. This record pins those files so a reader can fetch and check them. It
publishes no kernel source beyond the anchor lines quoted below.

**Scope.** This is a reading of upstream source at the `v7.2` tag. It is not an observation of the
running Arch `7.2.6-1` kernel, whose build may carry patches, and no device node was created. It
changes no criterion; the plan's prerequisites and HELD conditions still apply.

## Pinned files

Retrieved 2026-10-02T10:45:15Z. SHA256 is of the whole file as served.

| File | URL | Bytes | SHA256 |
|---|---|---|---|
| `fs/namei.c` | <https://raw.githubusercontent.com/torvalds/linux/v7.2/fs/namei.c> | 179429 | `d5498d87be97efd71286e27a30c34ce92a5e059e37540de11e93d1b8aad36c4a` |
| `security/landlock/fs.c` | <https://raw.githubusercontent.com/torvalds/linux/v7.2/security/landlock/fs.c> | 65329 | `35b7514d1677e4e537eebf6a1ad747ebd137f263a12b705b2a3d8da81f8b0af0` |

## Anchors

Line numbers refer to the pinned files above.

`fs/namei.c`:

- 5159: `filename_mknodat` begins.
- 5177: it calls `security_path_mknod(...)`. A denial from this hook ends the call before any
  node operation.
- 5190: for `S_IFCHR` and `S_IFBLK` it then calls `vfs_mknod(...)`.
- 5115–5117: inside `vfs_mknod`, a character or block device (other than a whiteout) without
  `capable(CAP_MKNOD)` returns `-EPERM`.

`security/landlock/fs.c`:

- 993–996: `get_mode_access` maps `S_IFCHR` to `LANDLOCK_ACCESS_FS_MAKE_CHAR` and `S_IFBLK` to
  `LANDLOCK_ACCESS_FS_MAKE_BLOCK`. Landlock's `mknod` hook checks that access right
  (`hook_path_mknod`, 1543–1547).

So the security hook at 5177 decides before the capability check at 5115–5117 is reached through
5190. A handled `MAKE_CHAR` or `MAKE_BLOCK` right outside the grants refuses first. An
unhandled one lets the call reach the capability check, which returns `-EPERM` without `CAP_MKNOD`. This matches the `EACCES` and `EPERM` pair the
plan's case asserts.

**Provenance.** The retrieval record `unit6-pass2-kernel-source/provenance.json` (SHA256
`680f0d86ec973b9a96b4c25174f4ff085d436d4c510c6cfa3eb326eb316aed33`) is retained at the root
orchestration checkout, under
`.local/24h-acceptance/buford-workflow-optimization-20261002/parallel-resume/`. It carries the URLs,
byte counts and hashes above. The two whole files stay there and are not published here.
