import json
import shutil
from pathlib import Path

import pytest

from homefit import create_app
from homefit.models import Exercise

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


@pytest.fixture(scope="session")
def raw_exercises():
    return json.loads((DATA / "exercises.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def exercises(raw_exercises):
    return [Exercise.from_dict(d) for d in raw_exercises]


@pytest.fixture(scope="session")
def by_id(exercises):
    return {e.id: e for e in exercises}


@pytest.fixture
def app(tmp_path):
    """실제 data/ 폴더를 건드리지 않도록 임시 폴더에 exercises.json만 복사해서 앱을 만든다."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    shutil.copy(DATA / "exercises.json", data_dir / "exercises.json")
    app = create_app({"DATA_DIR": data_dir, "VIDEO_DIR": tmp_path / "videos", "TESTING": True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user_client(client):
    """정보 입력을 마친 상태(175cm, 70kg, 중급)."""
    client.post("/setup", data={"height": "175", "weight": "70", "level": "중급"})
    return client
