import json

from homefit.storage import jsonfile
from homefit.storage.repos import RecordRepo


def test_missing_file_returns_default(tmp_path):
    assert jsonfile.load_json(tmp_path / "none.json", []) == []


def test_broken_file_is_moved_and_default_returned(tmp_path):
    path = tmp_path / "records.json"
    path.write_text("{ 깨진 파일", encoding="utf-8")
    jsonfile.recovered.clear()
    assert jsonfile.load_json(path, []) == []
    assert not path.exists()
    backups = list(tmp_path.glob("records.broken-*.json"))
    assert len(backups) == 1 and jsonfile.recovered == backups
    jsonfile.recovered.clear()


def test_atomic_save_leaves_no_tmp(tmp_path):
    path = tmp_path / "user.json"
    jsonfile.save_json(path, {"이름": "곰"})
    assert json.loads(path.read_text(encoding="utf-8")) == {"이름": "곰"}
    assert not list(tmp_path.glob("*.tmp"))


def test_record_repo_append_and_update(tmp_path):
    repo = RecordRepo(tmp_path / "records.json")
    rec = repo.append({"date": "2026-11-23", "completed": True})
    assert repo.get(rec["id"])["completed"] is True
    repo.update(rec["id"], feedback="적당해요")
    assert repo.all()[0]["feedback"] == "적당해요"
