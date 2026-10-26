#!/usr/bin/env python3
"""Render local, non-redistributed font-pairing examples and blind packets."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
from typing import Any

import PIL
from PIL import Image, ImageDraw, ImageFont, features


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "visual-design-review" / "tests" / "font-pairing-study-fixtures.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_fixture(path: Path) -> dict[str, Any]:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    if fixture.get("schema_version") != "1.0":
        raise ValueError("unsupported fixture schema")
    tasks = fixture.get("pair_tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("pair_tasks must be a non-empty list")
    for task in tasks:
        if len(task.get("variants", [])) != 2:
            raise ValueError(f"{task.get('id')}: exactly two variants are required")
        if task.get("blind_ratings") != []:
            raise ValueError(f"{task.get('id')}: ratings must remain empty before human review")
        if not task.get("fixed", {}).get("korean_font"):
            raise ValueError(f"{task.get('id')}: korean_font is required")
        for variant in task["variants"]:
            if not variant.get("latin_font"):
                raise ValueError(f"{task.get('id')}: latin_font is required")
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
    contract = fixture["render_contract"]
    width, height = contract["canvas"]
    fixed = task["fixed"]
    size = fixed["font_size_px"]
    padding_x, padding_y = fixed["padding_px"]
    results: list[dict[str, Any]] = []
    for variant in task["variants"]:
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
        image_path = output / "blind" / task["id"] / f"{variant['label']}.png"
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    fixture = load_fixture(args.fixture)
    if args.validate_only:
        print(f"PASS: validated {len(fixture['pair_tasks'])} controlled font-pair tasks")
        return 0
    if args.output_dir is None:
        parser.error("--output-dir is required when rendering")
    records: list[dict[str, Any]] = []
    for task in fixture["pair_tasks"]:
        records.extend(render_task(task, fixture, args.output_dir))
    write_manifests(fixture, args.fixture, args.output_dir, records)
    print(f"PASS: rendered {len(records)} PNGs with BASIC layout; human ratings remain pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
