/* 운동·휴식 카운트다운 (D-5)  담당: 고의찬
 *
 * - 운동 타이머(시간형 운동): [타이머 시작]을 누르면 줄어들고, 0초가 되면 세트 완료 폼을 자동 제출한다.
 * - 휴식 타이머: 화면이 열리면 바로 시작하고, 0초가 되면 다음 운동 화면으로 넘어간다.
 * 시간은 setInterval 횟수가 아니라 시작 시각과의 차이로 계산한다(탭이 백그라운드여도 어긋나지 않게).
 */
(function () {
  function fmt(sec) {
    var m = Math.floor(sec / 60), s = sec % 60;
    return m + ':' + (s < 10 ? '0' : '') + s;
  }

  function countdown(seconds, onTick, onDone) {
    var end = Date.now() + seconds * 1000;
    var last = null;
    function tick() {
      var left = Math.max(0, Math.ceil((end - Date.now()) / 1000));
      if (left !== last) { last = left; onTick(left); }
      if (left <= 0) { clearInterval(id); onDone(); }
    }
    var id = setInterval(tick, 200);
    tick();
    return { stop: function () { clearInterval(id); } };
  }

  function beep() {
    try {
      var ctx = new (window.AudioContext || window.webkitAudioContext)();
      var osc = ctx.createOscillator();
      osc.frequency.value = 880;
      osc.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.25);
    } catch (e) { /* 소리를 못 내도 동작에는 문제없음 */ }
  }

  window.HomefitTimer = {
    workTimer: function (o) {
      var running = null;
      o.button.addEventListener('click', function () {
        if (running) {               // 다시 누르면 일시정지 대신 처음부터
          running.stop(); running = null;
          o.display.textContent = o.seconds;
          o.button.textContent = '타이머 시작';
          return;
        }
        o.button.textContent = '다시 시작';
        running = countdown(o.seconds, function (left) { o.display.textContent = left; }, function () {
          beep();
          o.form.submit();
        });
      });
    },

    restTimer: function (o) {
      countdown(o.seconds, function (left) {
        o.display.textContent = fmt(left);
        if (o.ring) o.ring.setAttribute('stroke-dashoffset', (o.circumference * (1 - left / o.seconds)).toFixed(1));
      }, function () {
        beep();
        window.location.href = o.nextUrl;
      });
    },
  };
})();
