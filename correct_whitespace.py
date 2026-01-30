import json
from whitespace_correction import WhitespaceCorrector
import settings

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

def process_file(input_file, output_file, corrector):
    stats = {"total_lines": 0, "empty_lines": 0, "json_errors": 0, "invalid_text_field": 0, "excluded": 0, "correction_errors": 0, "corrected": 0}
    print("Starting whitespace correction process")
    with open(input_file, "r", encoding="utf-8") as infile, \
         open(output_file, "w", encoding="utf-8") as outfile:
        for line_num, raw_line in enumerate(infile, 1):
            stats["total_lines"] += 1
            result, status = process_json_line(raw_line, line_num, corrector)
            stats[status] += 1
            if result is None:
                outfile.write(raw_line)
            else:
                outfile.write(json.dumps(result, ensure_ascii=False) + "\n")
    return stats

def print_statistics(stats):
    print(f"Total lines:                {stats['total_lines']}")
    print(f"Excluded (label='exclude'): {stats['excluded']}")
    print(f"Successfully corrected:     {stats['corrected']}")
    print(f"Empty lines:                {stats['empty_lines']}")
    print(f"JSON parsing errors:        {stats['json_errors']}")
    print(f"Invalid text fields:        {stats['invalid_text_field']}")
    print(f"Correction errors:          {stats['correction_errors']}")
    print(f"Processed lines written to {settings.OUTPUT_FILE}")

def main():
    corrector = WhitespaceCorrector.from_pretrained(settings.MODEL_IDENTIFIER, device=settings.DEVICE)
    stats = process_file(input_file=settings.INPUT_FILE, output_file=settings.OUTPUT_FILE, corrector=corrector)
    print_statistics(stats)

if __name__ == "__main__":
    main()

