#!/usr/bin/env python3
"""Prove named Qyoo geometry and preserve pre-Task 06 Python output."""

from __future__ import annotations

import hashlib
import json
import random
import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from generate_qyoo_synthetic import render_qyoo  # noqa: E402
from geometry_profiles import GEOMETRY_PROFILES  # noqa: E402


class GeometryProfileTests(unittest.TestCase):
    def render(self, profile: str, bits: str, seed: int = 20260828):
        random.seed(seed)
        np.random.seed(seed)
        return render_qyoo(bits, geometry_profile=profile)[0]

    def test_legacy_profile_is_byte_for_byte_compatible_in_rgba(self):
        fixtures = json.loads((Path(__file__).parent / "legacy_geometry_known_answers.json").read_text())
        for case in fixtures["cases"]:
            with self.subTest(seed=case["seed"]):
                image = self.render("legacy_python", case["bits"], case["seed"])
                self.assertEqual(image.size, (256, 256))
                self.assertEqual(hashlib.sha256(image.tobytes()).hexdigest(), case["rgba_sha256"])
                self.assertEqual(
                    hashlib.sha256(image.getchannel("A").tobytes()).hexdigest(),
                    case["alpha_sha256"],
                )

    def test_default_is_legacy_profile(self):
        bits = "101111101010011110111010111001101100"
        random.seed(17)
        default = render_qyoo(bits)[0]
        random.seed(17)
        named = render_qyoo(bits, geometry_profile="legacy_python")[0]
        self.assertEqual(default.tobytes(), named.tobytes())

    def test_evidence_backed_measurements(self):
        expected = {
            "legacy_python": (256, 256, 128, (48, 208), 32, 12),
            "historical_svg_204": (204, 204, 102, (39, 164), 25, 10),
            "c_like_512": (512, 256, 128, (179, 329), 30, 13),
            "php_like_512": (512, 256, 128, (178.75, 329.5), None, 13.25),
        }
        for name, (canvas, diameter, square, endpoints, spacing, radius) in expected.items():
            with self.subTest(profile=name):
                metadata = GEOMETRY_PROFILES[name].output_metadata()
                self.assertEqual(metadata["canvas_size"], canvas)
                self.assertAlmostEqual(metadata["carrier_diameter"], diameter)
                self.assertAlmostEqual(metadata["square_right"] - metadata["square_left"], square)
                self.assertAlmostEqual(metadata["dot_centers_x"][0], endpoints[0])
                self.assertAlmostEqual(metadata["dot_centers_x"][-1], endpoints[1])
                if spacing is not None:
                    self.assertTrue(all(
                        abs((right - left) - spacing) < 1e-9
                        for left, right in zip(metadata["dot_centers_x"], metadata["dot_centers_x"][1:])
                    ))
                self.assertAlmostEqual(metadata["dot_radius"], radius)

    def test_every_visual_cell_changes_only_its_named_center(self):
        for profile_name, profile in GEOMETRY_PROFILES.items():
            zero = self.render(profile_name, "0" * 36)
            metadata = profile.output_metadata()
            zero_pixels = np.asarray(zero)
            for index in range(36):
                with self.subTest(profile=profile_name, index=index):
                    bits = "0" * index + "1" + "0" * (35 - index)
                    one = np.asarray(self.render(profile_name, bits))
                    row, column = divmod(index, 6)
                    x = round(metadata["dot_centers_x"][column])
                    y = round(metadata["dot_centers_y"][row])
                    self.assertFalse(np.array_equal(one[y, x], zero_pixels[y, x]))

    def test_task02_95_case_payload_placement_for_every_profile(self):
        generator = random.Random(20260828)
        patterns = [
            0,
            1,
            (1 << 36) - 1,
            0,
            (1 << 36) - 1,
            int("01" * 18, 2),
            int("10" * 18, 2),
        ]
        patterns.extend(1 << (35 - index) for index in range(36))
        patterns.extend(((1 << 36) - 1) ^ (1 << (35 - index)) for index in range(36))
        patterns.extend(generator.getrandbits(36) for _ in range(16))
        self.assertEqual(len(patterns), 95)

        for profile_name, profile in GEOMETRY_PROFILES.items():
            metadata = profile.output_metadata()
            for case_index, value in enumerate(patterns):
                bits = f"{value:036b}"
                seed = 991 + case_index
                zero = np.asarray(self.render(profile_name, "0" * 36, seed=seed))
                random.seed(seed)
                np.random.seed(seed)
                image, returned = render_qyoo(bits, geometry_profile=profile_name)
                self.assertEqual(returned, bits)
                pixels = np.asarray(image)
                observed = []
                for index in range(36):
                    row, column = divmod(index, 6)
                    x = round(metadata["dot_centers_x"][column])
                    y = round(metadata["dot_centers_y"][row])
                    observed.append("1" if not np.array_equal(pixels[y, x], zero[y, x]) else "0")
                with self.subTest(profile=profile_name, case=case_index):
                    self.assertEqual("".join(observed), bits)

    def test_invalid_bits_and_profile_are_rejected(self):
        for bits in ("0" * 35, "0" * 35 + "x", "0" * 37):
            with self.assertRaises(ValueError):
                render_qyoo(bits)
        with self.assertRaises(ValueError):
            render_qyoo("0" * 36, geometry_profile="not_a_profile")


if __name__ == "__main__":
    unittest.main()
