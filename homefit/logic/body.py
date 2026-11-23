"""BMI (A-3). 기준: 대한비만학회 비만 진료지침 2022."""

# (상한 미만, 분류) — 경계는 "이상/미만"
_CATEGORIES = (
    (18.5, "저체중"),
    (23.0, "정상"),
    (25.0, "비만 전단계(과체중)"),
    (30.0, "1단계 비만"),
)
OBESE_BMI = 25.0   # 이 값 이상이면 관절 부담 '높음' 운동을 대체한다


def bmi(height_cm: float, weight_kg: float) -> float:
    """반올림하지 않은 값을 돌려준다. 화면에 보일 때만 소수 첫째 자리로 줄인다."""
    m = height_cm / 100
    return weight_kg / (m * m)


def bmi_category(value: float) -> str:
    for upper, name in _CATEGORIES:
        if value < upper:
            return name
    return "2단계 이상 비만"
