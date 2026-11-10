/* Style: filmroll (compact film camera: rounded black frame, amber date stamp, sparse serif type). */
(function () {
  const CREAM = '#fff3da', AMBER = '#ff9a3d', BLACK = '#0b0907';
  const SHADOW = 'text-shadow:0 2px 10px rgba(0,0,0,.75),0 0 2px rgba(0,0,0,.6)';
  const fade = (e, rem) => {
    const i = Math.min(e / .6, 1);
    return {o: i * Math.min(rem / .4, 1), dy: 12 * (1 - VE.U.ease.outCubic(i))};
  };
  registerStyle({
    name: 'filmroll',
    holdFps: null,
    ink: CREAM,
    accent: AMBER,
    highlight: '#ffc27a',
    stickerCss: 'filter:drop-shadow(0 4px 10px rgba(0,0,0,.55))',
    css: `
      .style-filmroll .ft{font-family:'Anuphan';font-weight:500;white-space:nowrap;line-height:1.6;color:${CREAM};${SHADOW}}
      .style-filmroll .fd{font-family:var(--display,'Trirong');font-weight:400;white-space:nowrap;line-height:1.5;color:${CREAM};${SHADOW}}
      .style-filmroll .fstamp{font-family:var(--display,'Trirong');font-weight:400;font-size:62px;color:${AMBER};border:4px solid ${AMBER};padding:0 30px;white-space:nowrap;line-height:1.5;${SHADOW}}
      .style-filmroll .fdate{position:absolute;font-family:'VT323';font-size:56px;letter-spacing:.12em;color:${AMBER};text-shadow:0 0 12px #ff6a00;white-space:nowrap;line-height:1}`,
    text(kind, text, seed, cue, a) {
      const c = cue.color ? 'color:' + cue.color : '';
      const map = {
        speech: ['ft', 'font-size:46px'],
        voice: ['ft', 'font-size:44px;color:#ffe3b8'],
        comment: ['fd', 'font-size:48px'],
        label: ['ft', 'font-size:30px;letter-spacing:.24em'],
        score: ['fd', 'font-size:64px'],
        tag: ['ft', 'font-size:30px;letter-spacing:.1em'],
      }[kind];
      return a.U.node('div', `ob ${map[0]}`, `${map[1]};${c}`, text);
    },
    word(w, k, seed, cue, a) {
      return a.U.node('div', 'ob fd', `font-size:${cue.size || 110}px;${cue.color ? 'color:' + cue.color : ''}`, w);
    },
    wordGap: 28,
    tilt: {stamp: 0},
    stamp(text, cue, a) { return a.U.node('div', 'ob fstamp', '', text); },
    anim: {default: fade, impact: fade, stamp: fade},
    frame(a) {
      const {U, C, root} = a, {W, H, win, framed} = a.geo;
      const top = framed ? win.y : 0, h = framed ? win.h : H;
      if (framed) {
        const holes = (y) => `linear-gradient(90deg,rgba(255,243,218,.16) 0 46px,transparent 46px) 22px ${y}/92px 58px repeat-x,${BLACK}`;
        root.appendChild(U.node('div', '', `position:absolute;left:0;top:0;width:${W}px;height:${top}px;background:${holes('34px')}`));
        root.appendChild(U.node('div', '', `position:absolute;left:0;top:${top + h}px;width:${W}px;height:${H - top - h}px;background:${holes('calc(100% - 34px)')}`));
      }
      /* Solid shapes only: a full-frame gradient such as a vignette adds several hundred MB of overlay per minute. */
      const view = U.node('div', '', `position:absolute;left:0;top:${top}px;width:${W}px;height:${h}px;overflow:hidden`);
      view.appendChild(U.node('div', '', `position:absolute;inset:14px;border-radius:34px;box-shadow:0 0 0 80px ${BLACK}`));
      root.appendChild(view);
      if (!C.postmarks) return;
      const date = U.node('div', 'fdate', `right:74px;top:${top + h - 112}px`);
      root.appendChild(date);
      a.decor.push((t) => {
        const text = U.latest(C.postmarks, t).lines.join('  ');
        if (date.textContent !== text) date.textContent = text;
      });
    },
    transitions: {
      default: leak,
      leak,
    },
  });

  function leak(a, cue) {
    const {U, root} = a, {W, H} = a.geo;
    /* One flat colour: a gradient here costs about 4 MB of overlay per frame. */
    const el = U.node('div', 'ob', `width:${W}px;height:${H}px;background:${cue.color || '#ffc98a'}`);
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
