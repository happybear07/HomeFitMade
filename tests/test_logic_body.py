import pytest

from homefit.logic.body import bmi, bmi_category


@pytest.mark.parametrize("value, expected", [
    (18.49, "저체중"), (18.5, "정상"), (22.99, "정상"), (23.0, "비만 전단계(과체중)"),
    (24.99, "비만 전단계(과체중)"), (25.0, "1단계 비만"), (29.99, "1단계 비만"), (30.0, "2단계 이상 비만"),
])
def test_category_boundaries(value, expected):
    assert bmi_category(value) == expected


def test_bmi_value():
    assert bmi(175, 70) == pytest.approx(22.857, abs=1e-3)


def test_category_uses_unrounded_value():
    # 24.96은 화면에 25.0으로 보이지만 분류는 비만 전단계(5-1)
    assert bmi_category(24.96) == "비만 전단계(과체중)"
