#!/usr/bin/env python3
"""Focused reproducibility and split-safety tests for Task 06 dataset generation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import cv2


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "src/build_localization_dataset.py"
BACKGROUNDS = ROOT / "src/backgrounds"


class LocalizationDatasetTests(unittest.TestCase):
    def build(self, output: Path):
        subprocess.run([
            sys.executable, str(BUILDER), "--output", str(output),
            "--background-dir", str(BACKGROUNDS),
            "--family-train-positive", "3", "--historical-train-positive", "3",
            "--train-negative", "2", "--development-positive", "3",
            "--development-negative", "2", "--sealed-positive", "3",
            "--sealed-negative", "2",
        ], check=True, capture_output=True, text=True)
        return json.loads((output / "manifest.json").read_text())

    def test_tiny_dataset_is_complete_and_split_safe(self):
        with tempfile.TemporaryDirectory(prefix="qyoo-task06-dataset-") as directory:
            root = Path(directory)
            manifest = self.build(root)
            self.assertEqual(manifest["sample_count"], 20)
            payloads = {
                role: {sample["expected"]["payload_bits"] for sample in manifest["samples"]
                       if sample["split"] == role and sample["expected"]["present"]}
                for role in ("train_family", "train_historical", "development", "sealed_test")
            }
            self.assertEqual(payloads["train_family"], payloads["train_historical"])
            self.assertFalse(payloads["development"] & (payloads["train_family"] | payloads["train_historical"]))
            self.assertFalse(payloads["sealed_test"] & (payloads["train_family"] |
                                                         payloads["train_historical"] |
                                                         payloads["development"]))
            source_sets = [
                {item["sha256"] for item in manifest["background_source_roles"][role]}
                for role in ("train_family", "development", "sealed_test")
            ]
            self.assertFalse(source_sets[0] & source_sets[1])
            self.assertFalse(source_sets[0] & source_sets[2])
            self.assertFalse(source_sets[1] & source_sets[2])
            for sample in manifest["samples"]:
                image = Path(sample["image"]["path"])
                mask = Path(sample["segmentation_mask"]["path"])
                label = Path(sample["yolo_label"]["path"])
                self.assertEqual(cv2.imread(str(image)).shape[:2], (512, 512))
                mask_pixels = cv2.imread(str(mask), cv2.IMREAD_GRAYSCALE)
                if sample["expected"]["present"]:
                    self.assertGreater(cv2.countNonZero(mask_pixels), 0)
                    values = label.read_text().split()
                    self.assertEqual(values[0], "0")
                    self.assertEqual((len(values) - 1) % 2, 0)
                else:
                    self.assertEqual(cv2.countNonZero(mask_pixels), 0)
                    self.assertEqual(label.read_text(), "")

    def test_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="qyoo-task06-dataset-") as directory:
            root = Path(directory)
            (root / "existing").write_text("authority")
            process = subprocess.run(
                [sys.executable, str(BUILDER), "--output", str(root)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(process.returncode, 0)
            self.assertEqual((root / "existing").read_text(), "authority")

    def test_tiny_dataset_reproduces_exact_artifact_hashes(self):
        with tempfile.TemporaryDirectory(prefix="qyoo-task06-dataset-a-") as first_directory, \
             tempfile.TemporaryDirectory(prefix="qyoo-task06-dataset-b-") as second_directory:
            first = self.build(Path(first_directory))
            second = self.build(Path(second_directory))
            first_hashes = [(sample["sample_id"], sample["image"]["sha256"],
                             sample["segmentation_mask"]["sha256"],
                             sample["yolo_label"]["sha256"]) for sample in first["samples"]]
            second_hashes = [(sample["sample_id"], sample["image"]["sha256"],
                              sample["segmentation_mask"]["sha256"],
                              sample["yolo_label"]["sha256"]) for sample in second["samples"]]
            self.assertEqual(first_hashes, second_hashes)


if __name__ == "__main__":
    unittest.main()
