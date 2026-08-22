/* ══════════════════════════════════════════════════════════════════════
   Biofluids — flow field plates and filter bars
   ──────────────────────────────────────────────────────────────────────
   Two independent pieces, both progressive: the page is complete without
   either, they only add to it.

   1. Flow fields. Any <canvas data-bf-flow> is painted with a synthetic
      velocity field from a superposition of point vortices, colour-mapped
      through the site palette. These stand in until the lab's own PIV and
      CFD frames are dropped in; a plate holding a real <img> is untouched.

   2. Filter bars. A list may carry several bars (theses filter on status
      and on degree at once), so selections combine: an item survives only
      if it satisfies every bar pointing at its list.
   ══════════════════════════════════════════════════════════════════════ */

(function () {
  "use strict";

  var reduce =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── velocity colourmap: ink, petrol, teal, sand, rust ──────────────── */

  var STOPS = [
    [0.0, [8, 16, 22]],
    [0.3, [14, 74, 86]],
    [0.55, [40, 132, 140]],
    [0.78, [186, 150, 96]],
    [1.0, [206, 102, 62]]
  ];

  function cmap(t) {
    if (t < 0) t = 0;
    if (t > 1) t = 1;
    for (var i = 1; i < STOPS.length; i++) {
      if (t <= STOPS[i][0]) {
        var a = STOPS[i - 1];
        var b = STOPS[i];
        var f = (t - a[0]) / (b[0] - a[0] || 1);
        return [
          a[1][0] + (b[1][0] - a[1][0]) * f,
          a[1][1] + (b[1][1] - a[1][1]) * f,
          a[1][2] + (b[1][2] - a[1][2]) * f
        ];
      }
    }
    return STOPS[STOPS.length - 1][1];
  }

  function fit(cv) {
    var r = cv.getBoundingClientRect();
    if (!r.width || !r.height) return false;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    cv.width = Math.max(2, Math.round(r.width * dpr));
    cv.height = Math.max(2, Math.round(r.height * dpr));
    return true;
  }

  /* Vortex layouts. Each mode is a different flow the lab actually
     measures, so plates across the site do not all look alike. */
  function vortices(mode, seed) {
    var s = seed;
    function rnd() {
      s = (s * 1103515245 + 12345) & 0x7fffffff;
      return s / 0x7fffffff;
    }
    var v = [];
    var i;
    if (mode === "channel") {
      for (i = 0; i < 7; i++) {
        v.push({ x: 0.1 + i * 0.13, y: 0.5 + (i % 2 ? 0.14 : -0.14), g: (i % 2 ? 1 : -1) * 0.03 });
      }
    } else if (mode === "wake") {
      for (i = 0; i < 8; i++) {
        v.push({ x: 0.22 + i * 0.1, y: 0.5 + (i % 2 ? 0.12 : -0.12), g: (i % 2 ? 1 : -1) * 0.038 });
      }
    } else if (mode === "shear") {
      for (i = 0; i < 10; i++) v.push({ x: rnd(), y: rnd(), g: (rnd() - 0.5) * 0.075 });
    } else {
      for (i = 0; i < 4; i++) {
        v.push({ x: 0.22 + rnd() * 0.56, y: 0.22 + rnd() * 0.56, g: (rnd() - 0.42) * 0.11 });
      }
    }
    return v;
  }

  function speedAt(v, x, y) {
    var u = 0;
    var w = 0;
    for (var i = 0; i < v.length; i++) {
      var dx = x - v[i].x;
      var dy = y - v[i].y;
      var r2 = dx * dx + dy * dy + 0.006;
      u += (-v[i].g * dy) / r2;
      w += (v[i].g * dx) / r2;
    }
    return { u: u, w: w, s: Math.sqrt(u * u + w * w) };
  }

  function paintStatic(cv) {
    if (!fit(cv)) return;
    var ctx = cv.getContext("2d");
    var W = cv.width;
    var H = cv.height;
    var vs = vortices(cv.dataset.bfMode || "vortex", parseInt(cv.dataset.bfSeed || "7", 10));
    var step = 2;
    var img = ctx.createImageData(W, H);
    var d = img.data;
    for (var py = 0; py < H; py += step) {
      for (var px = 0; px < W; px += step) {
        var q = speedAt(vs, px / W, py / H);
        var c = cmap(Math.pow(Math.min(q.s / 2.6, 1), 0.62));
        for (var oy = 0; oy < step && py + oy < H; oy++) {
          for (var ox = 0; ox < step && px + ox < W; ox++) {
            var o = ((py + oy) * W + (px + ox)) * 4;
            d[o] = c[0];
            d[o + 1] = c[1];
            d[o + 2] = c[2];
            d[o + 3] = 255;
          }
        }
      }
    }
    ctx.putImageData(img, 0, 0);

    ctx.lineWidth = Math.max(1, W / 440);
    ctx.strokeStyle = "rgba(255,255,255,0.15)";
    for (var n = 0; n < 26; n++) {
      var x = ((n % 6) + 0.5) / 6;
      var y = (Math.floor(n / 6) + 0.5) / 5;
      ctx.beginPath();
      ctx.moveTo(x * W, y * H);
      for (var st = 0; st < 130; st++) {
        var qq = speedAt(vs, x, y);
        var mag = qq.s || 1e-6;
        x += (qq.u / mag) * 0.006;
        y += (qq.w / mag) * 0.006;
        if (x < 0 || x > 1 || y < 0 || y > 1) break;
        ctx.lineTo(x * W, y * H);
      }
      ctx.stroke();
    }
  }

  var stopFns = [];

  function paintAnimated(cv) {
    if (!fit(cv)) return;
    var ctx = cv.getContext("2d");
    var dim = cv.dataset.bfDim === "1";
    var vs = vortices(cv.dataset.bfMode || "vortex", parseInt(cv.dataset.bfSeed || "5", 10));
    var W = cv.width;
    var H = cv.height;
    var parts = [];
    /* Density is per device pixel, so a small plate on a hi-dpi screen still
       carries enough tracers to read as a seeded flow rather than empty ink. */
    var n = Math.round(Math.min(2000, Math.max(400, (W * H) / 1100)));
    for (var i = 0; i < n; i++) {
      parts.push({
        x: Math.random(),
        y: Math.random(),
        life: Math.floor(Math.random() * 300)
      });
    }
    var bg = dim ? "#0A1013" : "#05090B";
    /* A slow fade is what turns moving dots into streamlines; erase
       faster than this and the field reads as scattered dashes. */
    var fade = dim ? "rgba(10,16,19,0.010)" : "rgba(5,9,11,0.012)";
    var speed = dim ? 0.0018 : 0.0028;
    var dot = dim ? 1.6 : 2.1;
    var alpha = dim ? 0.5 : 0.85;
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, W, H);

    /* Speed is bucketed into a fixed set of colours so a frame costs one
       stroke() per bucket instead of one per particle. Stroking each particle
       separately means well over a thousand draw calls a frame across the two
       fields on a page, which starves the renderer: the loop drops to a few
       frames a second and the trails never grow long enough to read as a
       streakline. Same picture, two orders of magnitude fewer calls. */
    var BINS = 7;
    var binColour = [];
    for (var bi = 0; bi < BINS; bi++) {
      var bc = cmap(0.34 + (bi / (BINS - 1)) * 0.66);
      binColour.push(
        "rgba(" + (bc[0] | 0) + "," + (bc[1] | 0) + "," + (bc[2] | 0) + "," + alpha + ")"
      );
    }

    function tick(clear) {
      if (clear) {
        ctx.fillStyle = fade;
        ctx.fillRect(0, 0, W, H);
      }
      ctx.lineWidth = dot;
      ctx.lineCap = "round";

      var paths = [];
      for (var b = 0; b < BINS; b++) paths.push(null);

      for (var j = 0; j < parts.length; j++) {
        var p = parts[j];
        var q = speedAt(vs, p.x, p.y);
        var mag = q.s || 1e-6;
        var nx = p.x + (q.u / mag) * speed;
        var ny = p.y + (q.w / mag) * speed;
        if (nx < -0.02 || nx > 1.02 || ny < -0.02 || ny > 1.02 || p.life > 300) {
          p.x = Math.random();
          p.y = Math.random();
          p.life = 0;
          continue;
        }
        /* Most of a vortex field sits at low speed, so normalise harder than
           the static plates: otherwise the tracers land on the ink end of the
           colourmap and vanish into the background. */
        var t = Math.pow(Math.min(mag / 1.5, 1), 0.55);
        var bin = Math.min(BINS - 1, Math.max(0, Math.round(t * (BINS - 1))));
        if (!paths[bin]) paths[bin] = new Path2D();
        paths[bin].moveTo(p.x * W, p.y * H);
        paths[bin].lineTo(nx * W, ny * H);
        p.x = nx;
        p.y = ny;
        p.life++;
      }

      for (var k2 = 0; k2 < BINS; k2++) {
        if (!paths[k2]) continue;
        ctx.strokeStyle = binColour[k2];
        ctx.stroke(paths[k2]);
      }
    }

    /* Warm the field before showing it. Tracers start scattered, so the first
       second of a cold field is a few disconnected dashes rather than a flow.
       Running the steps up front means the plate is a developed field at first
       paint, which also covers the case where rAF never runs at all: a
       background tab, a reader who scrolls straight past, reduced motion. */
    for (var k = 0; k < 300; k++) tick(true);
    if (reduce) return;
    var raf;
    (function loop() {
      tick(true);
      raf = requestAnimationFrame(loop);
    })();
    stopFns.push(function () {
      cancelAnimationFrame(raf);
    });
  }

  function paintAll() {
    for (var s = 0; s < stopFns.length; s++) stopFns[s]();
    stopFns = [];
    var cvs = document.querySelectorAll("canvas[data-bf-flow]");
    for (var i = 0; i < cvs.length; i++) {
      if (cvs[i].dataset.bfAnim === "1") paintAnimated(cvs[i]);
      else paintStatic(cvs[i]);
    }
  }

  /* ── filter bars ────────────────────────────────────────────────────── */

  function wireFilters() {
    var bars = document.querySelectorAll("[data-bf-target][data-bf-key]");
    var byList = {};
    for (var g = 0; g < bars.length; g++) {
      var t = bars[g].dataset.bfTarget;
      if (!byList[t]) byList[t] = [];
      byList[t].push(bars[g]);
      bars[g].dataset.bfSel = "all";
    }
    Object.keys(byList).forEach(function (target) {
      var list = document.querySelector(target);
      if (!list) return;
      var mine = byList[target];
      var empty = list.parentNode.querySelector(".bf-noresults");

      function apply() {
        var items = list.children;
        var first = true;
        var shown = 0;
        for (var k = 0; k < items.length; k++) {
          var show = true;
          for (var b = 0; b < mine.length; b++) {
            var sel = mine[b].dataset.bfSel;
            if (sel !== "all" && items[k].dataset[mine[b].dataset.bfKey] !== sel) show = false;
          }
          items[k].style.display = show ? "" : "none";
          /* Rows draw their divider as a top border on every item after the
             first, so the first surviving row has to lose its own. */
          if (show) {
            items[k].style.borderTop = first ? "0" : "";
            first = false;
            shown++;
          }
        }
        if (empty) empty.style.display = shown ? "none" : "block";
      }

      mine.forEach(function (bar) {
        var btns = bar.querySelectorAll("button");
        for (var i = 0; i < btns.length; i++) {
          btns[i].addEventListener("click", function () {
            bar.dataset.bfSel = this.dataset.bfF;
            for (var b = 0; b < btns.length; b++) {
              btns[b].setAttribute("aria-pressed", String(btns[b] === this));
            }
            apply();
          });
        }
      });
    });
  }

  function boot() {
    paintAll();
    wireFilters();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();

  var rto;
  window.addEventListener("resize", function () {
    clearTimeout(rto);
    rto = setTimeout(paintAll, 260);
  });
})();
