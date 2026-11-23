"""경로와 상수. 숫자를 바꿀 일이 있으면 여기만 고친다."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"
VIDEO_DIR = ROOT / "static" / "videos"
TEMPLATE_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"

EXERCISE_FILE = "exercises.json"   # 읽기 전용
USER_FILE = "user.json"
RECORD_FILE = "records.json"
SECRET_FILE = "secret_key"

MAX_UPLOAD_MB = 50

# 정보 입력 허용 범위 (A-2)
HEIGHT_RANGE = (100, 250)
WEIGHT_RANGE = (20, 300)
