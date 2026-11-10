/* Style: journal (field-journal annotation: handwriting, pen arrows and circles, sparse). */
(function () {
  const CREAM = '#fff8e7', ORANGE = '#ff7a1a';
  const SHADOW = 'text-shadow:0 0 6px rgba(0,0,0,.9),0 3px 12px rgba(0,0,0,.7)';
  const write = (e, rem) => ({clip: 100 * (1 - Math.min(e / .45, 1)), o: Math.min(rem / .3, 1)});
  registerStyle({
    name: 'journal',
    holdFps: null,
    ink: CREAM,
    accent: ORANGE,
    stickerCss: 'filter:drop-shadow(0 4px 8px rgba(0,0,0,.6))',
    css: `
      .style-journal .jt{font-family:var(--display,'Sriracha');font-weight:400;white-space:nowrap;line-height:1.5;color:${CREAM};${SHADOW}}
      .style-journal .jstamp{font-family:var(--display,'Sriracha');font-size:64px;color:${CREAM};border:6px solid ${ORANGE};border-radius:50%;padding:18px 46px;white-space:nowrap;line-height:1.4;${SHADOW}}`,
    tilt: {comment: -2, label: -1, score: -3, tag: 2},
    text(kind, text, seed, cue, a) {
      const c = cue.color;
      const css = {
        speech: `font-size:56px;${c ? 'color:' + c : ''}`,
        voice: `font-size:54px;color:${c || '#ffe3b8'}`,
        comment: `font-size:52px;color:${c || '#ffb169'}`,
        label: `font-size:42px;border-bottom:5px solid ${ORANGE};padding:0 6px`,
        score: `font-size:62px;border-bottom:6px solid ${ORANGE};padding:0 10px`,
        tag: `font-size:36px;color:${c || '#ffe3b8'}`,
      }[kind];
      return a.U.node('div', 'ob jt', css, text);
    },
    word(w, k, seed, cue, a) {
      return a.U.node('div', 'ob jt', `font-size:${cue.size || 130}px;${cue.color ? 'color:' + cue.color : ''}`, w);
    },
    wordGap: 26,
    wordTilt: (k) => (k % 2 ? 2 : -3),
    stamp(text, cue, a) { return a.U.node('div', 'ob jstamp', '', text); },
    anim: {default: write, impact: write, stamp: write},
    frame(a) {
      const {U, root} = a, {W, H, win, framed} = a.geo;
      if (!framed) return;
      const css = `position:absolute;left:0;width:${W}px;background:repeating-linear-gradient(0deg,rgba(255,248,231,.07) 0 2px,transparent 2px 46px),repeating-linear-gradient(90deg,rgba(255,248,231,.07) 0 2px,transparent 2px 46px),#20302c`;
      root.appendChild(U.node('div', '', `${css};top:0;height:${win.y}px`));
      root.appendChild(U.node('div', '', `${css};top:${win.y + win.h}px;height:${H - win.y - win.h}px`));
    },
    transitions: {
      default: page,
      page,
    },
  });

  function page(a, cue) {
    const {U, root} = a, {W, H} = a.geo;
    const el = U.node('div', 'ob', `width:${W}px;height:${H}px;background:${cue.color || '#f4ead2'} repeating-linear-gradient(0deg,rgba(80,60,30,.12) 0 2px,transparent 2px 46px);box-shadow:-20px 0 40px rgba(0,0,0,.5)`);
    root.appendChild(el);
    a.items.push({el, cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      el.style.display = on ? '' : 'none';
      if (!on) return;
      const p = U.ease.inOutSine((t - cue.t) / (cue.end - cue.t));
      el.style.transform = `translate(${W - p * W * 2}px,0)`;
    }});
  }
})();
