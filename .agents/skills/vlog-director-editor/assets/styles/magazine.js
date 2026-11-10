/* Style: magazine (travel editorial: one large serif headline, small tracked labels, thin rules). */
(function () {
  const PAPER = '#f1ede4';
  const SHADOW = 'text-shadow:0 2px 14px rgba(0,0,0,.6),0 0 2px rgba(0,0,0,.5)';
  const rise = (e, rem) => {
    const i = Math.min(e / .35, 1);
    return {o: i * Math.min(rem / .3, 1), dy: 24 * (1 - VE.U.ease.outCubic(i))};
  };
  const wipe = (e, rem) => ({clip: 100 * (1 - Math.min(e / .4, 1)), o: Math.min(rem / .3, 1)});
  registerStyle({
    name: 'magazine',
    holdFps: null,
    ink: '#ffffff',
    accent: '#ffffff',
    highlight: '#ffd9a0',
    stickerCss: 'filter:drop-shadow(0 6px 14px rgba(0,0,0,.45))',
    css: `
      .style-magazine .mt{font-family:'Anuphan';font-weight:500;white-space:nowrap;line-height:1.6;color:#fff;${SHADOW}}
      .style-magazine .md{font-family:var(--display,'Trirong');font-weight:700;white-space:nowrap;line-height:1.35;color:#fff;${SHADOW}}
      .style-magazine .mstamp{font-family:var(--display,'Trirong');font-weight:700;font-size:84px;color:#fff;border-top:3px solid #fff;border-bottom:3px solid #fff;padding:0 22px;white-space:nowrap;line-height:1.3;${SHADOW}}`,
    text(kind, text, seed, cue, a) {
      const c = cue.color ? 'color:' + cue.color : '';
      const map = {
        speech: ['mt', 'font-size:46px'],
        voice: ['mt', 'font-size:44px;color:#ffe9c9'],
        comment: ['md', 'font-size:46px;font-weight:400'],
        label: ['mt', 'font-size:28px;letter-spacing:.3em;border-top:3px solid #fff;padding-top:10px'],
        score: ['md', 'font-size:70px'],
        tag: ['mt', 'font-size:28px;letter-spacing:.14em;border-left:3px solid #fff;padding-left:14px'],
      }[kind];
      return a.U.node('div', `ob ${map[0]}`, `${map[1]};${c}`, text);
    },
    word(w, k, seed, cue, a) {
      return a.U.node('div', 'ob md', `font-size:${cue.size || 150}px;${cue.color ? 'color:' + cue.color : ''}`, w);
    },
    wordGap: 28,
    tilt: {stamp: 0},
    stamp(text, cue, a) { return a.U.node('div', 'ob mstamp', '', text); },
    anim: {default: rise, label: wipe, tag: wipe},
    frame(a) {
      const {U, root} = a, {W, H, win, framed} = a.geo;
      if (!framed) return;
      const css = `position:absolute;left:0;width:${W}px;background:#121212;box-sizing:border-box`;
      root.appendChild(U.node('div', '', `${css};top:0;height:${win.y}px;border-bottom:2px solid ${PAPER}`));
      root.appendChild(U.node('div', '', `${css};top:${win.y + win.h}px;height:${H - win.y - win.h}px;border-top:2px solid ${PAPER}`));
    },
    transitions: {
      default: block,
      block,
    },
  });

  function block(a, cue) {
    const {U, root} = a, {W, H} = a.geo;
    const el = U.node('div', 'ob', `width:${W}px;height:${H}px;background:${cue.color || PAPER}`);
    root.appendChild(el);
    a.items.push({el, cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      el.style.display = on ? '' : 'none';
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t);
      const x = p < .5 ? -W * (1 - U.ease.outCubic(p * 2)) : W * U.ease.inCubic((p - .5) * 2);
      el.style.transform = `translate(${x}px,0)`;
    }});
  }
})();
