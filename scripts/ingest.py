import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import DATA_RAW, DATA_PROCESSED

INPUT_FILE = DATA_RAW / "datasets.json"
OUTPUT_FILE = DATA_PROCESSED / "documents.jsonl"


def clean_text(text: str) -> str:
    """Нормализация пробелов и переносов строк."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def load_datasets(path: Path) -> list[dict]:
    """Загружает JSON-массив."""
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Ожидался JSON-массив, получен {type(data)}")
    return data


def ingest_item(item: dict, doc_id: int, source_file: str) -> dict:
    """Преобразует одну запись в документ для JSONL."""
    return {
        "doc_id": doc_id,
        "name": item.get("Название документа", "").strip(),
        "source_file": source_file,
        "text": clean_text(item.get("Текст", "")),
        "comment": clean_text(item.get("Комментарий РГ", "")),
        "link": item.get("Ссылка", "").strip(),
        "date": item.get("Дата", "").strip(),
    }


def write_documents(documents: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")


def run(input_path: Path = INPUT_FILE, output_path: Path = OUTPUT_FILE) -> int:
    if not input_path.exists():
        raise FileNotFoundError(f"Не найден файл: {input_path}")

    source_file = str(input_path.relative_to(ROOT))
    datasets = load_datasets(input_path)
    documents = [ingest_item(item, idx, source_file) for idx, item in enumerate(datasets)]
    write_documents(documents, output_path)
    return len(documents)


def main() -> None:
    try:
        count = run()
        print(f"Записано {count} документов -> {OUTPUT_FILE}")
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
