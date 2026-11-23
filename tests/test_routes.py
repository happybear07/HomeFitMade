import io
import json

import pytest

from homefit import create_app


def records_of(app):
    return app.extensions["homefit"].records.all()


def test_first_run_goes_to_setup(client):
    res = client.get("/")
    assert res.status_code == 302 and res.headers["Location"].endswith("/setup")


def test_setup_validation_error_keeps_form(client):
    res = client.post("/setup", data={"height": "175", "weight": "700", "level": "중급"})
    assert res.status_code == 200
    assert "몸무게는 20~300kg 사이로 입력해 주세요" in res.get_data(as_text=True)


def test_setup_saves_and_home_shows_routine(user_client):
    page = user_client.get("/").get_data(as_text=True)
    assert "오늘의 루틴" in page and "중급 · 운동 5개" in page


@pytest.mark.parametrize("stage", ["g0", "g1", "g2", "g3"])
def test_home_stage_preview(user_client, stage):
    page = user_client.get(f"/?stage={stage}").get_data(as_text=True)
    assert f'class="stage-{stage}"' in page


def test_full_workout_flow_saves_one_record(app, user_client):
    user_client.post("/workout/start", data={"part": "전신"})
    for _ in range(100):                     # 세트를 끝까지 누른다
        res = user_client.post("/workout/set-done")
        if res.headers["Location"].endswith("/complete"):
            break
        assert user_client.get(res.headers["Location"]).status_code == 200
    else:
        pytest.fail("루틴이 끝나지 않음")
    page = user_client.get("/complete").get_data(as_text=True)
    assert "태웠어요" in page
    recs = records_of(app)
    assert len(recs) == 1 and recs[0]["completed"] is True
    assert all(it["sets_done"] == it["sets_planned"] for it in recs[0]["items"])
    # 새로고침해도 기록이 늘지 않는다(PRG)
    user_client.get("/complete")
    assert len(records_of(app)) == 1
    # 피드백 저장
    user_client.post("/complete/feedback", data={"feedback": "적당해요"})
    assert records_of(app)[0]["feedback"] == "적당해요"


def test_stop_saves_incomplete_record(app, user_client):
    user_client.post("/workout/start", data={"part": "전신"})
    user_client.post("/workout/set-done")
    res = user_client.post("/workout/stop")
    assert res.headers["Location"].endswith("/")
    recs = records_of(app)
    assert len(recs) == 1 and recs[0]["completed"] is False


def test_stop_without_any_set_saves_nothing(app, user_client):
    user_client.post("/workout/start", data={"part": "전신"})
    user_client.post("/workout/stop")
    assert records_of(app) == []


def test_two_completions_raise_multiplier(app, user_client):
    for _ in range(2):
        user_client.post("/workout/start", data={"part": "코어"})
        while not user_client.post("/workout/set-done").headers["Location"].endswith("/complete"):
            pass
    user = app.extensions["homefit"].users.get()
    assert user["rep_multiplier"] == 1.1
    assert "10% 늘렸어요" in user_client.get("/routine").get_data(as_text=True)


def test_workout_without_session_redirects(user_client):
    assert user_client.get("/workout").headers["Location"].endswith("/routine")


def test_records_page(user_client):
    assert "운동 기록" in user_client.get("/records").get_data(as_text=True)
    assert user_client.get("/records?month=bad").status_code == 200


MP4_HEAD = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 100


def test_upload_valid_mp4(app, client):
    res = client.post("/admin/videos", data={"exercise_id": "push_up", "video": (io.BytesIO(MP4_HEAD), "clip.mp4")},
                      content_type="multipart/form-data")
    assert res.status_code == 302
    assert (app.config["VIDEO_DIR"] / "push_up.mp4").exists()
    assert "26개 중 1개 등록" in client.get("/admin/videos").get_data(as_text=True)
    assert client.get("/videos/push_up.mp4").status_code == 200


def test_upload_rejects_mov(app, client):
    client.post("/admin/videos", data={"exercise_id": "push_up", "video": (io.BytesIO(MP4_HEAD), "squat.mov")},
                content_type="multipart/form-data")
    page = client.get("/admin/videos").get_data(as_text=True)
    assert "squat.mov는 올릴 수 없어요" in page
    assert not (app.config["VIDEO_DIR"] / "push_up.mp4").exists()


def test_upload_rejects_fake_mp4(app, client):
    client.post("/admin/videos", data={"exercise_id": "push_up", "video": (io.BytesIO(b"not a video" * 10), "a.mp4")},
                content_type="multipart/form-data")
    assert not (app.config["VIDEO_DIR"] / "push_up.mp4").exists()


def test_upload_too_large_returns_to_admin(client):
    big = io.BytesIO(MP4_HEAD + b"\x00" * (51 * 1024 * 1024))
    res = client.post("/admin/videos", data={"exercise_id": "push_up", "video": (big, "big.mp4")},
                      content_type="multipart/form-data")
    assert res.status_code == 302
    assert "50MB 이하 파일만" in client.get("/admin/videos").get_data(as_text=True)


def test_broken_exercises_stops_startup(tmp_path):
    (tmp_path / "exercises.json").write_text(json.dumps([{"id": "x"}]), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        create_app({"DATA_DIR": tmp_path, "VIDEO_DIR": tmp_path / "v"})
    assert "필수 항목 없음" in str(e.value)


def test_broken_records_file_is_recovered(app, user_client):
    path = app.config["DATA_DIR"] / "records.json"
    path.write_text("[ 깨짐", encoding="utf-8")
    page = user_client.get("/records", follow_redirects=True).get_data(as_text=True)
    page += user_client.get("/records").get_data(as_text=True)
    assert "저장 파일이 손상돼" in page
