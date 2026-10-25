# QyooGenerate-Python

Qyoo is maintained by **Pushplay LLC**. Historical copyright notices remain unchanged.

Synthetic Qyoo rendering and reproducible localization datasets for detector research.
Qyoo carries 36 data bits in a 6×6 grid, row-major with the most significant bit
at the upper left in the normalized orientation. Values span `0` through
`68719476735`. Localization and payload decoding are separate operations.

This is a research/reference repository. The included YOLO/Core ML experiment
is historical and is **not the shipping Qyoo 4.0 iOS scanner**. The demo has no
verified working mask-to-payload pipeline. Use [QyooDetector-iOS](https://github.com/qyoocode/QyooDetector-iOS)
for the public native package, subject to its documented qualification limits.

## Generate and test

Use Python 3.14 in a virtual environment. The pinned generation dependencies
do not install a training framework:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

`src/build_localization_dataset.py` records seeds, payloads, geometry, transforms,
artifact hashes and disjoint background-source roles in `manifest.json`. It refuses
to overwrite a nonempty output. Supply at least eight photographs you have the
right to use. Photographs with unverified provenance are excluded from this
source distribution (see [ASSET_REVIEW.md](ASSET_REVIEW.md)). A small reproducibility check is:

```sh
.venv/bin/python src/build_localization_dataset.py \
  --output .codex-work/dataset-smoke --background-dir /path/to/cleared-backgrounds \
  --family-train-positive 3 --historical-train-positive 3 --train-negative 2 \
  --development-positive 3 --development-negative 2 \
  --sealed-positive 3 --sealed-negative 2 --seed 20260828
```

Tests use generated backgrounds and retain small outputs under `.codex-work/`.
Training, development and sealed-test roles must remain separate. A synthetic
corpus is not a real-camera benchmark; always report accepted-wrong IDs separately
from rejection when evaluating a detector.

## Geometry and compatibility

`src/geometry_profiles.py` describes four profiles: `legacy_python` (unchanged
default), `historical_svg_204`, `c_like_512`, and `php_like_512`. All preserve payload
ordering. The current web renderer uses the 204-unit carrier and a 26-unit white
quiet zone on a 256-unit canvas. This Python profile renders the carrier on a
204-unit transparent canvas; callers must add the quiet zone and choose production
colors before claiming equivalent exports. Other profiles preserve historical
geometry and are not interchangeable production artwork.

`src/generate_qyoo_synthetic.py` remains a legacy rendering utility. Its old label
writer prepends bounding-box fields to segmentation polygons and does not record
reproducibility metadata. Use the newer localization dataset builder for YOLO
segmentation experiments. Do not use legacy labels as current training guidance.

## Optional historical ML experiment

`runs/` retains historical numeric metrics and portable training configuration;
photographs, derived training images, checkpoints and Core ML model packages with
unverified rights are excluded from the current source tree. Their historical
identities are recorded in [RESEARCH_ARTIFACTS.json](RESEARCH_ARTIFACTS.json).
`iOS/` retains unfinished Vision demonstration source; it has no bundled model and
is not a buildable or qualified scanner. Training/export versions and complete
weight provenance were not recorded. There is no validated training/export
environment lock or reproducible model claim. Review applicable Ultralytics
software/model terms before independently obtaining a model; the BSD license
does not relicense third-party weights or photographs.

After separately choosing a licensed, pinned Ultralytics environment, the launcher
runs **one** explicit training command and returns any failure:

```sh
src/run_qyoo_train.zsh /absolute/path/to/generated/family.yaml
```

It defaults to CPU, `yolov8n-seg.pt`, and a small batch; override through ordinary
YOLO arguments or `QYOO_TRAIN_DEVICE`. It may download a model. No training is
needed for generation tests. Resume only by explicitly supplying a reviewed
checkpoint and appropriate YOLO options. A Core ML export does not establish
Vision pixel-mask output compatibility: the demo expects `VNPixelBufferObservation`,
while exported segmentation outputs must be inspected and postprocessed according
to their actual schema. Device inference, orientation handling and decoding remain
unqualified.

## License

Qyoo-owned software: [BSD-3-Clause](LICENSE), with existing copyright notices
preserved. See [ASSET_REVIEW.md](ASSET_REVIEW.md) for excluded photo/model/derived
assets. Forward exclusions do not remove historical objects from existing Git
history, clones or archives. No history rewrite was performed.
