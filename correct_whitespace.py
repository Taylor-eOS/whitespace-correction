import json
from whitespace_correction import WhitespaceCorrector
import settings

corrector = WhitespaceCorrector.from_pretrained(settings.MODEL_IDENTIFIER, device=settings.DEVICE)

with open(settings.INPUT_FILE, "r", encoding="utf-8") as infile, open(settings.OUTPUT_FILE, "w", encoding="utf-8") as outfile:
    for line_num, raw_line in enumerate(infile, 1):
        line = raw_line.rstrip()
        if not line:
            outfile.write(raw_line)
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON on line {line_num}: {e}")
            outfile.write(raw_line)
            continue
        if "text" not in data or not isinstance(data["text"], str):
            outfile.write(json.dumps(data, ensure_ascii=False) + "\n")
            continue
        if data.get("label") == "exclude":
            outfile.write(json.dumps(data, ensure_ascii=False) + "\n")
            continue
        input_text = data["text"]
        try:
            clean = corrector.correct_text(input_text)
            data["text"] = clean
        except Exception as e:
            print(f"Error correcting text on line {line_num}: {e}")
        outfile.write(json.dumps(data, ensure_ascii=False) + "\n")
    print("Finished process")

