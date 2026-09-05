import os
import csv
import httpx
import argparse
import sys
from pathlib import Path
from collections import defaultdict
import uuid

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def load_provenance_csv(csv_path: str):
    prov = {}
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                local_path = row.get("local_path")
                if local_path:
                    # Normalize slashes
                    lp = local_path.replace("\\", "/")
                    prov[lp] = row
    return prov

def discover_case_files(case_dir: Path):
    discovered = []
    case_id = case_dir.name
    for root, dirs, files in os.walk(case_dir):
        for f in files:
            if f.endswith('.yaml'): continue
            
            full_path = Path(root) / f
            rel_path = full_path.relative_to(case_dir)
            rel_str = str(rel_path).replace("\\", "/")
            
            ext = full_path.suffix.lower()
            
            # Determine category and route
            route = None
            category = None
            dataset_id = None
            
            if "structured/cdr" in rel_str:
                route = "STRUCTURED"
                category = "CDR"
                dataset_id = "NETRA-DEMO-CDR"
            elif "structured/financial" in rel_str:
                route = "STRUCTURED"
                category = "FINANCIAL"
                dataset_id = "NETRA-DEMO-TXN"
            elif "structured/vehicle" in rel_str:
                route = "STRUCTURED"
                category = "VEHICLE"
                dataset_id = "NETRA-DEMO-VEHICLE"
            elif "structured/other" in rel_str:
                route = "STRUCTURED"
                category = "OTHER"
                dataset_id = "NETRA-DEMO-OTHER"
            else:
                # Unstructured or root file
                route = "UNSTRUCTURED"
                if ext in ['.txt', '.pdf', '.doc', '.docx']:
                    category = "REPORT"
                elif ext in ['.jpg', '.jpeg', '.png']:
                    category = "IMAGE"
                elif ext in ['.mp3', '.wav']:
                    category = "AUDIO"
                elif ext in ['.mp4', '.avi', '.mkv']:
                    category = "VIDEO"
                else:
                    category = "UNKNOWN"
            
            discovered.append({
                "case_id": case_id,
                "filepath": str(full_path.absolute()),
                "rel_path": rel_str,
                "route": route,
                "category": category,
                "dataset_id": dataset_id,
                "file_type": ext.lstrip('.').upper()
            })
            
    return discovered

def ingest_case(case_dir: Path, prov_map: dict, dry_run: bool):
    case_id = case_dir.name
    files = discover_case_files(case_dir)
    
    if not files:
        print(f"[WARNING] No files found for case {case_id}")
        return files
        
    print(f"\n--- Ingesting Case: {case_id} ---")
    
    if not dry_run:
        # Ensure Case exists in DB
        case_payload = {
            "case_id": case_id,
            "case_number": f"{case_id}-FIR",
            "title": f"Corpus Case {case_id}",
            "description": "Auto-created during corpus ingestion"
        }
        try:
            resp = httpx.post(f"{API_BASE_URL}/api/v1/cases", json=case_payload, timeout=10.0)
            if resp.status_code == 400:
                pass # Already exists
            else:
                resp.raise_for_status()
                print(f"   [INFO] Created new case {case_id} in DB.")
        except Exception as e:
            print(f"   [WARNING] Failed to ensure case exists: {e}")
            
    for df in files:
        # Check provenance map
        lookup_key = f"{case_id}/{df['rel_path']}"
        prov = prov_map.get(lookup_key, {})
        
        system_id = "SYS_UNKNOWN"
        if prov:
            # We could use source_name from CSV if needed, default to unknown
            pass
            
        if dry_run:
            print(f"-> [DRY-RUN] Would ingest {df['route']}: {df['rel_path']} (Category: {df['category']})")
            continue
            
        if df['route'] == "STRUCTURED":
            print(f"-> Ingesting STRUCTURED: {df['rel_path']} ({df['dataset_id']})")
            payload = {
                "filepath": df['filepath'],
                "file_type": df['file_type'],
                "system_id": system_id,
                "dataset_id": df["dataset_id"],
                "case_id": case_id
            }
            try:
                resp = httpx.post(f"{API_BASE_URL}/api/v1/ingestion/batch/structured", json=payload, timeout=60.0)
                resp.raise_for_status()
                print(f"   [SUCCESS] Batch ID: {resp.json().get('batch_id')}")
            except httpx.HTTPError as e:
                print(f"   [FAILED] API Request failed: {e}")
                if hasattr(e, 'response') and getattr(e, 'response', None):
                    print(f"   Response: {e.response.text}")
        else:
            print(f"-> Ingesting UNSTRUCTURED: {df['rel_path']}")
            payload = {
                "filepath": df['filepath'],
                "file_type": df['category'] if df['category'] in ['IMAGE', 'AUDIO', 'VIDEO'] else 'TXT',
                "case_id": case_id
            }
            try:
                resp = httpx.post(f"{API_BASE_URL}/api/v1/ingestion/batch/unstructured", json=payload, timeout=60.0)
                resp.raise_for_status()
                print(f"   [SUCCESS] Batch ID: {resp.json().get('batch_id')}")
            except httpx.HTTPError as e:
                print(f"   [FAILED] API Request failed: {e}")
                if hasattr(e, 'response') and getattr(e, 'response', None):
                    print(f"   Response: {e.response.text}")
                    
    return files

def main():
    parser = argparse.ArgumentParser(description="NETRA Corpus Ingestion CLI (No Manifest Required)")
    parser.add_argument("--corpus", type=str, help="Ingest all cases in corpus root directory")
    parser.add_argument("--case", type=str, help="Ingest a specific case folder directly")
    parser.add_argument("--dry-run", action="store_true", help="Print discovery output without mutating DB")
    
    args = parser.parse_args()
    
    if not args.corpus and not args.case:
        parser.print_help()
        sys.exit(1)
        
    prov_map = {}
    cases = []
    
    if args.corpus:
        corpus_path = Path(args.corpus)
        csv_path = corpus_path / "MULTIMEDIA_ACQUISITION_REPORT.csv"
        prov_map = load_provenance_csv(str(csv_path))
        
        for item in corpus_path.iterdir():
            if item.is_dir() and item.name.startswith("C-"):
                cases.append(item)
    elif args.case:
        case_path = Path(args.case)
        csv_path = case_path.parent / "MULTIMEDIA_ACQUISITION_REPORT.csv"
        prov_map = load_provenance_csv(str(csv_path))
        cases.append(case_path)
        
    print("==================================================")
    print("NETRA CORPUS DISCOVERY")
    print("==================================================")
    
    all_files = []
    
    # Discovery phase
    stats = {}
    for c in sorted(cases):
        c_files = discover_case_files(c)
        all_files.extend(c_files)
        
        cat_counts = defaultdict(int)
        for f in c_files:
            cat_counts[f['category']] += 1
            
        print(f"\n{c.name}")
        print(f"  TXT/Reports: {cat_counts['REPORT']}")
        print(f"  Images:      {cat_counts['IMAGE']}")
        print(f"  Audio:       {cat_counts['AUDIO']}")
        print(f"  Video:       {cat_counts['VIDEO']}")
        print(f"  CDR:         {cat_counts['CDR']}")
        print(f"  Financial:   {cat_counts['FINANCIAL']}")
        print(f"  Vehicle:     {cat_counts['VEHICLE']}")
        print(f"  Other:       {cat_counts['OTHER']}")
        
    print("\n==================================================")
    print(f"TOTAL FILES DISCOVERED: {len(all_files)}")
    print("==================================================\n")
    
    for c in sorted(cases):
        ingest_case(c, prov_map, args.dry_run)
        
if __name__ == "__main__":
    main()
