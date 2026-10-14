import os
import sys
import json
import argparse

# Add parent directory of scripts (which is testvkr-service) to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.docx_parser import DocxParser
from parsers.pdf_parser import PdfParser
from checkers.entry_document import EntryDocumentChecker
from checkers.word_format import WordFormatChecker
from checkers.pictures import PicturesChecker
from checkers.structure import StructureChecker
from checkers.dictionary import DictionaryChecker

def find_codex_dir():
    for item in os.listdir("D:\\"):
        if item.startswith("Codex"):
            return os.path.join("D:\\", item)
    return r"D:\Codex项Ŀ"

def load_confidence_map():
    confidence_map = {}
    try:
        rules_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rules", "rules_verified.json")
        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8-sig") as f:
                rules_data = json.load(f)
                for r in rules_data.get("rules", []):
                    confidence_map[r["rule_id"]] = r["confidence"]
    except Exception as e:
        print(f"Warning: Could not load rules_verified.json: {e}")
    return confidence_map

def run_checks_on_file(file_path, confidence_map, skip_structure=False, skip_pictures=False, skip_word_format=False, skip_dictionary=False, work_type="bachelor"):
    ext = os.path.splitext(file_path)[1].lower()
    file_type = 'docx' if ext == '.docx' else 'pdf'

    # 1. Parse
    try:
        if file_type == 'docx':
            parser = DocxParser(file_path)
            doc_data = parser.parse_all()
        else:
            parser = PdfParser(file_path)
            doc_data = parser.parse_all()
    except Exception as e:
        # Fallback for parsing errors
        return [{
            "rule_id": "Entry.DocumentParsingError",
            "module": "entry_document",
            "severity": "critical",
            "message": f"Ошибка при разборе содержимого документа: {str(e)}",
            "confidence": "high"
        }]

    # 2. Run checkers
    findings = []

    # Entry Checker
    entry_checker = EntryDocumentChecker(doc_data, file_type, work_type)
    findings.extend(entry_checker.check())

    is_empty_or_protected = any(f.code in ["Entry.DocumentEmpty", "Entry.DocumentProtected"] for f in findings)

    if not is_empty_or_protected:
        # Structure Checker
        if not skip_structure:
            structure_checker = StructureChecker(doc_data, file_type, work_type)
            findings.extend(structure_checker.check())

        # Pictures Checker
        if not skip_pictures:
            pictures_checker = PicturesChecker(doc_data, file_type, work_type)
            findings.extend(pictures_checker.check())

        # Word Format Checker
        if not skip_word_format:
            word_checker = WordFormatChecker(doc_data, file_type, work_type)
            findings.extend(word_checker.check())

        # Dictionary Checker
        if not skip_dictionary:
            dict_checker = DictionaryChecker(doc_data, file_type, work_type)
            findings.extend(dict_checker.check())

    # Format output findings
    formatted_findings = []
    for f in findings:
        formatted_findings.append({
            "rule_id": f.code,
            "module": f.module.value,
            "severity": f.severity.value,
            "message": f.message,
            "confidence": confidence_map.get(f.code, "medium"),
            "threshold": f.threshold,
            "location": f.location
        })

    return formatted_findings

def main():
    parser = argparse.ArgumentParser(description="Run TestVkr Python checkers on sample documents.")
    parser.add_argument("--samples", type=str, help="Path to p1_dynamic_samples folder")
    parser.add_argument("--out", type=str, default="results_plugin.json", help="Path to output JSON file")
    parser.add_argument("--skip-structure", action="store_true", help="Skip structural checks")
    parser.add_argument("--skip-pictures", action="store_true", help="Skip picture checks")
    parser.add_argument("--skip-word-format", action="store_true", help="Skip formatting checks")
    parser.add_argument("--skip-dictionary", action="store_true", help="Skip dictionary checks")
    parser.add_argument("--work-type", type=str, default="bachelor", help="Work type (bachelor/master/phd/specialist)")
    args = parser.parse_args()

    # Determine samples directory
    samples_dir = args.samples
    if not samples_dir:
        codex_dir = find_codex_dir()
        samples_dir = os.path.join(codex_dir, "analysis_TestVkr", "p1_dynamic_samples")

    if not os.path.exists(samples_dir):
        print(f"Error: Samples directory not found at {samples_dir}")
        sys.exit(1)

    print(f"Scanning samples in: {samples_dir}")
    confidence_map = load_confidence_map()

    results = {}

    # Walk through the directories and find all docx/pdf files
    for root, dirs, files in os.walk(samples_dir):
        for file in files:
            if file.lower().endswith(('.docx', '.pdf')):
                file_path = os.path.join(root, file)
                # Get relative path for cleaner output keys
                rel_path = os.path.relpath(file_path, samples_dir)
                print(f"Processing: {rel_path}...")

                findings = run_checks_on_file(
                    file_path,
                    confidence_map,
                    skip_structure=args.skip_structure,
                    skip_pictures=args.skip_pictures,
                    skip_word_format=args.skip_word_format,
                    skip_dictionary=args.skip_dictionary,
                    work_type=args.work_type
                )
                results[rel_path] = {
                    "file_name": file,
                    "findings_count": len(findings),
                    "findings": findings
                }

    # Write out findings
    out_path = args.out
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Processed {len(results)} files. Results written to {out_path}")

if __name__ == "__main__":
    main()
