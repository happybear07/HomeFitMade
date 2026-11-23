import math


def round_half_up(x: float) -> int:
    """사람이 기대하는 반올림. 16.5 → 17.

    파이썬 round()는 은행가 반올림이라 round(16.5) == 16이 되므로 횟수 계산에 쓰지 않는다.
    """
    return math.floor(x + 0.5)
