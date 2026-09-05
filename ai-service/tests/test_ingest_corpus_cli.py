import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from scripts.ingest_corpus import discover_case_files

def test_discover_case_files(tmp_path):
    case_dir = tmp_path / "C-TEST"
    case_dir.mkdir()
    
    (case_dir / "test_report.txt").write_text("dummy")
    (case_dir / "test_image.jpg").write_text("dummy")
    
    struct_cdr = case_dir / "structured" / "cdr"
    struct_cdr.mkdir(parents=True)
    (struct_cdr / "data.csv").write_text("dummy")
    
    files = discover_case_files(case_dir)
    assert len(files) == 3
    
    txt = next(f for f in files if f['file_type'] == 'TXT')
    assert txt['route'] == 'UNSTRUCTURED'
    assert txt['category'] == 'REPORT'
    
    img = next(f for f in files if f['file_type'] == 'JPG')
    assert img['route'] == 'UNSTRUCTURED'
    assert img['category'] == 'IMAGE'
    
    csv = next(f for f in files if f['file_type'] == 'CSV')
    assert csv['route'] == 'STRUCTURED'
    assert csv['dataset_id'] == 'NETRA-DEMO-CDR'

