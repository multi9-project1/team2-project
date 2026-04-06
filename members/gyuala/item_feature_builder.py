from __future__ import annotations

import json
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List

from fashion_config import MOCK_DATASET_ITEMS

DATASET_SURVEY_FIELD_KEYS = ["Q3", "Q411", "Q412", "Q413", "Q414"] + [f"Q42{i:02d}" for i in range(1, 17)]
IMAGE_FILE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def extract_dataset_zip_archive(zip_path: str | Path, extract_dir: str | Path) -> Path:
    zip_archive_path = Path(zip_path)
    if not zip_archive_path.exists():
        raise FileNotFoundError(f"zip file not found: {zip_archive_path}")

    extract_path = Path(extract_dir)
    extract_path.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_archive_path, "r") as archive:
        archive.extractall(extract_path)
    return extract_path


def _ensure_extracted_dataset_directory(zip_path: str | Path, extract_dir: str | Path) -> Path:
    extract_path = Path(extract_dir)
    if extract_path.exists() and any(extract_path.rglob("*.json")):
        return extract_path
    return extract_dataset_zip_archive(zip_path, extract_dir)


def ensure_dataset_archive_extracted(zip_path: str | Path, extract_dir: str | Path) -> Path:
    return _ensure_extracted_dataset_directory(zip_path, extract_dir)


def resolve_dataset_root_directory(dataset_dir: str | Path) -> Path:
    dataset_root_path = Path(dataset_dir)
    nested_sample_directory = dataset_root_path / "Sample"
    if nested_sample_directory.exists():
        return nested_sample_directory
    return dataset_root_path


def discover_dataset_label_files(root_dir: str | Path) -> List[Path]:
    resolved_root_dir = resolve_dataset_root_directory(root_dir)
    if not resolved_root_dir.exists():
        raise FileNotFoundError(f"dataset directory not found: {resolved_root_dir}")
    return sorted(resolved_root_dir.rglob("*.json"))


def _find_nested_field_value(payload: Any, key: str) -> Any:
    if isinstance(payload, dict):
        if key in payload:
            return payload[key]
        for value in payload.values():
            found = _find_nested_field_value(value, key)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _find_nested_field_value(value, key)
            if found is not None:
                return found
    return None


def _extract_dataset_survey_values(payload: Any) -> Dict[str, int]:
    extracted_values: Dict[str, int] = {}
    survey_section = _find_nested_field_value(payload, "survey")
    for question_code in DATASET_SURVEY_FIELD_KEYS:
        raw_question_value = None
        if isinstance(survey_section, dict):
            raw_question_value = survey_section.get(question_code)
        if raw_question_value is None:
            raw_question_value = _find_nested_field_value(payload, question_code)
        if raw_question_value is None:
            continue
        try:
            extracted_values[question_code] = int(raw_question_value)
        except (TypeError, ValueError):
            continue
    return extracted_values


def _resolve_local_image_path(json_path: Path, payload: Dict[str, Any]) -> str:
    image_path_candidates = [
        _find_nested_field_value(payload, "image_path"),
        _find_nested_field_value(payload, "image"),
        _find_nested_field_value(payload, "img_path"),
        _find_nested_field_value(payload, "source"),
    ]
    for image_candidate in image_path_candidates:
        if isinstance(image_candidate, str) and image_candidate:
            possible_image_path = (json_path.parent / image_candidate).resolve()
            if possible_image_path.exists():
                return str(possible_image_path)
            return image_candidate

    file_stem = json_path.stem
    for image_path in json_path.parent.rglob("*"):
        if image_path.suffix.lower() in IMAGE_FILE_EXTENSIONS and image_path.stem == file_stem:
            return str(image_path.resolve())
    return str(json_path.resolve())


def _select_first_available_string(payload: Dict[str, Any], keys: Iterable[str], default: str = "unknown") -> str:
    for key in keys:
        value = _find_nested_field_value(payload, key)
        if value not in (None, ""):
            return str(value)
    return default


def parse_dataset_item_from_label_file(json_path: str | Path) -> Dict[str, Any] | None:
    json_file = Path(json_path)
    try:
        payload = json.loads(json_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

    dataset_feature_values = _extract_dataset_survey_values(payload)
    if not dataset_feature_values:
        return None

    parsed_item_record = {
        "item_id": _select_first_available_string(payload, ("item_id", "id", "file_id"), default=json_file.stem),
        "image_path": _resolve_local_image_path(json_file, payload),
        "gender": _select_first_available_string(payload, ("gender", "model_gender", "sex"), default="U"),
        "era": _select_first_available_string(payload, ("era", "year", "season"), default="unknown"),
        "style": _select_first_available_string(payload, ("style", "look", "category"), default="unknown"),
    }
    parsed_item_record.update(dataset_feature_values)
    return parsed_item_record


def parse_dataset_item_from_label_file_with_image_index(
    json_path: str | Path,
    image_index: Dict[str, str],
) -> Dict[str, Any] | None:
    json_file = Path(json_path)
    try:
        payload = json.loads(json_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

    dataset_feature_values = _extract_dataset_survey_values(payload)
    if not dataset_feature_values:
        return None

    image_name = _select_first_available_string(payload, ("imgName", "image_path", "image"), default="")
    resolved_image_path = image_index.get(image_name, "")

    parsed_item_record = {
        "item_id": _select_first_available_string(payload, ("item_id", "id", "file_id", "E_id"), default=json_file.stem),
        "image_path": resolved_image_path,
        "gender": _select_first_available_string(payload, ("gender", "model_gender", "sex"), default="U"),
        "era": _select_first_available_string(payload, ("era", "year", "season"), default="unknown"),
        "style": _select_first_available_string(payload, ("style", "look", "category"), default="unknown"),
        "label_path": str(json_file.resolve()),
    }
    parsed_item_record.update(dataset_feature_values)
    return parsed_item_record


def parse_dataset_item_from_label_payload(
    payload: Dict[str, Any],
    *,
    json_identifier: str,
    image_locator: str,
) -> Dict[str, Any] | None:
    dataset_feature_values = _extract_dataset_survey_values(payload)
    if not dataset_feature_values:
        return None

    parsed_item_record = {
        "item_id": _select_first_available_string(payload, ("item_id", "id", "file_id", "E_id"), default=Path(json_identifier).stem),
        "image_path": image_locator,
        "gender": _select_first_available_string(payload, ("gender", "model_gender", "sex"), default="U"),
        "era": _select_first_available_string(payload, ("era", "year", "season"), default="unknown"),
        "style": _select_first_available_string(payload, ("style", "look", "category"), default="unknown"),
        "label_path": json_identifier,
    }
    parsed_item_record.update(dataset_feature_values)
    return parsed_item_record


def _create_zip_image_path_index(zip_file: zipfile.ZipFile) -> Dict[str, str]:
    image_path_index: Dict[str, str] = {}
    for member in zip_file.namelist():
        lower_name = member.lower()
        if lower_name.endswith((".jpg", ".jpeg", ".png", ".webp")):
            image_path_index.setdefault(Path(member).name, member)
    return image_path_index


def _create_directory_image_path_index(dataset_dir: Path) -> Dict[str, str]:
    image_path_index: Dict[str, str] = {}
    for image_file in dataset_dir.rglob("*"):
        if image_file.suffix.lower() in IMAGE_FILE_EXTENSIONS:
            image_path_index.setdefault(image_file.name, str(image_file.resolve()))
    return image_path_index


@lru_cache(maxsize=4)
def _load_dataset_items_from_zip_cache(zip_path_str: str) -> tuple[Dict[str, Any], ...]:
    zip_archive_path = Path(zip_path_str)
    if not zip_archive_path.exists():
        raise FileNotFoundError(f"zip file not found: {zip_archive_path}")

    dataset_items: List[Dict[str, Any]] = []
    with zipfile.ZipFile(zip_archive_path, "r") as archive:
        image_index = _create_zip_image_path_index(archive)
        for member in archive.namelist():
            if not member.lower().endswith(".json"):
                continue
            try:
                payload = json.loads(archive.read(member).decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

            image_name = _select_first_available_string(payload, ("imgName", "image_path", "image"), default="")
            image_locator = image_index.get(image_name, image_name)
            parsed_item_record = parse_dataset_item_from_label_payload(
                payload,
                json_identifier=member,
                image_locator=image_locator,
            )
            if parsed_item_record:
                dataset_items.append(parsed_item_record)
    return tuple(dataset_items)


@lru_cache(maxsize=4)
def _load_dataset_items_from_directory_cache(dataset_dir_str: str) -> tuple[Dict[str, Any], ...]:
    resolved_dataset_dir = resolve_dataset_root_directory(dataset_dir_str).resolve()
    image_index = _create_directory_image_path_index(resolved_dataset_dir)
    dataset_items: List[Dict[str, Any]] = []
    for json_file in discover_dataset_label_files(resolved_dataset_dir):
        parsed_item_record = parse_dataset_item_from_label_file_with_image_index(json_file, image_index)
        if parsed_item_record:
            dataset_items.append(parsed_item_record)
    return tuple(dataset_items)


def load_dataset_item_records(
    *,
    zip_path: str | Path | None = None,
    extract_dir: str | Path | None = None,
    dataset_dir: str | Path | None = None,
    allow_mock: bool = True,
) -> List[Dict[str, Any]]:
    if dataset_dir:
        resolved_dataset_dir = Path(dataset_dir)
        if resolved_dataset_dir.exists():
            dataset_items = list(_load_dataset_items_from_directory_cache(str(resolved_dataset_dir.resolve())))
            if dataset_items:
                return [dict(item) for item in dataset_items]

    if zip_path:
        zip_archive_path = Path(zip_path)
        if zip_archive_path.exists():
            dataset_items = list(_load_dataset_items_from_zip_cache(str(zip_archive_path.resolve())))
            if dataset_items:
                return [dict(item) for item in dataset_items]

    if zip_path and extract_dir:
        resolved_dataset_dir = _ensure_extracted_dataset_directory(zip_path, extract_dir)
        if resolved_dataset_dir.exists():
            dataset_items = list(_load_dataset_items_from_directory_cache(str(resolved_dataset_dir.resolve())))
            if dataset_items:
                return [dict(item) for item in dataset_items]

    if allow_mock:
        return [dict(item) for item in MOCK_DATASET_ITEMS]

    raise ValueError("no valid dataset items found and mock fallback disabled")
