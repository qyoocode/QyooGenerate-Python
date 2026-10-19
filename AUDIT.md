# Python generator publication audit

Inspected public main `17d42e7390549a2271811d156e05aca4ac57521f`.
Classification: research/reference rendering and localization data tools.
Verdict: research documentation and generation tests prepared; asset/model rights
and the unfinished Core ML demonstration block a fully cleared publication.

## Findings and changes

- HIGH — `iOS/QyooDemo/SegmentationCoordinator.swift:21`: target calls a generated
  `best` model class but the tracked app model is `SegOnly.mlpackage`; its tracked
  package also lacks the weight binary. Vision expects `VNPixelBufferObservation`
  without proven matching model outputs. Force unwraps, fixed `.right` orientation,
  unguarded camera setup and byte-stride assumptions remain historical limitations.
  README no longer promotes it as a shipping detector. Device/build qualification
  is NOT RUN; no successful inference or decoding claim is made.
- HIGH — photo/model provenance: no tracked rights manifest for photographs,
  derivatives, checkpoints or pretrained model. Eight `.pt` files total about
  107 MB before other artifacts. [ASSET_REVIEW.md](ASSET_REVIEW.md) proposes an exact
  recoverable retention/rights review; no artifact has been deleted or relocated.
- MEDIUM — `src/dataset.yaml:1`, `runs/segment/train_full/args.yaml:105` contained
  developer absolute paths; current metadata is portable and the launcher requires
  an explicit generated dataset configuration. Old values remain in Git history.
- MEDIUM — old training launcher retried failures indefinitely and assumed MPS,
  an existing resume checkpoint and local paths. It now executes once with explicit
  dataset input, returns failure status and supports explicit YOLO overrides. A stub
  test reproduced the old ignored-input/resume behavior before remediation.
- MEDIUM — `src/generate_qyoo_synthetic.py` old labels include bbox fields before
  polygons and lack full reproducibility metadata. Preserved as historical utility;
  README directs segmentation work to `build_localization_dataset.py`.
- MEDIUM — tracked Xcode user state and `.DS_Store` remain pending the asset cleanup
  proposal. Added ignore rules; cleared machine-specific Xcode signing-team defaults.
- MEDIUM — no dependency pinning or CI existed. Added generation-only exact pins
  matching the available validation environment and a generation CI workflow.
  Training/export stack remains explicitly unpinned and unqualified. No expensive
  training or export ran.
- LOW — removed help-request introduction and internal-task phrasing from public
  introduction; preserved useful algorithm comments, tests and history.

## Compatibility

All rendering profiles serialize the same 36 row-major MSB-first bits. The current
web profile has a 204-unit carrier, 26-unit quiet zone and 256-unit opaque export;
Python `historical_svg_204` renders the carrier alone with randomized colors and
transparent outside pixels. Other profiles differ in geometry. Existing 95-pattern
and single-cell tests exercise cell placement in all four profiles; they are not a
camera detector benchmark. Manifest v1, link routing, native actions, AR and Registry
ownership belong to other implementations, not this generator/model.

## Exposure and provenance review

Reviewed eleven public-main commits, tracked text, project configuration, model
package file inventories, samples and dependency imports. Redacted pattern scanning
included public-main reachable blobs, including binary/model blobs, for PEM private
keys, common GitHub/AWS/Slack/Google/Stripe credentials and literal private-key
assignments. No credential matches were found. Developer paths were confirmed and
sanitized in current text only. This is a bounded review, not a guarantee about
unknown formats, remote deleted refs or credentials in an opaque model payload.

Sample photos 1–4 contain camera/capture metadata but no GPS tag in inspected EXIF;
metadata values were not logged. Photo permission and people/brand-image rights
require owner review. No weight/checkpoint was loaded or unpickled.
Original BSD-3-Clause license and copyright are preserved; they do not establish
rights in Pexels photographs, Ultralytics weights or derivative training images.

## Exact verification commands

From workspace root, using an existing Python 3.14.7 environment with Pillow12.3.0,
NumPy2.5.3 and opencv-python-headless5.0.0.93 (no dependency installation):

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .codex-work/public-repo-audit/QyooGenerate-Python/tests -p test_training_command.py -v`
  — initial FAIL: launcher ignored explicit dataset and forced resume; then PASS.
- `PYTHONDONTWRITEBYTECODE=1 Qyoo-Web/.codex-work/launch-audit/python-env/bin/python -m unittest discover -s .codex-work/public-repo-audit/QyooGenerate-Python/tests -v`
  — PASS: 13 tests, including single-cell/95-pattern placement, complete split-safe
  dataset, deterministic artifact hashes, overwrite refusal, launcher arguments,
  failure propagation and missing dataset rejection. Inputs are procedural test
  images; no unclear photograph is required.
- `git diff --check` — PASS.
- Fresh pip installation / Linux GitHub CI — NOT RUN; pins match the reused macOS
  environment. CI uses Python3.14 and is prepared but not executed.
- Xcode build, physical camera, Core ML inference/export, model training — NOT RUN;
  incomplete model/interface and storage-heavy build limits; not a qualified demo.

Outputs remain below 10 MiB in ignored `.codex-work/`. No project material was
permanently deleted, quarantined or copied in bulk. Historical checkpoints were
left in the original checkout and omitted from this sparse audit worktree.
