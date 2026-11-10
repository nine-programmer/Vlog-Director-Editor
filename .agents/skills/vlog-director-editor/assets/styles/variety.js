/* Style: variety (Korean variety-show captions: bold, outlined, bouncy). */
(function () {
  const NAVY = '#16223f';
  registerStyle({
    name: 'variety',
    holdFps: null,
    ink: NAVY,
    accent: '#ff3d7f',
    highlight: '#ffe14d',
    stickerCss: 'filter:drop-shadow(0 8px 0 rgba(22,34,63,.9))',
    css: `
      .style-variety .vt{font-family:var(--display,'Kanit');font-weight:900;white-space:nowrap;line-height:1.3;paint-order:stroke fill}
      .style-variety .vb{font-family:'Kanit';font-weight:700;white-space:nowrap;line-height:1.45}
      .style-variety .vstamp{font-family:var(--display,'Kanit');font-weight:900;font-size:64px;color:#fff;background:#d21f3c;border:7px solid #fff;border-radius:20px;padding:4px 30px;box-shadow:0 9px 0 ${NAVY};white-space:nowrap;line-height:1.35}`,
    tilt: {comment: -3, score: -2, tag: 2},
    text(kind, text, seed, cue, a) {
      const U = a.U, c = cue.color;
      const css = {
        speech: `font-size:58px;color:${c || '#fff'};-webkit-text-stroke:10px ${NAVY}`,
        voice: `font-size:54px;color:${c || '#ffe14d'};-webkit-text-stroke:9px ${NAVY}`,
        comment: `font-size:50px;color:#fff;background:${c || '#ff3d7f'};padding:6px 32px;border-radius:48px;box-shadow:0 7px 0 ${NAVY}`,
        label: `font-size:40px;color:#ffe14d;background:${c || NAVY};padding:6px 24px`,
        score: `font-size:58px;color:${NAVY};background:${c || '#ffe14d'};border:6px solid ${NAVY};border-radius:14px;padding:4px 28px`,
        tag: `font-size:32px;color:${NAVY};background:${c || '#fff'};border:5px solid ${NAVY};border-radius:40px;padding:2px 22px`,
      }[kind];
      const cls = kind === 'speech' || kind === 'voice' ? 'vt' : 'vb';
      return U.node('div', `ob ${cls}`, css, text);
    },
    word(w, k, seed, cue, a) {
      return a.U.node('div', 'ob', '', `<div class="vt" style="font-size:${cue.size || 170}px;color:${cue.color || '#ffe14d'};-webkit-text-stroke:16px #d21f3c;filter:drop-shadow(0 10px 0 ${NAVY})">${w}</div>`);
    },
    wordGap: 10,
    wordTilt: (k) => (k % 2 ? 4 : -4),
    stamp(text, cue, a) { return a.U.node('div', 'ob vstamp', '', text); },
    anim: {
      default: (e, rem) => {
        const s = e < .28 ? Math.max(VE.U.ease.outBack(e / .28, 2.6), 0) : 1;
        return {s: rem < .12 ? s * rem / .12 : s};
      },
      speech: (e, rem) => ({o: Math.min(e / .12, 1) * Math.min(rem / .08, 1), dy: 14 * (1 - Math.min(e / .12, 1))}),
      voice: (e, rem) => ({o: Math.min(e / .12, 1) * Math.min(rem / .08, 1), dy: 14 * (1 - Math.min(e / .12, 1))}),
      impact: (e, rem, it) => ({
        s: Math.max(VE.U.spring(e, 2.4, 7), 0) * (rem < .1 ? rem / .1 : 1),
        r: (it.seed % 2 ? 9 : -9) * Math.exp(-e * 7),
      }),
      stamp: (e) => ({s: e < .25 ? Math.max(VE.U.ease.outBack(e / .25, 3), 0) : 1, r: -12 * Math.exp(-e * 9)}),
    },
    decorate: {
      impact(a, cue, pos) {
        const {U, root} = a;
        for (let i = 0; i < 8; i++) {
          const ang = i / 8 * Math.PI * 2, dist = 330 + (i % 2) * 70;
          const el = U.node('div', 'ob', 'width:58px;height:58px',
            `<svg viewBox="0 0 24 24" width="58" height="58"><path fill="#ffe14d" stroke="${NAVY}" stroke-width="1.6" d="M12 1l2.6 8.4L23 12l-8.4 2.6L12 23l-2.6-8.4L1 12l8.4-2.6z"/></svg>`);
          root.appendChild(el);
          a.items.push({el, cue, update(it, t) {
            const e = t - cue.t - .05, on = e >= 0 && e < .6;
            el.style.display = on ? '' : 'none';
            if (!on) return;
            const p = U.ease.outCubic(Math.min(e / .55, 1));
            el.style.transform = `translate(${pos.x - 29 + Math.cos(ang) * dist * p}px,${pos.y - 29 + Math.sin(ang) * dist * .7 * p}px) rotate(${p * 180}deg) scale(${.4 + p})`;
            el.style.opacity = 1 - Math.max(0, (e - .4) / .2);
          }});
        }
      },
    },
    frame(a) {
      const {U, root} = a, {W, H, win, framed} = a.geo;
      if (!framed) return;
      const css = `position:absolute;left:0;width:${W}px;background:${NAVY} radial-gradient(rgba(255,225,77,.16) 22%,transparent 24%) 0 0/34px 34px`;
      root.appendChild(U.node('div', '', `${css};top:0;height:${win.y}px;border-bottom:8px solid #ffe14d`));
      root.appendChild(U.node('div', '', `${css};top:${win.y + win.h}px;height:${H - win.y - win.h}px;border-top:8px solid #ffe14d`));
    },
    transitions: {
      default: whip,
      whip,
    },
  });

  function whip(a, cue) {
    const {U, root} = a, {W, H} = a.geo;
    const el = U.node('div', 'ob', `width:${W * 1.4}px;height:${H}px;background:${cue.color || '#ffe14d'};filter:blur(6px)`);
    root.appendChild(el);
    a.items.push({el, cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      el.style.display = on ? '' : 'none';
      if (!on) return;
      const p = U.ease.inOutSine((t - cue.t) / (cue.end - cue.t));
      el.style.transform = `translate(${-W * 1.5 + p * W * 2.6}px,0) skewX(-18deg)`;
    }});
  }
})();
