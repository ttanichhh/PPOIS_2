from __future__ import annotations

from pathlib import Path

from src.config_loader import load_json, save_json


class RecordManager:
    def __init__(self, path: str):
        self.path = Path(path)
        self.records = self.load()

    def load(self) -> list[dict[str, int | str]]:
        if not self.path.exists():
            default = {'records': []}
            save_json(self.path, default)
            return []

        data = load_json(self.path)
        return data.get('records', [])

    def save(self) -> None:
        save_json(self.path, {'records': self.records})

    def add_record(self, name: str, score: int) -> None:
        self.records.append({'name': name, 'score': score})
        self.records.sort(key=lambda item: int(item['score']), reverse=True)
        self.records = self.records[:10]
        self.save()

    def best_score(self) -> int:
        if not self.records:
            return 0
        return int(self.records[0]['score'])
