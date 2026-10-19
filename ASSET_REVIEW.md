# Asset provenance and recoverable cleanup proposal

Status: owner/legal review required. Models/photographs were not removed, relocated or re-licensed. The continuation
excludes Xcode user state and .DS_Store entries from the proposed Git tip using
index-only changes; all original bytes remain in the original checkout and Git
history. Ignore rules prevent recurrence. No filesystem deletion occurred.

## Rights review

- `samples/1.jpg` through `4.jpg`: photograph and derivative annotations; no
  photographer permission, subject release, or license record is tracked.
- `samples/000004*.jpg`: synthetic examples; source background provenance is
  not recorded, so generated status alone is insufficient clearance.
- Eight `src/backgrounds/pexels-photo-*.jpg`: filenames suggest Pexels, but original
  contributor, download date, license snapshot and asset identity are unverified.
  [Pexels license](https://www.pexels.com/license/) is a starting point, not proof
  that these exact files may be redistributed in this repository.
- `runs/segment/**`: checkpoints and derived training images need the provenance
  of the base model and input assets. BSD-3-Clause covers original repository
  software, not automatically these dependencies. Review the
  [Ultralytics licensing terms](https://www.ultralytics.com/license) before reuse.
- `iOS/QyooDemo/SegOnly.mlpackage`: model metadata exists but the tracked package
  does not contain its weight binary. The Vision coordinator instantiates a
  generated `best` class while the target contains `SegOnly`; no working demo is
  established. The separate `runs/.../best.mlpackage` is not the app target.

## Proposed action, pending owner approval

1. Establish an asset manifest with exact source URLs, authors, licenses, dates,
   checksums and derivative rights; replace unclear examples only after approval.
2. Completed forward metadata exclusion: Xcode `xcuserdata` and `.DS_Store`
   are no longer tracked in the proposed branch tip. Original checkout files
   and historical Git blobs are retained and hash-verified; no move, deletion or
   history rewrite occurred. Metadata retention evidence is in the workspace audit.
3. Review `runs/segment/train_full/weights/`: eight approximately 13.4 MB `.pt`
   checkpoints plus the Core ML model/weights. Keep one canonical research artifact
   only if licensing is established; propose a separate downloadable artifact with
   hash, generation metadata and license. The approximately 107 MB of checkpoint
   payloads stays intact until the owner selects a retention plan.
4. Preserve training metrics and unique reproducibility evidence. Do not erase
   public history, use force pushes or claim that a forward removal scrubs old
   clones. Any history restructuring requires a separate explicit decision.

For this workspace, approved removals would move to the central
`~/Documents/_dev/_remove_later` with original-path/date/reason manifest and copy
verification. No such operation has been performed. No ML training or model export
was run during the audit.

## Continuation: source-only checkpoint proposal

The eight `.pt` checkpoints contain embedded machine-specific training paths.
They are excluded from the proposed branch tip without loading, modifying,
relocating or deleting any checkpoint. Every original was byte/hash-verified in
the original checkout; the pinned public Git objects remain available in history.
[RESEARCH_ARTIFACTS.json](RESEARCH_ARTIFACTS.json) records exact objects, hashes,
sizes and the retained source revision. This is a reviewable forward publication
proposal; it does not scrub old public clones or establish artifact rights.

Do not redistribute these opaque checkpoints as clean BSD assets. Owner/legal
clearance and a portable reproducibility/weights manifest are still needed for any
future release artifact. To inspect an approved historical checkpoint, retrieve
its exact recorded path from the pinned Git revision into local research scratch;
never execute or unpickle untrusted checkpoints merely to sanitize metadata.
Historical Core ML artifacts and unique metrics remain intact.
