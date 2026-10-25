#!/usr/bin/env zsh
# Run once; failures are returned to the caller. Training is opt-in research.
set -eu
if (( $# < 1 )) || [[ ! -f "$1" ]]; then
  print -u2 'Usage: src/run_qyoo_train.zsh /absolute/path/to/dataset.yaml [yolo options...]'
  exit 2
fi
dataset_config="${1:A}"
shift
exec yolo task=segment mode=train model=yolov8n-seg.pt \
  "data=$dataset_config" imgsz=512 epochs=120 batch=8 \
  "device=${QYOO_TRAIN_DEVICE:-cpu}" workers=0 cache=False \
  project=.codex-work/training name=qyoo_research "$@"
