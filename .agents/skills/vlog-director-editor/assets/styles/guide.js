/* Style: guide (travel guide cards: white callout cards with a pin, yellow rounded titles, a corner info widget). */
(function () {
  const YELLOW = '#ffd21f', INK = '#1d1d1f', DARK = '#17181c';
  const SHADOW = 'text-shadow:0 2px 10px rgba(0,0,0,.7),0 0 2px rgba(0,0,0,.6)';
  const pin = (size, fill) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" style="flex:none"><path fill="${fill}" fill-rule="evenodd" d="M12 1.5a7.5 7.5 0 0 0-7.5 7.5c0 5.4 7.5 13.5 7.5 13.5s7.5-8.1 7.5-13.5A7.5 7.5 0 0 0 12 1.5zm0 10.3a2.8 2.8 0 1 1 0-5.6 2.8 2.8 0 0 1 0 5.6z"/></svg>`;
  const card = (e, rem) => {
    const i = Math.min(e / .22, 1);
    return {o: i * Math.min(rem / .15, 1), s: .9 + .1 * VE.U.ease.outBack(i, 1.6), dy: 16 * (1 - i)};
  };
  const wipe = (e, rem) => ({clip: 100 * (1 - VE.U.ease.outCubic(Math.min(e / .45, 1))), o: Math.min(rem / .2, 1)});
  registerStyle({
    name: 'guide',
    holdFps: null,
    ink: YELLOW,
    accent: YELLOW,
    highlight: YELLOW,
    stickerCss: 'filter:drop-shadow(0 6px 14px rgba(0,0,0,.45))',
    css: `
      .style-guide .gt{font-family:'Anuphan';font-weight:600;white-space:nowrap;line-height:1.6;color:#fff;${SHADOW}}
      .style-guide .gd{font-family:var(--display,'Kodchasan');font-weight:700;white-space:nowrap;line-height:1.5}
      .style-guide .grow{display:flex;align-items:center;gap:12px}
      .style-guide .gcol{display:flex;flex-direction:column;align-items:center}
      .style-guide .gcard{background:#fff;color:${INK};border-radius:18px;box-shadow:0 8px 22px rgba(0,0,0,.35);text-shadow:none}
      .style-guide .gstem{width:3px;height:34px;background:#fff}
      .style-guide .gdot{width:13px;height:13px;border-radius:50%;background:#fff}
      .style-guide .gstamp{font-family:var(--display,'Kodchasan');font-weight:700;font-size:54px;color:#fff;border:4px solid ${YELLOW};border-radius:50%;padding:10px 52px;white-space:nowrap;line-height:1.5;${SHADOW}}
      .style-guide .gwidget{position:absolute;display:flex;align-items:center;gap:14px;color:#fff;font-family:'Anuphan';line-height:1.25;${SHADOW}}
      .style-guide .gwidget b{display:flex;align-items:center;justify-content:center;width:84px;height:84px;border-radius:50%;background:${YELLOW}}`,
    text(kind, text, seed, cue, a) {
      const U = a.U, c = cue.color;
      if (kind === 'comment') {
        return U.node('div', 'ob', '',
          `<div class="gcol"><div class="gt gcard grow" style="font-size:40px;padding:8px 28px 8px 20px;${c ? 'background:' + c : ''}">${pin(40, YELLOW)}<span>${text}</span></div><div class="gstem"></div><div class="gdot"></div></div>`);
      }
      if (kind === 'label') return U.node('div', 'ob gd grow', `font-size:40px;color:${c || '#fff'};${SHADOW}`, `${pin(46, YELLOW)}<span>${text}</span>`);
      if (kind === 'score') return U.node('div', 'ob gd gcard', `font-size:56px;padding:4px 34px;border-left:14px solid ${YELLOW};${c ? 'background:' + c : ''}`, text);
      if (kind === 'tag') return U.node('div', 'ob gt gcard', `font-size:28px;padding:0 20px;border-radius:999px;${c ? 'background:' + c : ''}`, text);
      return U.node('div', 'ob gt', `font-size:${kind === 'speech' ? 46 : 44}px;color:${c || (kind === 'voice' ? '#ffe98a' : '#fff')}`, text);
    },
    word(w, k, seed, cue, a) {
      const c = cue.color || YELLOW;
      const css = k % 2 ? `color:transparent;-webkit-text-stroke:4px ${c}` : `color:${c}`;
      return a.U.node('div', 'ob', '', `<div class="gd" style="font-size:${cue.size || 150}px;${css};filter:drop-shadow(0 4px 10px rgba(0,0,0,.55))">${w}</div>`);
    },
    wordGap: 30,
    tilt: {stamp: -5},
    stamp(text, cue, a) { return a.U.node('div', 'ob gstamp', '', text); },
    anim: {
      default: card,
      label: wipe, speech: (e, rem) => ({o: Math.min(e / .15, 1) * Math.min(rem / .1, 1)}), voice: (e, rem) => ({o: Math.min(e / .15, 1) * Math.min(rem / .1, 1)}),
      impact: (e, rem) => {
        const i = Math.min(e / .3, 1);
        return {o: i * Math.min(rem / .2, 1), dy: 40 * (1 - VE.U.ease.outBack(i, 1.4))};
      },
    },
    frame(a) {
      const {U, C, root} = a, {W, H, win, framed} = a.geo;
      if (framed) {
        const css = `position:absolute;left:0;width:${W}px;box-sizing:border-box;background:${DARK}`;
        root.appendChild(U.node('div', '', `${css};top:0;height:${win.y}px;border-bottom:4px dashed ${YELLOW}`));
        root.appendChild(U.node('div', '', `${css};top:${win.y + win.h}px;height:${H - win.y - win.h}px;border-top:4px dashed ${YELLOW}`));
      }
      if (!C.postmarks) return;
      const widget = U.node('div', 'gwidget', `right:66px;top:${a.geo.vertical ? 124 : 56}px`);
      root.appendChild(widget);
      a.decor.push((t) => {
        const [one, two] = U.latest(C.postmarks, t).lines;
        const html = `<b>${pin(48, INK)}</b><div>${two ? `<div style="font-size:26px">${one}</div><div style="font-size:42px;font-weight:600">${two}</div>` : `<div style="font-size:40px;font-weight:600">${one}</div>`}</div>`;
        if (widget.innerHTML !== html) widget.innerHTML = html;
      });
    },
    transitions: {
      default: cardSlide,
      card: cardSlide,
    },
  });

  function cardSlide(a, cue) {
    const {U, root} = a, {W, H} = a.geo;
    const el = U.node('div', 'ob', `width:${W}px;height:${H * 1.2}px;border-radius:70px;background:${cue.color || '#fff'}`);
    root.appendChild(el);
    a.items.push({el, cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      el.style.display = on ? '' : 'none';
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t);
      const y = p < .5 ? H * (1 - U.ease.outCubic(p * 2)) - H * .1 * U.ease.outCubic(p * 2) : -H * .1 - H * 1.2 * U.ease.inCubic((p - .5) * 2);
      el.style.transform = `translate(0,${y}px)`;
    }});
  }
})();
