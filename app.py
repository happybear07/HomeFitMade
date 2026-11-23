"""홈핏 메이트 실행 진입점.

실행: uv run app.py  → 브라우저에서 http://127.0.0.1:5000
"""
from homefit import create_app

app = create_app()

if __name__ == "__main__":
    # use_reloader=False: 리로더가 코드를 두 번 실행해 첫 실행 파일(secret_key)을 두 번 만드는 것을 막는다.
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
