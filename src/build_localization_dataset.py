#!/usr/bin/env python3
"""Build the deterministic Task 06 Qyoo localization/segmentation dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from generate_qyoo_synthetic import render_qyoo
from geometry_profiles import GEOMETRY_PROFILES


CANVAS = 512
MASTER_SEED = 20260828
FAMILY_PROFILES = ("historical_svg_204", "c_like_512", "php_like_512")
PAYLOAD_KINDS = (
    "random", "sparse", "dense", "single_set", "single_cleared",
    "alternating_01", "alternating_10", "fixture",
)
FIXTURES = (
    "101111101010011110111010111001101100",
    "000000011110011110011110011110000000",
    "010101100010001011111110010101101010",
    "000000000000000001000000000000000000",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_commit(root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=True
    ).stdout.strip()


def unique_payload(kind: str, rng: random.Random, index: int, used: set[str]) -> str:
    for attempt in range(1000):
        if kind == "sparse":
            count = rng.randint(1, 6)
            value = sum(1 << bit for bit in rng.sample(range(36), count))
        elif kind == "dense":
            count = rng.randint(30, 35)
            cleared = set(rng.sample(range(36), 36 - count))
            value = sum(1 << bit for bit in range(36) if bit not in cleared)
        elif kind == "single_set":
            value = 1 << ((index + attempt) % 36)
        elif kind == "single_cleared":
            value = ((1 << 36) - 1) ^ (1 << ((index + attempt) % 36))
        elif kind == "alternating_01":
            value = int("01" * 18, 2) ^ (1 << ((index + attempt) % 36) if attempt else 0)
        elif kind == "alternating_10":
            value = int("10" * 18, 2) ^ (1 << ((index + attempt) % 36) if attempt else 0)
        elif kind == "fixture":
            value = int(FIXTURES[index % len(FIXTURES)], 2) ^ (
                1 << ((index + attempt) % 36) if attempt else 0
            )
        else:
            value = rng.getrandbits(36)
        bits = f"{value:036b}"
        if bits not in used:
            used.add(bits)
            return bits
    raise RuntimeError("unable to allocate a unique 36-bit payload")


def photo_background(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"unable to load background {path}")
    return cv2.cvtColor(cv2.resize(image, (CANVAS, CANVAS), interpolation=cv2.INTER_CUBIC),
                        cv2.COLOR_BGR2RGB)


def procedural_background(rng: random.Random, category: str) -> np.ndarray:
    image = Image.new("RGB", (CANVAS, CANVAS), tuple(rng.randint(35, 220) for _ in range(3)))
    draw = ImageDraw.Draw(image)
    if category == "architecture":
        for x in range(-CANVAS, CANVAS * 2, rng.randint(24, 52)):
            draw.line((x, 0, x + rng.randint(-180, 180), CANVAS),
                      fill=tuple(rng.randint(0, 255) for _ in range(3)), width=rng.randint(2, 8))
        for y in range(0, CANVAS, rng.randint(28, 60)):
            draw.line((0, y, CANVAS, y + rng.randint(-25, 25)), fill=(30, 30, 30), width=3)
    elif category == "printed_material":
        for y in range(18, CANVAS - 10, 18):
            width = rng.randint(100, 480)
            draw.rectangle((rng.randint(8, 35), y, width, y + rng.randint(2, 6)), fill=(20, 20, 20))
        for _ in range(10):
            x, y = rng.randint(0, 460), rng.randint(0, 460)
            draw.rectangle((x, y, x + rng.randint(20, 90), y + rng.randint(20, 90)),
                           outline=(0, 0, 0), width=rng.randint(2, 8))
    elif category == "ui":
        draw.rectangle((0, 0, CANVAS, 54), fill=(28, 31, 38))
        for index in range(12):
            x = 24 + (index % 4) * 122
            y = 78 + (index // 4) * 132
            draw.rounded_rectangle((x, y, x + 96, y + 102), radius=12,
                                   fill=tuple(rng.randint(100, 245) for _ in range(3)))
            draw.ellipse((x + 28, y + 15, x + 68, y + 55), outline=(30, 30, 30), width=4)
    elif category == "texture":
        pixels = np.random.default_rng(rng.getrandbits(64)).normal(128, 52, (CANVAS, CANVAS, 3))
        return np.clip(pixels, 0, 255).astype(np.uint8)
    else:
        for _ in range(90):
            x, y = rng.randint(0, CANVAS), rng.randint(0, CANVAS)
            radius = rng.randint(2, 45)
            color = tuple(rng.randint(0, 255) for _ in range(3))
            if rng.random() < 0.5:
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=color,
                             width=rng.randint(1, 7))
            else:
                draw.rectangle((x - radius, y - radius, x + radius, y + radius), outline=color,
                               width=rng.randint(1, 7))
    return np.asarray(image)


def hard_negative(rng: random.Random, category: str, photo: Path | None) -> np.ndarray:
    if photo is not None and category in {"natural", "texture"}:
        image = Image.fromarray(photo_background(photo))
    else:
        image = Image.fromarray(procedural_background(rng, category))
    draw = ImageDraw.Draw(image)
    if category == "circle_square":
        for _ in range(8):
            x, y = rng.randint(40, 472), rng.randint(40, 472)
            r = rng.randint(18, 55)
            draw.ellipse((x - r, y - r, x + r, y + r), outline=(0, 0, 0), width=6)
            sx = min(480, x + r + 25)
            draw.rectangle((sx, y - r, min(510, sx + 2 * r), y + r), outline=(0, 0, 0), width=6)
    elif category == "dot_grid":
        for block in range(3):
            ox, oy = rng.randint(10, 250), rng.randint(10, 250)
            spacing = rng.randint(20, 42)
            for row in range(6):
                for column in range(6):
                    if rng.random() < 0.72:
                        r = rng.randint(3, 9)
                        x, y = ox + column * spacing, oy + row * spacing
                        draw.ellipse((x-r, y-r, x+r, y+r), fill=(0, 0, 0))
    elif category in {"qr_like", "data_matrix_like"}:
        modules = rng.choice((17, 21, 25))
        size = rng.randint(180, 390)
        x0, y0 = rng.randint(5, CANVAS-size-5), rng.randint(5, CANVAS-size-5)
        module = size / modules
        for row in range(modules):
            for column in range(modules):
                value = ((row * 13 + column * 7 + rng.randint(0, 1)) % 3) == 0
                if value:
                    draw.rectangle((x0+column*module, y0+row*module,
                                    x0+(column+1)*module, y0+(row+1)*module), fill=(0, 0, 0))
    elif category == "logos_icons":
        for _ in range(20):
            x, y = rng.randint(25, 487), rng.randint(25, 487)
            r = rng.randint(10, 35)
            draw.regular_polygon((x, y, r), n_sides=rng.randint(3, 8),
                                 outline=tuple(rng.randint(0, 100) for _ in range(3)), width=5)
    return np.asarray(image)


def convex_quad(rng: random.Random, scale: float, angle_degrees: float, severity: float,
                clipped: bool) -> np.ndarray:
    angle = math.radians(angle_degrees)
    rotation = np.array([[math.cos(angle), -math.sin(angle)],
                         [math.sin(angle), math.cos(angle)]], dtype=np.float32)
    base = np.array([[-.5, -.5], [.5, -.5], [.5, .5], [-.5, .5]], dtype=np.float32)
    rotated = (base * scale) @ rotation.T
    for _ in range(100):
        jitter = np.array([[rng.uniform(-severity, severity), rng.uniform(-severity, severity)]
                           for _ in range(4)], dtype=np.float32) * scale
        quad = rotated + jitter
        radius = float(np.max(np.linalg.norm(quad, axis=1)))
        if clipped or radius >= CANVAS / 2 - 4:
            # Permit frame-edge clipping while retaining a substantial visible region.
            center = np.array([rng.uniform(-0.25 * radius, CANVAS + 0.25 * radius),
                               rng.uniform(-0.25 * radius, CANVAS + 0.25 * radius)], dtype=np.float32)
        else:
            center = np.array([rng.uniform(radius + 4, CANVAS - radius - 4),
                               rng.uniform(radius + 4, CANVAS - radius - 4)], dtype=np.float32)
        candidate = quad + center
        contour = candidate.reshape((-1, 1, 2)).astype(np.float32)
        if cv2.isContourConvex(contour) and abs(cv2.contourArea(contour)) > scale * scale * 0.35:
            return candidate
    raise RuntimeError("unable to produce a convex destination quadrilateral")


def motion_kernel(length: int, angle: float) -> np.ndarray:
    kernel = np.zeros((length, length), dtype=np.float32)
    center = (length - 1) / 2
    radians = math.radians(angle)
    dx, dy = math.cos(radians) * center, math.sin(radians) * center
    cv2.line(kernel, (round(center - dx), round(center - dy)),
             (round(center + dx), round(center + dy)), 1.0, 1)
    total = float(kernel.sum())
    return kernel / total if total else np.eye(1, dtype=np.float32)


def apply_camera_effects(image: np.ndarray, rng: random.Random) -> tuple[np.ndarray, dict]:
    contrast = rng.uniform(0.45, 1.35)
    brightness = rng.uniform(-45, 45)
    image = np.clip(128 + contrast * (image.astype(np.float32) - 128) + brightness, 0, 255)
    gradient_start, gradient_end = rng.uniform(0.55, 1.15), rng.uniform(0.65, 1.30)
    gradient = np.linspace(gradient_start, gradient_end, CANVAS, dtype=np.float32)[None, :, None]
    image = np.clip(image * gradient, 0, 255)
    shadow = None
    if rng.random() < 0.35:
        shadow = {"x": rng.randint(0, CANVAS), "width": rng.randint(45, 180),
                  "factor": rng.uniform(0.35, 0.75)}
        x0 = max(0, shadow["x"] - shadow["width"] // 2)
        x1 = min(CANVAS, shadow["x"] + shadow["width"] // 2)
        image[:, x0:x1] *= shadow["factor"]
    blur_sigma = rng.choice((0.0, 0.0, 0.6, 1.2, 2.2, 3.5))
    if blur_sigma:
        image = cv2.GaussianBlur(image, (0, 0), blur_sigma)
    motion_length = rng.choice((0, 0, 0, 3, 5, 9))
    motion_angle = rng.uniform(0, 180)
    if motion_length:
        image = cv2.filter2D(image, -1, motion_kernel(motion_length, motion_angle))
    downsample = rng.choice((1.0, 1.0, 0.75, 0.55, 0.4))
    if downsample != 1.0:
        small = cv2.resize(image, None, fx=downsample, fy=downsample, interpolation=cv2.INTER_AREA)
        image = cv2.resize(small, (CANVAS, CANVAS), interpolation=cv2.INTER_LINEAR)
    noise_std = rng.choice((0.0, 0.0, 2.0, 5.0, 10.0, 18.0))
    if noise_std:
        noise = np.random.default_rng(rng.getrandbits(64)).normal(0, noise_std, image.shape)
        image = np.clip(image + noise, 0, 255)
    quality = rng.randint(38, 96)
    return image.astype(np.uint8), {
        "contrast": contrast, "brightness": brightness,
        "gradient": [gradient_start, gradient_end], "shadow": shadow,
        "gaussian_blur_sigma": blur_sigma,
        "motion_blur": {"length": motion_length, "angle_degrees": motion_angle},
        "resolution_scale": downsample, "noise_stddev": noise_std,
        "jpeg_quality": quality,
    }


def contour_label(mask: np.ndarray) -> tuple[str, list[list[float]]]:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return "", []
    contour = max(contours, key=cv2.contourArea)
    epsilon = 0.003 * cv2.arcLength(contour, True)
    points = cv2.approxPolyDP(contour, epsilon, True).reshape(-1, 2)
    if len(points) > 64:
        points = points[np.linspace(0, len(points) - 1, 64, dtype=int)]
    normalized = [[float(x) / CANVAS, float(y) / CANVAS] for x, y in points]
    label = "0 " + " ".join(f"{coordinate:.6f}" for point in normalized for coordinate in point)
    return label + "\n", normalized


def geometry_crop(image: Image.Image) -> tuple[Image.Image, list[int]]:
    alpha = np.asarray(image.getchannel("A"))
    ys, xs = np.nonzero(alpha > 0)
    bounds = [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]
    return image.crop(tuple(bounds)), bounds


def generate_positive(role: str, index: int, profile_name: str, seed: int,
                      photos: list[Path], used_payloads: set[str]) -> tuple[np.ndarray, np.ndarray, dict]:
    rng = random.Random(seed)
    random.seed(seed)
    np.random.seed(seed & 0xFFFFFFFF)
    payload_kind = PAYLOAD_KINDS[index % len(PAYLOAD_KINDS)]
    bits = unique_payload(payload_kind, rng, index, used_payloads)
    symbol, returned = render_qyoo(bits, geometry_profile=profile_name)
    if returned != bits:
        raise AssertionError("renderer returned different carrier bits")
    symbol, source_crop = geometry_crop(symbol)
    rgba = np.asarray(symbol)
    source_points = np.float32([[0, 0], [symbol.width - 1, 0],
                                [symbol.width - 1, symbol.height - 1], [0, symbol.height - 1]])
    scale = rng.uniform(52, 330)
    perspective_name, severity = rng.choice((("mild", .035), ("medium", .10), ("strong", .19)))
    requested_clipping = rng.random() < 0.18
    quad = convex_quad(rng, scale, rng.uniform(0, 360), severity, requested_clipping)
    clipped = bool(np.any(quad < 0) or np.any(quad[:, 0] >= CANVAS) or np.any(quad[:, 1] >= CANVAS))
    matrix = cv2.getPerspectiveTransform(source_points, quad.astype(np.float32))
    warped = cv2.warpPerspective(rgba, matrix, (CANVAS, CANVAS), flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    procedural_category = rng.choice(("architecture", "printed_material", "ui", "texture", "shapes"))
    photo = rng.choice(photos) if photos and rng.random() < .65 else None
    background = photo_background(photo) if photo else procedural_background(rng, procedural_category)
    alpha = warped[:, :, 3:4].astype(np.float32) / 255.0
    composed = warped[:, :, :3].astype(np.float32) * alpha + background.astype(np.float32) * (1 - alpha)
    visible_mask = (warped[:, :, 3] > 24).astype(np.uint8) * 255
    occlusion = None
    if rng.random() < .14:
        ys, xs = np.nonzero(visible_mask)
        if len(xs):
            width = max(4, int((xs.max() - xs.min()) * rng.uniform(.08, .25)))
            height = max(4, int((ys.max() - ys.min()) * rng.uniform(.08, .25)))
            x0 = rng.randint(max(0, int(xs.min())), max(0, int(xs.max()) - width + 1))
            y0 = rng.randint(max(0, int(ys.min())), max(0, int(ys.max()) - height + 1))
            composed[y0:y0+height, x0:x0+width] = background[y0:y0+height, x0:x0+width]
            occlusion = [x0, y0, width, height]
    composed, effects = apply_camera_effects(composed, rng)
    ys, xs = np.nonzero(visible_mask)
    if not len(xs):
        raise RuntimeError("positive carrier became fully invisible")
    bbox = [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]
    label, polygon = contour_label(visible_mask)
    metadata = {
        "present": True, "payload_bits": bits, "raw_integer": int(bits, 2),
        "payload_kind": payload_kind, "geometry_profile": profile_name,
        "source_geometry": GEOMETRY_PROFILES[profile_name].output_metadata(),
        "source_alpha_crop_xyxy": source_crop, "background_source": str(photo) if photo else procedural_category,
        "destination_quad_xy": quad.astype(float).tolist(), "source_to_image_homography": matrix.astype(float).tolist(),
        "bounding_box_xyxy": bbox, "mask_polygon_normalized": polygon,
        "clipped": clipped, "clipping_requested": requested_clipping,
        "occlusion_xywh": occlusion, "effects": effects,
    }
    return composed, visible_mask, metadata | {"yolo_label": label}


def generate_negative(role: str, index: int, seed: int, photos: list[Path]) -> tuple[np.ndarray, np.ndarray, dict]:
    rng = random.Random(seed)
    category = ("circle_square", "dot_grid", "qr_like", "data_matrix_like",
                "logos_icons", "architecture", "printed_material", "ui", "texture", "natural")[index % 10]
    photo = rng.choice(photos) if photos and category in {"natural", "texture"} else None
    image = hard_negative(rng, category, photo)
    image, effects = apply_camera_effects(image, rng)
    return image, np.zeros((CANVAS, CANVAS), dtype=np.uint8), {
        "present": False, "payload_bits": None, "geometry_profile": None,
        "background_source": str(photo) if photo else category,
        "hard_negative_category": category, "effects": effects, "yolo_label": "",
    }


def write_case(output: Path, role: str, index: int, positive: bool, profile: str | None,
               seed: int, photos: list[Path], used_payloads: set[str]) -> dict:
    sample_id = f"{role}_{'positive' if positive else 'negative'}_{index:04d}"
    if positive:
        image, mask, metadata = generate_positive(role, index, profile or FAMILY_PROFILES[0], seed,
                                                  photos, used_payloads)
    else:
        image, mask, metadata = generate_negative(role, index, seed, photos)
    image_path = output / "images" / role / f"{sample_id}.jpg"
    mask_path = output / "masks" / role / f"{sample_id}.png"
    label_path = output / "labels" / role / f"{sample_id}.txt"
    for path in (image_path, mask_path, label_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    quality = metadata["effects"]["jpeg_quality"]
    cv2.imwrite(str(image_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR),
                [cv2.IMWRITE_JPEG_QUALITY, quality])
    cv2.imwrite(str(mask_path), mask, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    label_path.write_text(metadata.pop("yolo_label"), encoding="utf-8")
    return {
        "sample_id": sample_id, "split": role, "random_seed": seed,
        "image": {"path": str(image_path), "sha256": sha256(image_path),
                  "dimensions": [CANVAS, CANVAS], "format": "jpeg"},
        "segmentation_mask": {"path": str(mask_path), "sha256": sha256(mask_path)},
        "yolo_label": {"path": str(label_path), "sha256": sha256(label_path),
                       "format": "class followed by segmentation polygon; empty for negatives"},
        "expected": metadata,
    }


def yaml_text(output: Path, train_role: str) -> str:
    return "\n".join((
        f"path: {output}", f"train: images/{train_role}", "val: images/development",
        "names:", "  0: qyoo", "",
    ))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--background-dir", type=Path,
                        default=Path(__file__).parent / "backgrounds")
    parser.add_argument("--family-train-positive", type=int, default=360)
    parser.add_argument("--historical-train-positive", type=int, default=360)
    parser.add_argument("--train-negative", type=int, default=180)
    parser.add_argument("--development-positive", type=int, default=180)
    parser.add_argument("--development-negative", type=int, default=90)
    parser.add_argument("--sealed-positive", type=int, default=240)
    parser.add_argument("--sealed-negative", type=int, default=120)
    parser.add_argument("--seed", type=int, default=MASTER_SEED)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty dataset {output}")
    output.mkdir(parents=True, exist_ok=True)
    photos = sorted(args.background_dir.resolve().glob("*"))
    photos = [path for path in photos if path.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    if len(photos) < 8:
        raise ValueError("at least eight source backgrounds are required for source-level split isolation")
    photo_roles = {
        "train_family": photos[:5], "train_historical": photos[:5],
        "development": photos[5:7], "sealed_test": photos[7:],
    }
    role_counts = {
        "train_family": (args.family_train_positive, args.train_negative),
        "train_historical": (args.historical_train_positive, args.train_negative),
        "development": (args.development_positive, args.development_negative),
        "sealed_test": (args.sealed_positive, args.sealed_negative),
    }
    records = []
    payload_guards: dict[str, set[str]] = {}
    for role_index, (role, (positive_count, negative_count)) in enumerate(role_counts.items()):
        if role == "train_family":
            payload_guards[role] = set()
        elif role == "train_historical":
            # The geometry ablation intentionally uses the same payload/condition sequence.
            payload_guards[role] = set()
        elif role == "development":
            payload_guards[role] = payload_guards["train_family"] | payload_guards["train_historical"]
        else:
            payload_guards[role] = (payload_guards["train_family"] | payload_guards["train_historical"] |
                                    payload_guards["development"])
        for index in range(positive_count):
            profile = "historical_svg_204" if role == "train_historical" else FAMILY_PROFILES[index % 3]
            seed_group = 0 if role in {"train_family", "train_historical"} else role_index - 1
            seed = args.seed + seed_group * 1_000_000 + index
            records.append(write_case(output, role, index, True, profile, seed,
                                      photo_roles[role], payload_guards[role]))
        for index in range(negative_count):
            seed_group = 0 if role in {"train_family", "train_historical"} else role_index - 1
            seed = args.seed + seed_group * 1_000_000 + 500_000 + index
            records.append(write_case(output, role, index, False, None, seed,
                                      photo_roles[role], payload_guards[role]))
    repository = Path(__file__).resolve().parents[1]
    manifest = {
        "schema": "org.qyoo.recovery.task06-ml-localization-dataset",
        "schema_version": 1,
        "master_seed": args.seed,
        "canvas_dimensions": [CANVAS, CANVAS],
        "generator_commit": git_commit(repository),
        "generator_script": str(Path(__file__).resolve()),
        "geometry_profiles": list(FAMILY_PROFILES),
        "legacy_python_excluded_from_training_family": True,
        "role_counts": {role: {"positive": counts[0], "negative": counts[1]}
                        for role, counts in role_counts.items()},
        "background_source_roles": {role: [{"path": str(path), "sha256": sha256(path)}
                                             for path in paths]
                                    for role, paths in photo_roles.items()},
        "split_policy": {
            "training": ["train_family", "train_historical"],
            "development": ["development"],
            "synthetic_sealed_test": ["sealed_test"],
            "training_ablation_payloads_and_conditions_shared_by_index": True,
            "development_payloads_unseen_in_training": True,
            "sealed_payloads_unseen_in_training_and_development": True,
            "photo_background_sources_disjoint_between_training_development_and_sealed": True,
        },
        "sample_count": len(records),
        "samples": records,
        "environment": {"python": sys.version, "opencv": cv2.__version__,
                        "numpy": np.__version__, "pillow": Image.__version__},
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (output / "family.yaml").write_text(yaml_text(output, "train_family"), encoding="utf-8")
    (output / "historical-only.yaml").write_text(yaml_text(output, "train_historical"), encoding="utf-8")
    print(json.dumps({"output": str(output), "sample_count": len(records),
                      "role_counts": manifest["role_counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
