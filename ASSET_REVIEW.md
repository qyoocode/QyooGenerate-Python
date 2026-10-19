# Asset provenance and recoverable cleanup proposal

Status: owner/legal review required. No tracked artifact was removed, relocated,
or re-licensed by the publication audit. Ignore rules prevent new accidental
artifacts; they do not untrack existing files or change history.

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
2. Quarantine the tracked Xcode `xcuserdata` trees and all tracked `.DS_Store`
   files with original paths and a manifest. They expose local editor state and
   are unnecessary to build; history still retains them.
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
