"""
Case ingestion: turn an uploaded file into validated Case objects.

Supports three input formats so users don't have to hand-craft our exact
JSON schema:

1. JSON  -- a single case object, or a list of case objects, matching the
            Case schema. This is the canonical/native format.
2. CSV   -- one row per case, with columns mapping onto the case fields.
            Genomic findings may be given as a single ';'-separated cell.
3. TXT   -- one free-text clinical vignette (optionally several, separated
            by a line containing only '---'). A lightweight, rule-based
            converter extracts structured fields. This is best-effort and
            explicitly surfaces what it could and couldn't parse.

Every path funnels through `_coerce_case`, which validates against the
Pydantic schema, so malformed input fails loudly with a clear message
rather than silently producing a bad case.
"""

from __future__ import annotations

import csv
import io
import json
import re
from typing import List, Tuple

from tumorboard_agent.schemas import Case, PatientFactors


class CaseParseError(ValueError):
    """Raised when an uploaded file can't be turned into a valid Case."""


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------
def parse_json(raw: str) -> List[Case]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CaseParseError(f"File is not valid JSON: {exc}") from exc

    records = data if isinstance(data, list) else [data]
    if not records:
        raise CaseParseError("JSON contained no cases.")
    return [_coerce_case(r, source=f"JSON record {i + 1}") for i, r in enumerate(records)]


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------
CSV_COLUMNS = {
    "case_id", "cancer_type", "stage", "imaging_findings", "pathology_findings",
    "genomic_findings", "performance_status", "comorbidities", "patient_preferences",
}


def parse_csv(raw: str) -> List[Case]:
    reader = csv.DictReader(io.StringIO(raw))
    if reader.fieldnames is None:
        raise CaseParseError("CSV appears to be empty.")

    unknown = set(reader.fieldnames) - CSV_COLUMNS
    if unknown:
        raise CaseParseError(
            f"CSV has unrecognized column(s): {sorted(unknown)}. "
            f"Allowed columns: {sorted(CSV_COLUMNS)}."
        )

    cases = []
    for i, row in enumerate(reader):
        record = {
            "case_id": (row.get("case_id") or f"uploaded-{i + 1}").strip(),
            "cancer_type": (row.get("cancer_type") or "unspecified").strip(),
            "stage": (row.get("stage") or "").strip() or None,
            "imaging_findings": (row.get("imaging_findings") or "").strip(),
            "pathology_findings": (row.get("pathology_findings") or "").strip(),
            "genomic_findings": _split_multi(row.get("genomic_findings")),
            "patient_factors": {
                "performance_status": (row.get("performance_status") or "").strip() or None,
                "comorbidities": _split_multi(row.get("comorbidities")),
                "patient_preferences": (row.get("patient_preferences") or "").strip() or None,
            },
        }
        cases.append(_coerce_case(record, source=f"CSV row {i + 2}"))  # +2: header + 1-index
    if not cases:
        raise CaseParseError("CSV had a header but no data rows.")
    return cases


def _split_multi(cell: str | None) -> List[str]:
    if not cell:
        return []
    parts = re.split(r"[;|]", cell)
    return [p.strip() for p in parts if p.strip()]


# ---------------------------------------------------------------------------
# Free text
# ---------------------------------------------------------------------------
CANCER_TERMS = [
    "breast", "lung", "colorectal", "colon", "rectal", "prostate", "ovarian",
    "pancreatic", "gastric", "melanoma", "lymphoma",
]
GENOMIC_TERMS = [
    "EGFR", "ALK", "HER2", "BRCA1", "BRCA2", "KRAS G12C", "KRAS", "MSI-H",
    "dMMR", "PD-L1", "TMB-low", "TMB-high", "ER positive", "ER+", "triple negative",
]
ECOG_RE = re.compile(r"ecog\s*([0-4])", re.IGNORECASE)


def parse_free_text(raw: str) -> Tuple[List[Case], List[str]]:
    """Best-effort conversion. Returns (cases, warnings)."""

    chunks = [c.strip() for c in re.split(r"(?m)^---\s*$", raw) if c.strip()]
    if not chunks:
        raise CaseParseError("The text file is empty.")

    cases, warnings = [], []
    for i, chunk in enumerate(chunks):
        record, chunk_warnings = _free_text_to_record(chunk, index=i + 1)
        warnings.extend(chunk_warnings)
        cases.append(_coerce_case(record, source=f"text vignette {i + 1}"))
    return cases, warnings


def _free_text_to_record(text: str, index: int) -> Tuple[dict, List[str]]:
    lowered = text.lower()
    warnings: List[str] = []

    cancer_type = next((t for t in CANCER_TERMS if t in lowered), None)
    if cancer_type is None:
        cancer_type = "unspecified"
        warnings.append(f"Vignette {index}: could not detect a cancer type; set to 'unspecified'.")

    genomic = [t for t in GENOMIC_TERMS if t.lower() in lowered]

    ecog_match = ECOG_RE.search(text)
    performance_status = f"ECOG {ecog_match.group(1)}" if ecog_match else None
    if performance_status is None:
        warnings.append(f"Vignette {index}: no ECOG performance status found; patient-factor logic will be limited.")

    imaging = _extract_sentence(text, ["imaging", "ct ", "scan", "mri", "lesion", "metasta"])
    pathology = _extract_sentence(text, ["pathology", "biopsy", "histolog", "carcinoma", "grade", "receptor", "ihc"])
    prefs = _extract_sentence(text, ["prefer", "wants", "quality of life", "avoid hospital", "goal"])

    if not imaging:
        warnings.append(f"Vignette {index}: no imaging sentence detected.")
    if not pathology:
        warnings.append(f"Vignette {index}: no pathology sentence detected.")

    record = {
        "case_id": f"uploaded-text-{index}",
        "cancer_type": cancer_type,
        "stage": None,
        "imaging_findings": imaging,
        "pathology_findings": pathology,
        "genomic_findings": genomic,
        "patient_factors": {
            "performance_status": performance_status,
            "comorbidities": [],
            "patient_preferences": prefs or None,
        },
    }
    return record, warnings


def _extract_sentence(text: str, keywords: List[str]) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    hits = [s.strip() for s in sentences if any(k in s.lower() for k in keywords)]
    return " ".join(hits)


# ---------------------------------------------------------------------------
# Shared validation + dispatch
# ---------------------------------------------------------------------------
def _coerce_case(record: dict, source: str) -> Case:
    try:
        if "patient_factors" in record and isinstance(record["patient_factors"], dict):
            record = {**record, "patient_factors": PatientFactors(**record["patient_factors"])}
        return Case(**record)
    except Exception as exc:  # noqa: BLE001
        raise CaseParseError(f"{source}: could not build a valid case ({exc}).") from exc


def parse_upload(filename: str, raw_bytes: bytes) -> Tuple[List[Case], List[str]]:
    """Dispatch on file extension. Returns (cases, warnings)."""

    try:
        raw = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CaseParseError("File must be UTF-8 encoded text (JSON, CSV, or TXT).") from exc

    name = filename.lower()
    if name.endswith(".json"):
        return parse_json(raw), []
    if name.endswith(".csv"):
        return parse_csv(raw), []
    if name.endswith(".txt"):
        return parse_free_text(raw)
    raise CaseParseError(
        f"Unsupported file type '{filename}'. Please upload a .json, .csv, or .txt file."
    )
