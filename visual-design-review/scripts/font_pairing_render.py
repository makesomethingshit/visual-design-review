#!/usr/bin/env python3
"""Render local, non-redistributed font-pairing examples and blind packets."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any

import PIL
from PIL import Image, ImageDraw, ImageFont, features


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "assets" / "font-pairing-study-fixtures.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _path_component(value: Any, label: str) -> str:
    if (not isinstance(value, str) or not value.strip() or value.endswith((".", " "))
            or any(character in value for character in "/\\:\0")):
        raise ValueError(f"{label} must be a single non-empty path component")
    return value


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON list")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return value


def _task_names(task: dict[str, Any]) -> tuple[str, list[str]]:
    task = _object(task, "pair_tasks item")
    task_id = _path_component(task.get("id"), "task id")
    variants = _list(task.get("variants"), f"{task_id}: variants")
    if len(variants) != 2:
        raise ValueError(f"{task_id}: exactly two variants are required")
    labels = [_path_component(_object(variant, f"{task_id}: variant").get("label"),
                              "variant label") for variant in variants]
    if len({label.casefold() for label in labels}) != len(labels):
        raise ValueError(f"{task_id}: duplicate variant labels")
    return task_id, labels


def load_fixture(path: Path) -> dict[str, Any]:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    fixture = _object(fixture, "fixture")
    if fixture.get("schema_version") != "1.0":
        raise ValueError("unsupported fixture schema")
    contract = _object(fixture.get("render_contract"), "render_contract")
    for field in ("platform", "renderer", "pillow_layout_engine",
                  "font_version_identifier", "anchor", "background",
                  "foreground", "output"):
        _string(contract.get(field), f"render_contract.{field}")
    if not isinstance(contract.get("raqm_or_harfbuzz"), bool):
        raise ValueError("render_contract.raqm_or_harfbuzz must be a boolean")
    canvas = _list(contract.get("canvas"), "render_contract.canvas")
    if len(canvas) != 2:
        raise ValueError("render_contract.canvas must contain width and height")
    for index, value in enumerate(canvas):
        _integer(value, f"render_contract.canvas[{index}]")

    tasks = _list(fixture.get("pair_tasks"), "pair_tasks")
    if not tasks:
        raise ValueError("pair_tasks must be a non-empty list")
    task_ids: set[str] = set()
    for task_index, raw_task in enumerate(tasks):
        task = _object(raw_task, f"pair_tasks[{task_index}]")
        task_id, _ = _task_names(task)
        if task_id.casefold() in task_ids:
            raise ValueError(f"duplicate task id: {task_id}")
        task_ids.add(task_id.casefold())
        _string(task.get("context"), f"{task_id}: context")
        _string(task.get("controlled_variable"), f"{task_id}: controlled_variable")
        blind_ratings = _list(task.get("blind_ratings"), f"{task_id}: blind_ratings")
        if blind_ratings:
            raise ValueError(f"{task.get('id')}: ratings must remain empty before human review")
        fixed = _object(task.get("fixed"), f"{task_id}: fixed")
        _string(fixed.get("korean_font"), f"{task_id}: korean_font")
        _integer(fixed.get("font_size_px"), f"{task_id}: font_size_px")
        _integer(fixed.get("line_spacing_px"), f"{task_id}: line_spacing_px")
        padding = _list(fixed.get("padding_px"), f"{task_id}: padding_px")
        if len(padding) != 2:
            raise ValueError(f"{task_id}: padding_px must contain x and y")
        for index, value in enumerate(padding):
            _integer(value, f"{task_id}: padding_px[{index}]")
        text_lines = _list(task.get("text_lines"), f"{task_id}: text_lines")
        for line_index, raw_line in enumerate(text_lines):
            line = _list(raw_line, f"{task_id}: text_lines[{line_index}]")
            for segment_index, raw_segment in enumerate(line):
                segment = _object(raw_segment,
                                  f"{task_id}: text_lines[{line_index}][{segment_index}]")
                role = _string(segment.get("role"), f"{task_id}: segment role")
                if role not in ("korean", "latin"):
                    raise ValueError(f"{task_id}: segment role must be korean or latin")
                _string(segment.get("text"), f"{task_id}: segment text")
        for variant_index, raw_variant in enumerate(task["variants"]):
            variant = _object(raw_variant, f"{task_id}: variants[{variant_index}]")
            _string(variant.get("latin_font"), f"{task_id}: latin_font")
    return fixture


def require_font(path_text: str) -> Path:
    path = Path(path_text)
    if not path.is_file():
        raise FileNotFoundError(
            f"font not found: {path}; select a legally usable local font, "
            "then rerun without adding the font to the repository"
        )
    return path


def font_record(path: Path, size: int) -> tuple[ImageFont.FreeTypeFont, dict[str, Any]]:
    font = ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.BASIC)
    file_hash = sha256(path)
    return font, {
        "path": str(path),
        "name": font.getname(),
        "file_size": path.stat().st_size,
        "file_sha256": file_hash,
        "version_identifier": "sha256:" + file_hash,
        "numeric_version": None,
        "size_px": size,
        "layout_engine": "BASIC",
    }


def render_task(task: dict[str, Any], fixture: dict[str, Any], output: Path) -> list[dict[str, Any]]:
    task_id, labels = _task_names(task)
    image_paths = [output / "blind" / task_id / f"{label}.png" for label in labels]
    output_root = output.resolve()
    # Check both images before creating directories or loading fonts. Existing
    # links below the explicitly selected output root must not redirect writes.
    for path in image_paths:
        if not path.resolve().is_relative_to(output_root):
            raise ValueError("image destination is outside output directory")
    contract = fixture["render_contract"]
    width, height = contract["canvas"]
    fixed = task["fixed"]
    size = fixed["font_size_px"]
    padding_x, padding_y = fixed["padding_px"]
    results: list[dict[str, Any]] = []
    for variant, image_path in zip(task["variants"], image_paths):
        korean_path = require_font(fixed["korean_font"])
        latin_path = require_font(variant["latin_font"])
        korean, korean_meta = font_record(korean_path, size)
        latin, latin_meta = font_record(latin_path, size)
        image = Image.new("RGB", (width, height), contract["background"])
        draw = ImageDraw.Draw(image)
        baseline = padding_y + korean.getmetrics()[0]
        y = baseline
        for line in task["text_lines"]:
            x = padding_x
            for segment in line:
                font = korean if segment["role"] == "korean" else latin
                text = segment["text"]
                bounds = draw.textbbox((x, y), text, font=font, anchor="ls")
                if not (0 <= bounds[0] < bounds[2] <= width and
                        0 <= bounds[1] < bounds[3] <= height):
                    raise ValueError(f"{task['id']}/{variant['label']}: text would be cropped: {bounds}")
                draw.text((x, y), text, fill=contract["foreground"], font=font, anchor="ls")
                x += draw.textlength(text, font=font)
            y += fixed["line_spacing_px"]
        image_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(image_path, format="PNG", optimize=False)
        results.append({
            "task_id": task["id"],
            "label": variant["label"],
            "image": str(image_path.relative_to(output)).replace("\\", "/"),
            "image_sha256": sha256(image_path),
            "parameters": {
                "canvas": [width, height],
                "padding_px": [padding_x, padding_y],
                "font_size_px": size,
                "line_spacing_px": fixed["line_spacing_px"],
                "background": contract["background"],
                "foreground": contract["foreground"],
                "renderer": contract["renderer"],
                "pillow_version": PIL.__version__,
                "anchor": contract["anchor"],
                "layout_engine": "BASIC",
                "raqm": bool(features.check("raqm")),
                "platform": platform.platform(),
            },
            "fonts": {"korean": korean_meta, "latin": latin_meta},
        })
    return results


def write_manifests(fixture: dict[str, Any], fixture_path: Path,
                    output: Path, records: list[dict[str, Any]]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    key = {
        "fixture": str(fixture_path.resolve()),
        "fixture_sha256": sha256(fixture_path),
        "font_binaries_in_repository": False,
        "records": records,
    }
    (output / "render-manifest.json").write_text(
        json.dumps(key, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    blind = [{key: value for key, value in record.items() if key != "fonts"}
             for record in records]
    (output / "blind-packet.json").write_text(
        json.dumps({"status": "HUMAN_REVIEW_PENDING", "ratings": [], "items": blind},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    if not args.validate_only and args.output_dir is None:
        parser.error("--output-dir is required when rendering")
    try:
        fixture = load_fixture(args.fixture)
        if args.validate_only:
            print(f"PASS: validated {len(fixture['pair_tasks'])} controlled font-pair tasks")
            return 0
        records: list[dict[str, Any]] = []
        for task in fixture["pair_tasks"]:
            records.extend(render_task(task, fixture, args.output_dir))
        write_manifests(fixture, args.fixture, args.output_dir, records)
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 2
    print(f"PASS: rendered {len(records)} PNGs with BASIC layout; human ratings remain pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
