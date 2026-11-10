/* Style: soft (soft cinematic: small type, wide tracking, slow blur-in, no hard hits). */
(function () {
  const WARM = '#fff6e4';
  const GLOW = 'text-shadow:0 0 22px rgba(0,0,0,.5),0 2px 8px rgba(0,0,0,.55),0 0 2px rgba(0,0,0,.6)';
  const bloom = (e, rem) => {
    const i = VE.U.ease.outCubic(Math.min(e / .9, 1));
    return {o: i * Math.min(rem / .6, 1), blur: 10 * (1 - i)};
  };
  /* Titles keep drifting forward very slowly after they appear, like a slow push-in. */
  const drift = (e, rem) => Object.assign(bloom(e, rem), {s: .96 + .04 * VE.U.ease.outCubic(Math.min(e / 1.4, 1)) + .006 * e});
  const rule = (side) => `<i style="display:block;width:70px;height:2px;background:${WARM};opacity:.85;margin-${side}:26px;box-shadow:0 0 8px rgba(0,0,0,.5)"></i>`;
  registerStyle({
    name: 'soft',
    holdFps: null,
    ink: WARM,
    accent: WARM,
    stickerCss: 'filter:drop-shadow(0 6px 14px rgba(0,0,0,.45))',
    css: `
      .style-soft .st{font-family:'Anuphan';font-weight:500;white-space:nowrap;line-height:1.6;color:#fff;${GLOW}}
      .style-soft .sd{font-family:var(--display,'Charm');font-weight:var(--display-weight,700);white-space:nowrap;line-height:1.5;color:${WARM};${GLOW}}`,
    text(kind, text, seed, cue, a) {
      const c = cue.color ? 'color:' + cue.color : '';
      const map = {
        speech: ['st', 'font-size:46px;letter-spacing:.03em'],
        voice: ['st', `font-size:44px;letter-spacing:.03em;color:${WARM}`],
        comment: ['st', 'font-size:42px;font-weight:400;letter-spacing:.04em'],
        label: ['st', `font-size:30px;font-weight:400;letter-spacing:.32em;padding-left:64px;background:linear-gradient(${WARM},${WARM}) left center/44px 2px no-repeat`],
        score: ['sd', 'font-size:66px'],
        tag: ['st', 'font-size:30px;font-weight:400;letter-spacing:.12em'],
      }[kind];
      return a.U.node('div', `ob ${map[0]}`, `${map[1]};${c}`, text);
    },
    word(w, k, seed, cue, a) {
      return a.U.node('div', 'ob sd', `font-size:${cue.size || 120}px;${cue.color ? 'color:' + cue.color : ''}`, w);
    },
    wordGap: 30,
    tilt: {stamp: 0},
    /* The verdict sits between two hairlines. */
    stamp(text, cue, a) { return a.U.node('div', 'ob sd', 'font-size:72px', `<div style="display:flex;align-items:center">${rule('right')}<span>${text}</span>${rule('left')}</div>`); },
    anim: {default: bloom, impact: drift, stamp: drift, score: drift},
    frame(a) {
      const {U, root} = a, {W, H, win, framed} = a.geo;
      if (!framed) return;
      root.appendChild(U.node('div', '', `position:absolute;left:0;top:0;width:${W}px;height:${win.y}px;background:linear-gradient(#0b121a,#16222e)`));
      root.appendChild(U.node('div', '', `position:absolute;left:0;top:${win.y + win.h}px;width:${W}px;height:${H - win.y - win.h}px;background:linear-gradient(#16222e,#0b121a)`));
    },
    transitions: {
      default: (a, cue) => fadeDip(a, cue),
      fade: (a, cue) => fadeDip(a, cue),
    },
  });

  function fadeDip(a, cue) {
    const {U, root} = a, {W, H} = a.geo;
    const el = U.node('div', 'ob', `width:${W}px;height:${H}px;background:${cue.color || '#fff8ee'}`);
    root.appendChild(el);
    a.items.push({el, cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      el.style.display = on ? '' : 'none';
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t);
      el.style.opacity = U.ease.inOutSine(p < .5 ? p * 2 : (1 - p) * 2);
    }});
  }
})();
