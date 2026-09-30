import json

from pathlib import Path


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)



def save_json(file_path, data):
    file_path = Path(file_path)

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)



def extract_json_objects(text):
    decoder = json.JSONDecoder()
    objects = []

    for index, character in enumerate(text):
        if character != "{":
            continue

        try:
            obj, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue

        if isinstance(obj, dict):
            objects.append(obj)

    return objects