/* Style: splash (thin white type with bright liquid strokes that sweep past the words). */
(function () {
  const COLORS = ['#1fb6ff', '#ff1f6b', '#8be21a', '#ffc21f', '#b51fff'];
  const DARK = '#101014';
  const SHADOW = 'text-shadow:0 2px 12px rgba(0,0,0,.6),0 0 2px rgba(0,0,0,.5)';
  const tint = (seed, n = 0) => COLORS[(Math.floor(seed / 101) + n) % COLORS.length];
  const rise = (e, rem) => {
    const i = Math.min(e / .3, 1);
    return {o: i * Math.min(rem / .25, 1), dy: 18 * (1 - VE.U.ease.outCubic(i))};
  };
  registerStyle({
    name: 'splash',
    holdFps: null,
    ink: '#ffc21f',
    accent: '#ff1f6b',
    highlight: '#ffc21f',
    stickerCss: 'filter:drop-shadow(0 6px 14px rgba(0,0,0,.45))',
    css: `
      .style-splash .pt{font-family:'Anuphan';font-weight:500;white-space:nowrap;line-height:1.6;color:#fff;${SHADOW}}
      .style-splash .pd{font-family:var(--display,'Anuphan');font-weight:200;white-space:nowrap;line-height:1.4;color:#fff;${SHADOW}}`,
    text(kind, text, seed, cue, a) {
      const U = a.U, c = cue.color;
      const css = {
        speech: `font-size:46px;${c ? 'color:' + c : ''}`,
        voice: `font-size:44px;color:${c || '#ffe9a8'}`,
        comment: `font-size:46px;font-weight:300;padding:0 6px;border-bottom:8px solid ${c || tint(seed)};border-radius:0 0 8px 8px`,
        label: `font-size:34px;font-weight:300;letter-spacing:.18em;padding-left:22px;border-left:10px solid ${c || tint(seed)}`,
        score: `font-size:72px;${c ? 'color:' + c : ''}`,
        tag: `font-size:28px;font-weight:600;padding:0 22px;border-radius:999px;background:${c || tint(seed, 2)};text-shadow:none`,
      }[kind];
      return U.node('div', `ob ${kind === 'score' ? 'pd' : 'pt'}`, css, text);
    },
    word(w, k, seed, cue, a) {
      return a.U.node('div', 'ob pd', `font-size:${cue.size || 150}px;${cue.color ? 'color:' + cue.color : ''}`, w);
    },
    wordGap: 34,
    tilt: {stamp: -4},
    stamp(text, cue, a) {
      return a.U.node('div', 'ob pd', `font-size:76px;padding:14px 60px;border:9px solid ${COLORS[1]};border-radius:48% 52% 55% 45% / 56% 44% 58% 42%`, text);
    },
    anim: {
      default: rise,
      impact: (e, rem) => ({clip: 100 * (1 - Math.min(e / .35, 1)), o: Math.min(rem / .25, 1)}),
      stamp: (e, rem) => ({o: Math.min(e / .15, 1) * Math.min(rem / .2, 1), s: .85 + .15 * VE.U.ease.outBack(Math.min(e / .3, 1), 2)}),
    },
    decorate: {
      /* A swoosh crosses the words and runs off, an underline stays, a few drops fly. */
      impact(a, cue, pos, seed, els) {
        const {U, root} = a, {W, H} = a.geo;
        const words = a.items.slice(-els.length), first = words[0], last = words[words.length - 1];
        const L = first.x - first.w * first.fit / 2, R = last.x + last.w * last.fit / 2, w = R - L, h = first.h * first.fit, y = pos.y;
        const paths = [
          {d: `M${L - 70},${y + h * .25} Q${L + w * .45},${y - h * 1.05} ${R + 90},${y + h * .5}`, sw: 16, c: tint(seed), from: .05, pass: true},
          {d: `M${L + w * .08},${y + h * .56} Q${L + w * .45},${y + h * .68} ${L + w * .8},${y + h * .54}`, sw: 11, c: tint(seed, 1), from: .3},
          {d: `M${R + 30},${y - h * .5} l34,-30 M${R + 70},${y - h * .2} l44,-12 M${R + 50},${y - h * .82} l14,-36`, sw: 12, c: tint(seed, 3), from: .25, pass: true},
        ];
        const el = U.node('div', 'ob', `width:${W}px;height:${H}px`,
          `<svg width="${W}" height="${H}" fill="none" stroke-linecap="round">${paths.map(p => `<path d="${p.d}" stroke="${p.c}" stroke-width="${p.sw}"/>`).join('')}</svg>`);
        root.appendChild(el);
        const nodes = [...el.querySelectorAll('path')].map((n, i) => {
          const len = n.getTotalLength();
          n.style.strokeDasharray = `${len} ${len}`;
          return {n, len, ...paths[i]};
        });
        a.items.push({el, cue, update(it, t) {
          const e = t - cue.t, rem = cue.end - t, on = e >= 0 && rem > 0;
          el.style.display = on ? '' : 'none';
          if (!on) return;
          for (const p of nodes) {
            const draw = U.ease.outCubic(U.clamp((e - p.from) / .4, 0, 1));
            const wipe = p.pass ? U.ease.inCubic(U.clamp((e - p.from - .55) / .4, 0, 1)) : U.ease.inCubic(U.clamp(1 - rem / .25, 0, 1));
            p.n.style.strokeDashoffset = p.len * (1 - draw) - p.len * wipe;
          }
        }});
      },
    },
    frame(a) {
      const {U, root} = a, {W, H, win, framed} = a.geo;
      if (!framed) return;
      const bar = (top, h, d, c) => root.appendChild(U.node('div', '', `position:absolute;left:0;top:${top}px;width:${W}px;height:${h}px;background:${DARK};overflow:hidden`,
        `<svg width="${W}" height="${h}" fill="none" stroke-linecap="round"><path d="${d}" stroke="${c}" stroke-width="14"/></svg>`));
      bar(0, win.y, `M${W * .5},70 Q${W * .78},20 ${W + 40},110`, COLORS[0]);
      const bh = H - win.y - win.h;
      bar(win.y + win.h, bh, `M-40,${bh - 150} Q${W * .25},${bh - 60} ${W * .55},${bh - 120}`, COLORS[1]);
    },
    transitions: {
      default: swipe,
      swipe,
    },
  });

  function swipe(a, cue, seed) {
    const {U, root} = a, {W, H} = a.geo, D = Math.hypot(W, H);
    const bands = [0, 1, 2].map(i => {
      const el = U.node('div', 'ob', `width:${D * 1.5}px;height:${D * 1.3}px;border-radius:${D * .2}px;background:${cue.color && i === 1 ? cue.color : tint(seed, i)}`);
      root.appendChild(el);
      return el;
    });
    a.items.push({el: bands[0], cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      bands.forEach(b => { b.style.display = on ? '' : 'none'; });
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t);
      bands.forEach((b, i) => {
        /* Each band follows the one before; the middle one covers the frame at the midpoint. */
        const q = U.clamp((p - i * .12) / .76, 0, 1);
        const x = q < .5 ? -D * 1.6 * (1 - U.ease.outCubic(q * 2)) : D * 1.6 * U.ease.inCubic((q - .5) * 2);
        b.style.transform = `translate(${(W - D * 1.5) / 2 + x}px,${(H - D * 1.3) / 2}px) rotate(-18deg)`;
      });
    }});
  }
})();
