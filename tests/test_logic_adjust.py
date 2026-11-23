from homefit.logic.adjust import next_multiplier


def r(completed, mult=1.0, feedback=None):
    return {"completed": completed, "multiplier": mult, "feedback": feedback}


def test_two_completions_increase():
    assert next_multiplier([r(True), r(True)], 1.0) == (1.1, "최근 2번 모두 끝까지 해서 횟수를 10% 늘렸어요")


def test_one_completion_keeps():
    assert next_multiplier([r(True)], 1.0) == (1.0, None)


def test_two_of_three_stopped_decrease():
    new, reason = next_multiplier([r(True), r(False), r(False)], 1.0)
    assert new == 0.9 and reason


def test_needs_two_completions_at_new_multiplier():
    # 1.0에서 2번 완료해 1.1이 된 직후, 1.1로 1번만 끝냈으면 그대로
    assert next_multiplier([r(True), r(True), r(True, 1.1)], 1.1) == (1.1, None)
    assert next_multiplier([r(True), r(True), r(True, 1.1), r(True, 1.1)], 1.1)[0] == 1.21


def test_upper_and_lower_bounds():
    assert next_multiplier([r(True, 1.3), r(True, 1.3)], 1.3) == (1.3, None)
    assert next_multiplier([r(True, 1.25), r(True, 1.25)], 1.25)[0] == 1.3
    assert next_multiplier([r(False, 0.7), r(False, 0.7)], 0.7) == (0.7, None)
    assert next_multiplier([r(False, 0.75), r(False, 0.75)], 0.75)[0] == 0.7


def test_hard_feedback_blocks_increase():
    assert next_multiplier([r(True), r(True, feedback="힘들었어요")], 1.0) == (1.0, None)
