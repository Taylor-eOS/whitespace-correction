import json
from pathlib import Path
from whitespace_correction import WhitespaceCorrector
import settings

def get_output_file(input_file):
    p = Path(input_file)
    return str(p.with_name(f"output_{p.stem}").with_suffix(p.suffix))

def process_json_line(line, line_num, corrector):
    line = line.rstrip()
    if not line:
        return None, "empty_line"
    try:
        data = json.loads(line)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON on line {line_num}: {e}")
        return None, "json_error"
    if "text" not in data or not isinstance(data["text"], str):
        return data, "invalid_text_field"
    if data.get("label") == "exclude":
        return data, "excluded"
    input_text = data["text"]
    try:
        clean = corrector.correct_text(input_text)
        data["text"] = clean
        cl_len = len(clean)
        print(f"{cl_len:<4} {clean[:85].strip()}{'...' if cl_len > 85 else ''}")
        return data, "corrected"
    except Exception as e:
        print(f"Error correcting text on line {line_num}: {e}")
        return data, "correction_error"

def process_text_line(line, line_num, corrector):
    line = line.rstrip("\n")
    if not line.strip():
        return None, "empty_line"
    try:
        clean = corrector.correct_text(line)
        cl_len = len(clean)
        print(f"{cl_len:<4} {clean[:85].strip()}{'...' if cl_len > 85 else ''}")
        return clean, "corrected"
    except Exception as e:
        print(f"Error correcting text on line {line_num}: {e}")
        return line, "correction_error"

def process_file(input_file, output_file, corrector):
    stats = {"total_lines": 0, "empty_line": 0, "json_error": 0, "invalid_text_field": 0, "excluded": 0, "correction_error": 0, "corrected": 0}
    print("Starting whitespace correction")
    is_text = Path(input_file).suffix.lower() == ".txt"
    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        for line_num, raw_line in enumerate(infile, 1):
            stats["total_lines"] += 1
            if is_text:
                result, status = process_text_line(raw_line, line_num, corrector)
                stats[status] += 1
                if result is None:
                    outfile.write(raw_line)
                else:
                    outfile.write(result.rstrip("\n") + "\n")
            else:
                result, status = process_json_line(raw_line, line_num, corrector)
                stats[status] += 1
                if result is None:
                    outfile.write(raw_line)
                else:
                    outfile.write(json.dumps(result, ensure_ascii=False) + "\n")
    return stats

def print_statistics(stats):
    def _get(*keys):
        for k in keys:
            if k in stats:
                return stats[k]
        return None
    total = _get("total_lines")
    if total is not None:
        print(f"Total lines:                {total}")
    excluded = _get("excluded")
    if excluded is not None:
        print(f"Excluded (label='exclude'): {excluded}")
    corrected = _get("corrected")
    if corrected is not None:
        print(f"Successfully corrected:     {corrected}")
    empty = _get("empty_line", "empty_lines")
    if empty is not None:
        print(f"Empty lines:                {empty}")
    json_err = _get("json_error", "json_errors")
    if json_err is not None:
        print(f"JSON parsing errors:        {json_err}")
    invalid = _get("invalid_text_field")
    if invalid is not None:
        print(f"Invalid text fields:        {invalid}")
    corr_err = _get("correction_error", "correction_errors")
    if corr_err is not None:
        print(f"Correction errors:          {corr_err}")

if __name__ == "__main__":
    INPUT_FILE = input('Input file: ') or settings.INPUT_DEFAULT
    OUTPUT_FILE = get_output_file(INPUT_FILE)
    corrector = WhitespaceCorrector.from_pretrained(settings.MODEL_IDENTIFIER, device=settings.DEVICE)
    stats = process_file(input_file=INPUT_FILE, output_file=OUTPUT_FILE, corrector=corrector)
    print_statistics(stats)
    print(f"Processed lines written to {OUTPUT_FILE}")

