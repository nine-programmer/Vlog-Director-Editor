/* Style: camcorder (90s home video: viewfinder brackets, REC, tape counter, scanlines, colour-fringed type). */
(function () {
  const FRINGE = 'text-shadow:3px 0 rgba(255,40,40,.8),-3px 0 rgba(40,200,255,.8),0 3px 10px rgba(0,0,0,.6)';
  const HUD = `position:absolute;font-family:'VT323';color:#fff;white-space:nowrap;line-height:1;${FRINGE}`;
  const jitter = (e, rem) => ({
    dx: e < .15 ? Math.sin(e * 200) * 12 * (1 - e / .15) : 0,
    o: (e < .05 ? .4 : 1) * Math.min(rem / .08, 1),
  });
  const pad = (n) => String(n).padStart(2, '0');
  registerStyle({
    name: 'camcorder',
    holdFps: null,
    ink: '#ffffff',
    accent: '#ff3b3b',
    highlight: '#ffe66b',
    stickerCss: 'filter:drop-shadow(3px 0 rgba(255,40,40,.7)) drop-shadow(-3px 0 rgba(40,200,255,.7))',
    css: `
      .style-camcorder .ct{font-family:var(--display,'Chakra Petch');font-weight:700;white-space:nowrap;line-height:1.45;color:#fff;${FRINGE}}
      .style-camcorder .cbox{background:rgba(0,0,0,.55);padding:2px 22px}
      .style-camcorder .cstamp{font-family:var(--display,'Chakra Petch');font-weight:700;font-size:60px;color:#fff;border:5px solid #fff;padding:0 28px;white-space:nowrap;line-height:1.4;${FRINGE}}`,
    text(kind, text, seed, cue, a) {
      const c = cue.color;
      const map = {
        speech: ['ct', `font-size:52px;${c ? 'color:' + c : ''}`],
        voice: ['ct', `font-size:50px;color:${c || '#ffe66b'}`],
        comment: ['ct cbox', `font-size:46px;${c ? 'color:' + c : ''}`],
        label: ['ct cbox', `font-size:36px;letter-spacing:.08em;${c ? 'color:' + c : ''}`],
        score: ['ct', `font-size:60px;color:${c || '#ffe66b'}`],
        tag: ['ct cbox', `font-size:32px;${c ? 'color:' + c : ''}`],
      }[kind];
      return a.U.node('div', `ob ${map[0]}`, map[1], text);
    },
    word(w, k, seed, cue, a) {
      return a.U.node('div', 'ob ct', `font-size:${cue.size || 130}px;letter-spacing:.04em;${cue.color ? 'color:' + cue.color : ''}`, w);
    },
    wordGap: 24,
    stamp(text, cue, a) { return a.U.node('div', 'ob cstamp', '', text); },
    anim: {default: jitter, impact: jitter, stamp: jitter},
    frame(a) {
      const {U, C, root} = a, {W, H, win, framed} = a.geo;
      const top = framed ? win.y : 0, h = framed ? win.h : H;
      if (framed) {
        root.appendChild(U.node('div', '', `position:absolute;left:0;top:0;width:${W}px;height:${top}px;background:#000`));
        root.appendChild(U.node('div', '', `position:absolute;left:0;top:${top + h}px;width:${W}px;height:${H - top - h}px;background:#000`));
      }
      root.appendChild(U.node('div', '', `position:absolute;left:0;top:${top}px;width:${W}px;height:${h}px;background:repeating-linear-gradient(0deg,rgba(0,0,0,.16) 0 2px,transparent 2px 6px)`));
      const m = 44, L = 70, b = '6px solid #fff';
      [[m, top + m, `border-left:${b};border-top:${b}`], [W - m - L, top + m, `border-right:${b};border-top:${b}`],
       [m, top + h - m - L, `border-left:${b};border-bottom:${b}`], [W - m - L, top + h - m - L, `border-right:${b};border-bottom:${b}`]]
        .forEach(([x, y, css]) => root.appendChild(U.node('div', '', `position:absolute;left:${x}px;top:${y}px;width:${L}px;height:${L}px;box-sizing:border-box;${css}`)));
      /* REC sits top-right because labels use the top-left; the date and counter share the bottom line, below the captions. */
      const low = H - top - h + m + 8;
      const rec = U.node('div', '', `${HUD};right:${m + 44}px;top:${top + m + 36}px;font-size:64px;display:flex;align-items:center;gap:16px`,
        '<i style="width:28px;height:28px;border-radius:50%;background:#ff2a2a"></i>REC');
      const dot = rec.firstChild;
      const counter = U.node('div', '', `${HUD};right:${m + 44}px;bottom:${low}px;font-size:56px`);
      root.appendChild(rec); root.appendChild(counter);
      let date = null;
      if (C.postmarks) {
        date = U.node('div', '', `${HUD};left:${m + 44}px;bottom:${low}px;font-size:56px`);
        root.appendChild(date);
      }
      a.decor.push((t) => {
        dot.style.visibility = t % 1.2 < .7 ? 'visible' : 'hidden';
        const s = Math.floor(t + 1e-6), text = `SP ${Math.floor(s / 3600)}:${pad(Math.floor(s / 60) % 60)}:${pad(s % 60)}`;
        if (counter.textContent !== text) counter.textContent = text;
        if (date) {
          const text = U.latest(C.postmarks, t).lines.join('  ');
          if (date.textContent !== text) date.textContent = text;
        }
      });
    },
    transitions: {
      default: glitch,
      glitch,
    },
  });

  function glitch(a, cue, seed) {
    const {U, root} = a, {W, H} = a.geo;
    const el = U.node('div', 'ob', `width:${W}px;height:${H}px;overflow:hidden`);
    const black = U.node('div', '', `position:absolute;inset:0;background:${cue.color || '#000'}`);
    el.appendChild(black);
    const bars = [];
    for (let i = 0; i < 8; i++) {
      const bar = U.node('div', '', `position:absolute;left:0;width:${W}px;background:${['#fff', '#ff2a2a', '#28c8ff', '#fff'][i % 4]}`);
      el.appendChild(bar); bars.push(bar);
    }
    root.appendChild(el);
    a.items.push({el, cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      el.style.display = on ? '' : 'none';
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t), step = Math.floor(t * 25 + 1e-6);
      black.style.opacity = p > .3 && p < .7 ? 1 : 0;
      bars.forEach((bar, i) => {
        const r = U.hash(step * 13 + seed + i), r2 = U.hash(step * 29 + seed + i * 7);
        bar.style.top = r * H + 'px';
        bar.style.height = 6 + r2 * 60 + 'px';
        bar.style.opacity = .35 + r2 * .5;
        bar.style.transform = `translate(${(r - .5) * 120}px,0)`;
      });
    }});
  }
})();
