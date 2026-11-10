/* Style: sage (soft editorial: cream sans beside lime serif italic, outlined pills, sage and charcoal panels). */
(function () {
  const SAGE = '#94a37e', CHAR = '#232422', CREAM = '#ece7dc', LIME = '#e3ff7a';
  const SHADOW = 'text-shadow:0 2px 14px rgba(0,0,0,.55),0 0 2px rgba(0,0,0,.45)';
  const rise = (e, rem) => {
    const i = Math.min(e / .45, 1);
    return {o: i * Math.min(rem / .35, 1), dy: 30 * (1 - VE.U.ease.outCubic(i))};
  };
  const wipe = (e, rem) => ({clip: 100 * (1 - Math.min(e / .45, 1)), o: Math.min(rem / .3, 1)});
  const star = (size) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="${LIME}" stroke-width="2.2" stroke-linecap="round"><path d="M12 2v20M3.3 7l17.4 10M20.7 7L3.3 17"/></svg>`;
  registerStyle({
    name: 'sage',
    holdFps: null,
    ink: CREAM,
    accent: LIME,
    highlight: LIME,
    stickerCss: 'filter:drop-shadow(0 6px 14px rgba(0,0,0,.4))',
    css: `
      .style-sage .et{font-family:'Anuphan';font-weight:500;white-space:nowrap;line-height:1.6;color:${CREAM};${SHADOW}}
      .style-sage .ed{font-family:var(--display,'Trirong');font-weight:400;white-space:nowrap;line-height:1.4;color:${LIME};${SHADOW}}
      .style-sage .estamp{position:relative;display:inline-block;font-family:var(--display,'Trirong');font-weight:400;font-size:66px;color:${CREAM};border:3px solid ${CREAM};border-radius:50%;padding:4px 64px;white-space:nowrap;line-height:1.5;${SHADOW}}
      .style-sage .estamp svg{position:absolute;right:-22px;top:-20px}`,
    text(kind, text, seed, cue, a) {
      const c = cue.color ? 'color:' + cue.color : '';
      const map = {
        speech: ['et', 'font-size:46px'],
        voice: ['ed', `font-size:48px;color:${CREAM}`],
        comment: ['ed', 'font-size:50px'],
        label: ['et', `font-size:26px;font-weight:600;letter-spacing:.12em;border:2px solid ${CREAM};border-radius:999px;padding:0 22px`],
        score: ['ed', `font-size:72px;color:${CREAM}`],
        tag: ['et', `font-size:24px;font-weight:600;letter-spacing:.06em;color:${CHAR};background:${cue.color || LIME};border-radius:999px;padding:0 18px;text-shadow:none`],
      }[kind];
      return a.U.node('div', `ob ${map[0]}`, `${map[1]};${kind === 'tag' ? '' : c}`, text);
    },
    /* Sans in cream, then serif italic in lime, alternating. */
    word(w, k, seed, cue, a) {
      const css = k % 2 ? `font-size:${(cue.size || 140) * 1.08}px` : `font-size:${cue.size || 140}px;line-height:1.4`;
      return a.U.node('div', `ob ${k % 2 ? 'ed' : 'et'}`, `${css};${cue.color ? 'color:' + cue.color : ''}`, w);
    },
    wordGap: 30,
    tilt: {stamp: 0},
    stamp(text, cue, a) { return a.U.node('div', 'ob', '', `<div class="estamp">${text}${star(52)}</div>`); },
    anim: {default: rise, label: wipe, tag: wipe},
    frame(a) {
      const {U, root} = a, {W, H, win, framed} = a.geo;
      if (!framed) return;
      const css = `position:absolute;left:0;width:${W}px;box-sizing:border-box;background:${CHAR}`;
      root.appendChild(U.node('div', '', `${css};top:0;height:${win.y}px;border-bottom:14px solid ${SAGE}`));
      root.appendChild(U.node('div', '', `${css};top:${win.y + win.h}px;height:${H - win.y - win.h}px;border-top:14px solid ${SAGE}`));
    },
    transitions: {
      default: arch,
      arch,
    },
  });

  function arch(a, cue) {
    const {U, root} = a, {W, H} = a.geo, D = Math.hypot(W, H) * 1.25;
    const el = U.node('div', 'ob', `width:${D}px;height:${D}px;border-radius:50%;background:${cue.color || SAGE}`);
    root.appendChild(el);
    a.items.push({el, cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      el.style.display = on ? '' : 'none';
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t);
      const y = p < .5 ? H + (-(D + H) / 2) * U.ease.outCubic(p * 2) : (H - D) / 2 - (D + H) / 2 * U.ease.inCubic((p - .5) * 2);
      el.style.transform = `translate(${(W - D) / 2}px,${y}px)`;
    }});
  }
})();
