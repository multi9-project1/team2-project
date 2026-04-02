from __future__ import annotations

import json
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List

from fashion_config import MOCK_ITEMS

QUESTION_KEYS = ["Q411", "Q412", "Q413", "Q414"] + [f"Q42{i:02d}" for i in range(1, 17)]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def extract_sample_zip(zip_path: str | Path, extract_dir: str | Path) -> Path:
    zip_file = Path(zip_path)
    if not zip_file.exists():
        raise FileNotFoundError(f"zip file not found: {zip_file}")

    destination = Path(extract_dir)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_file, "r") as archive:
        archive.extractall(destination)
    return destination


def _extract_if_needed(zip_path: str | Path, extract_dir: str | Path) -> Path:
    destination = Path(extract_dir)
    if destination.exists() and any(destination.rglob("*.json")):
        return destination
    return extract_sample_zip(zip_path, extract_dir)


def ensure_dataset_extracted(zip_path: str | Path, extract_dir: str | Path) -> Path:
    return _extract_if_needed(zip_path, extract_dir)


def normalize_dataset_root(dataset_dir: str | Path) -> Path:
    root = Path(dataset_dir)
    nested_root = root / "Sample"
    if nested_root.exists():
        return nested_root
    return root


def load_label_jsons(root_dir: str | Path) -> List[Path]:
    root = normalize_dataset_root(root_dir)
    if not root.exists():
        raise FileNotFoundError(f"dataset directory not found: {root}")
    return sorted(root.rglob("*.json"))


def _find_nested_value(payload: Any, key: str) -> Any:
    if isinstance(payload, dict):
        if key in payload:
            return payload[key]
        for value in payload.values():
            found = _find_nested_value(value, key)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _find_nested_value(value, key)
            if found is not None:
                return found
    return None


def _collect_question_values(payload: Any) -> Dict[str, int]:
    result: Dict[str, int] = {}
    survey_blob = _find_nested_value(payload, "survey")
    for key in QUESTION_KEYS:
        raw_value = None
        if isinstance(survey_blob, dict):
            raw_value = survey_blob.get(key)
        if raw_value is None:
            raw_value = _find_nested_value(payload, key)
        if raw_value is None:
            continue
        try:
            result[key] = int(raw_value)
        except (TypeError, ValueError):
            continue
    return result


def _resolve_image_path(json_path: Path, payload: Dict[str, Any]) -> str:
    candidates = [
        _find_nested_value(payload, "image_path"),
        _find_nested_value(payload, "image"),
        _find_nested_value(payload, "img_path"),
        _find_nested_value(payload, "source"),
    ]
    for candidate in candidates:
        if isinstance(candidate, str) and candidate:
            possible = (json_path.parent / candidate).resolve()
            if possible.exists():
                return str(possible)
            return candidate

    stem = json_path.stem
    for image_path in json_path.parent.rglob("*"):
        if image_path.suffix.lower() in IMAGE_EXTENSIONS and image_path.stem == stem:
            return str(image_path.resolve())
    return str(json_path.resolve())


def _pick_first(payload: Dict[str, Any], keys: Iterable[str], default: str = "unknown") -> str:
    for key in keys:
        value = _find_nested_value(payload, key)
        if value not in (None, ""):
            return str(value)
    return default


def parse_item_feature(json_path: str | Path) -> Dict[str, Any] | None:
    json_file = Path(json_path)
    try:
        payload = json.loads(json_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

    features = _collect_question_values(payload)
    if not features:
        return None

    item = {
        "item_id": _pick_first(payload, ("item_id", "id", "file_id"), default=json_file.stem),
        "image_path": _resolve_image_path(json_file, payload),
        "gender": _pick_first(payload, ("gender", "model_gender", "sex"), default="U"),
        "era": _pick_first(payload, ("era", "year", "season"), default="unknown"),
        "style": _pick_first(payload, ("style", "look", "category"), default="unknown"),
    }
    item.update(features)
    return item


def parse_item_feature_with_index(
    json_path: str | Path,
    image_index: Dict[str, str],
) -> Dict[str, Any] | None:
    json_file = Path(json_path)
    try:
        payload = json.loads(json_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

    features = _collect_question_values(payload)
    if not features:
        return None

    image_name = _pick_first(payload, ("imgName", "image_path", "image"), default="")
    image_path = image_index.get(image_name, "")

    item = {
        "item_id": _pick_first(payload, ("item_id", "id", "file_id", "E_id"), default=json_file.stem),
        "image_path": image_path,
        "gender": _pick_first(payload, ("gender", "model_gender", "sex"), default="U"),
        "era": _pick_first(payload, ("era", "year", "season"), default="unknown"),
        "style": _pick_first(payload, ("style", "look", "category"), default="unknown"),
        "label_path": str(json_file.resolve()),
    }
    item.update(features)
    return item


def parse_item_feature_from_payload(
    payload: Dict[str, Any],
    *,
    json_identifier: str,
    image_locator: str,
) -> Dict[str, Any] | None:
    features = _collect_question_values(payload)
    if not features:
        return None

    item = {
        "item_id": _pick_first(payload, ("item_id", "id", "file_id", "E_id"), default=Path(json_identifier).stem),
        "image_path": image_locator,
        "gender": _pick_first(payload, ("gender", "model_gender", "sex"), default="U"),
        "era": _pick_first(payload, ("era", "year", "season"), default="unknown"),
        "style": _pick_first(payload, ("style", "look", "category"), default="unknown"),
        "label_path": json_identifier,
    }
    item.update(features)
    return item


def _build_zip_image_index(zip_file: zipfile.ZipFile) -> Dict[str, str]:
    index: Dict[str, str] = {}
    for member in zip_file.namelist():
        lower_name = member.lower()
        if lower_name.endswith((".jpg", ".jpeg", ".png", ".webp")):
            index.setdefault(Path(member).name, member)
    return index


def _build_directory_image_index(dataset_dir: Path) -> Dict[str, str]:
    index: Dict[str, str] = {}
    for image_file in dataset_dir.rglob("*"):
        if image_file.suffix.lower() in IMAGE_EXTENSIONS:
            index.setdefault(image_file.name, str(image_file.resolve()))
    return index


@lru_cache(maxsize=4)
def _load_items_from_zip(zip_path_str: str) -> tuple[Dict[str, Any], ...]:
    zip_path = Path(zip_path_str)
    if not zip_path.exists():
        raise FileNotFoundError(f"zip file not found: {zip_path}")

    items: List[Dict[str, Any]] = []
    with zipfile.ZipFile(zip_path, "r") as archive:
        image_index = _build_zip_image_index(archive)
        for member in archive.namelist():
            if not member.lower().endswith(".json"):
                continue
            try:
                payload = json.loads(archive.read(member).decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

            image_name = _pick_first(payload, ("imgName", "image_path", "image"), default="")
            image_locator = image_index.get(image_name, image_name)
            parsed = parse_item_feature_from_payload(
                payload,
                json_identifier=member,
                image_locator=image_locator,
            )
            if parsed:
                items.append(parsed)
    return tuple(items)


@lru_cache(maxsize=4)
def _load_items_from_directory(dataset_dir_str: str) -> tuple[Dict[str, Any], ...]:
    resolved_dataset_dir = normalize_dataset_root(dataset_dir_str).resolve()
    image_index = _build_directory_image_index(resolved_dataset_dir)
    items: List[Dict[str, Any]] = []
    for json_file in load_label_jsons(resolved_dataset_dir):
        parsed = parse_item_feature_with_index(json_file, image_index)
        if parsed:
            items.append(parsed)
    return tuple(items)


def build_item_feature_list(
    *,
    zip_path: str | Path | None = None,
    extract_dir: str | Path | None = None,
    dataset_dir: str | Path | None = None,
    allow_mock: bool = True,
) -> List[Dict[str, Any]]:
    if dataset_dir:
        resolved_dataset_dir = Path(dataset_dir)
        if resolved_dataset_dir.exists():
            items = list(_load_items_from_directory(str(resolved_dataset_dir.resolve())))
            if items:
                return [dict(item) for item in items]

    if zip_path:
        zip_file = Path(zip_path)
        if zip_file.exists():
            items = list(_load_items_from_zip(str(zip_file.resolve())))
            if items:
                return [dict(item) for item in items]

    if zip_path and extract_dir:
        resolved_dataset_dir = _extract_if_needed(zip_path, extract_dir)
        if resolved_dataset_dir.exists():
            items = list(_load_items_from_directory(str(resolved_dataset_dir.resolve())))
            if items:
                return [dict(item) for item in items]

    if allow_mock:
        return [dict(item) for item in MOCK_ITEMS]

    raise ValueError("no valid dataset items found and mock fallback disabled")
