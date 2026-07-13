import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tumorboard_agent.case_loader import CaseParseError, parse_upload


def test_parse_json_single_object():
    raw = b'{"case_id":"j1","cancer_type":"lung","imaging_findings":"stable","pathology_findings":"adenocarcinoma","genomic_findings":["EGFR exon 19 deletion"],"patient_factors":{"performance_status":"ECOG 1"}}'
    cases, warnings = parse_upload("x.json", raw)
    assert len(cases) == 1
    assert cases[0].case_id == "j1"
    assert cases[0].genomic_findings == ["EGFR exon 19 deletion"]


def test_parse_json_list():
    raw = b'[{"case_id":"a","cancer_type":"lung"},{"case_id":"b","cancer_type":"breast"}]'
    cases, _ = parse_upload("x.json", raw)
    assert [c.case_id for c in cases] == ["a", "b"]


def test_parse_csv_splits_multi_value_cells():
    raw = (
        b"case_id,cancer_type,genomic_findings,comorbidities,performance_status\n"
        b"c1,lung,EGFR exon 19 deletion;KRAS G12C,diabetes;hypertension,ECOG 1"
    )
    cases, _ = parse_upload("x.csv", raw)
    assert cases[0].genomic_findings == ["EGFR exon 19 deletion", "KRAS G12C"]
    assert cases[0].patient_factors.comorbidities == ["diabetes", "hypertension"]


def test_parse_csv_rejects_unknown_columns():
    raw = b"case_id,not_a_column\nc1,x"
    with pytest.raises(CaseParseError):
        parse_upload("x.csv", raw)


def test_parse_free_text_extracts_key_fields():
    raw = (
        b"Metastatic lung adenocarcinoma. Follow-up CT shows stable disease with no new lesions. "
        b"Biopsy confirmed adenocarcinoma with EGFR exon 19 deletion. Performance status ECOG 3, "
        b"bed-bound. Patient prefers comfort care and wants to avoid hospitalization."
    )
    cases, warnings = parse_upload("x.txt", raw)
    c = cases[0]
    assert c.cancer_type == "lung"
    assert c.patient_factors.performance_status == "ECOG 3"
    assert "EGFR" in c.genomic_findings
    assert "stable disease" in c.imaging_findings.lower()


def test_parse_free_text_multiple_vignettes():
    raw = b"Lung case with ECOG 1.\n---\nBreast case with ECOG 2."
    cases, _ = parse_upload("x.txt", raw)
    assert len(cases) == 2


def test_unsupported_extension_rejected():
    with pytest.raises(CaseParseError):
        parse_upload("x.pdf", b"whatever")


def test_invalid_json_reports_clearly():
    with pytest.raises(CaseParseError):
        parse_upload("x.json", b"{not valid")
