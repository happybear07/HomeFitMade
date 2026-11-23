"""
운동 공백 단계 결정 (담당: 장선민)

마지막 운동 후 지난 일수(days)를 받아 4단계 중 하나를 고른다.
key 값은 CSS 클래스(stage-happy 등)와 마스코트 그림 파일 이름으로 그대로 쓰인다.
"""

STAGES = [
    # (최대 일수, key, 이름, 홈 화면 문구)
    (2, "happy", "좋아요", "오늘도 같이 움직여볼까요?"),
    (6, "sad", "시무룩", "조금 쉬었네요. 오늘은 운동할까요?"),
    (13, "angry", "화남", "일주일 넘게 쉬었어요! 지금 바로 시작해요."),
]
LAST = ("faint", "쓰러짐", "2주 넘게 쉬어서 세상이 흑백이 됐어요. 운동하면 색이 돌아와요.")


def get_stage(days):
    """days가 None이면 아직 운동 기록이 없는 첫 사용자다."""
    if days is None:
        return {"key": "happy", "name": "처음", "message": "첫 운동을 시작해볼까요?"}
    for max_days, key, name, message in STAGES:
        if days <= max_days:
            return {"key": key, "name": name, "message": message}
    key, name, message = LAST
    return {"key": key, "name": name, "message": message}
