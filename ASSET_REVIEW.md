# Asset distribution scope

The current distribution contains Qyoo-owned source under BSD-3-Clause, tests,
portable configuration and historical numeric metrics. Qyoo is maintained by
Pushplay LLC; existing copyright notices are unchanged.

## Excluded assets

The following have no verified redistribution provenance and are excluded from
the current Git tree, rather than blocking the source tools:

- `samples/`: photographs and synthetic examples whose background/derivative rights are unrecorded.
- `src/backgrounds/pexels-photo-*.jpg`: filenames alone do not establish the identity, contributor or license applicable to these exact files.
- Historical training/validation image outputs under `runs/`, including annotated photos and plot images.
- `.pt` checkpoints and `.mlpackage` model packages, including the unfinished iOS demonstration model.

[RESEARCH_ARTIFACTS.json](RESEARCH_ARTIFACTS.json) records exact historical blobs,
SHA-256 hashes and sizes. Original checkout bytes and Git objects were verified
and preserved; these are index-only forward exclusions, not file deletion or a
history rewrite. Ignore rules prevent routine reintroduction. Git clones can
still contain historical objects; current Git-tree archives exclude these assets.
No checkpoint was loaded, unpickled, trained or exported.

## Bounded rights check

The official [Pexels license](https://www.pexels.com/license/) permits broad photo
use but does not establish that these exact repository files came from Pexels
under that grant. The official [Ultralytics licensing page](https://www.ultralytics.com/license)
distinguishes AGPL and Enterprise terms; the repository does not contain a
verified base-model/training-data license record for its historical weights.
Both pages were checked on 2026-10-24. No grant or ownership is inferred from a
filename, model format, generated image or the repository's BSD license.

Generation tests use procedural backgrounds and need none of the excluded
assets. Users provide their own cleared photographs and independently licensed
models for optional research. Training CSV/configuration remains as historical
reproducibility evidence. The iOS source is unfinished reference material, without
a bundled model or claim of successful inference/decoding.
