import json
import os
import pandas as pd
import yaml
import xml.etree.ElementTree as ET

from AI.ai_client import call_llm


def generate_ai_data(prompt: str):

    raw = call_llm(prompt)

    raw = raw.strip()

    # chặn expression kiểu JS
    if ".repeat(" in raw:
        print("AI sinh expression repeat - bỏ vòng")
        return []

    try:
        data = json.loads(raw)

    except Exception:

        start = raw.find("[")
        end = raw.rfind("]")

        if start != -1 and end != -1:
            json_text = raw[start:end + 1]

            try:
                data = json.loads(json_text)
            except Exception:
                print("\nAI trả JSON lỗi - bỏ vòng")
                print(raw)
                return []
        else:
            print("\nAI trả JSON lỗi - bỏ vòng")
            print(raw)
            return []

    if isinstance(data, dict):
        data = [data]

    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
        data = [{"value": v} for v in data]

    return data


def write_files(data, folder, formats):

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    # cấu trúc đúng: data/<folder>/
    output_dir = os.path.join(
        base_dir,
        "data",
        folder
    )

    os.makedirs(output_dir, exist_ok=True)

    df = pd.DataFrame(data)

    for ext in formats:

        path = os.path.join(
            output_dir,
            f"data_{folder}_ai.{ext}"
        )

        if ext == "csv":
            df.to_csv(path, index=False, encoding="utf-8-sig")

        elif ext == "xlsx":
            df.to_excel(path, index=False)

        elif ext == "json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        elif ext in ["yaml", "yml"]:
            with open(path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)

        elif ext == "txt":
            with open(path, "w", encoding="utf-8") as f:
                for row in data:
                    f.write(",".join(str(v) for v in row.values()) + "\n")

        elif ext == "xml":

            root = ET.Element("data")

            for row in data:

                item = ET.SubElement(root, "item")

                for k, v in row.items():

                    child = ET.SubElement(item, k)
                    child.text = str(v)

            tree = ET.ElementTree(root)
            tree.write(path, encoding="utf-8", xml_declaration=True)

        print("Saved:", path)