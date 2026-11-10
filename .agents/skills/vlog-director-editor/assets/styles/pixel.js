/* Style: pixel (8-bit game interface: dialog boxes, quest labels, stepped motion at 12 fps). */
(function () {
  const NAVY = '#141834', YELLOW = '#ffe066', CYAN = '#7fe3ff', RED = '#ff5a6e';
  const EDGE = `box-shadow:0 0 0 5px #fff,0 0 0 10px ${NAVY}`;
  const STEPS = [.4, .8, 1.15, 1];
  const step = (e) => ({s: STEPS[Math.min(Math.floor(e * 12 + 1e-6), 3)]});
  registerStyle({
    name: 'pixel',
    holdFps: 12,
    ink: YELLOW,
    accent: YELLOW,
    highlight: YELLOW,
    stickerCss: `filter:drop-shadow(6px 6px 0 ${NAVY})`,
    css: `
      .style-pixel .pt{font-family:'Pixelify Sans',var(--display,'Chakra Petch');font-weight:700;white-space:nowrap;line-height:1.5}
      .style-pixel .pw{font-family:'Pixelify Sans',var(--display,'Chakra Petch');font-weight:700;white-space:nowrap;line-height:1.3;paint-order:stroke fill}
      .style-pixel .pstamp{font-family:'Pixelify Sans',var(--display,'Chakra Petch');font-weight:700;font-size:60px;color:#fff;background:${RED};padding:2px 30px;white-space:nowrap;line-height:1.4;${EDGE}}`,
    text(kind, text, seed, cue, a) {
      const c = cue.color;
      const css = {
        speech: `font-size:48px;color:${c || '#fff'};background:rgba(20,24,52,.92);padding:8px 34px;${EDGE}`,
        voice: `font-size:46px;color:${c || CYAN};background:rgba(20,24,52,.92);padding:8px 34px;${EDGE}`,
        comment: `font-size:44px;color:${NAVY};background:${c || YELLOW};padding:4px 26px;box-shadow:6px 6px 0 ${NAVY}`,
        label: `font-size:36px;color:${YELLOW};background:${c || NAVY};padding:4px 22px;${EDGE}`,
        score: `font-size:56px;color:${NAVY};background:${c || CYAN};padding:2px 28px;box-shadow:8px 8px 0 ${NAVY}`,
        tag: `font-size:30px;color:${NAVY};background:${c || '#fff'};padding:0 16px;box-shadow:5px 5px 0 ${NAVY}`,
      }[kind];
      return a.U.node('div', 'ob pt', css, text);
    },
    word(w, k, seed, cue, a) {
      return a.U.node('div', 'ob', '', `<div class="pw" style="font-size:${cue.size || 150}px;color:${cue.color || YELLOW};-webkit-text-stroke:12px ${NAVY};filter:drop-shadow(8px 8px 0 ${RED})">${w}</div>`);
    },
    wordGap: 14,
    stamp(text, cue, a) { return a.U.node('div', 'ob pstamp', '', text); },
    anim: {default: step},
    frame(a) {
      const {U, root} = a, {W, H, win, framed} = a.geo;
      if (!framed) return;
      const grid = 'linear-gradient(rgba(127,227,255,.08) 2px,transparent 2px) 0 0/40px 40px,linear-gradient(90deg,rgba(127,227,255,.08) 2px,transparent 2px) 0 0/40px 40px';
      const css = `position:absolute;left:0;width:${W}px;box-sizing:border-box;background:${grid},${NAVY}`;
      root.appendChild(U.node('div', '', `${css};top:0;height:${win.y}px;border-bottom:8px solid #fff`));
      root.appendChild(U.node('div', '', `${css};top:${win.y + win.h}px;height:${H - win.y - win.h}px;border-top:8px solid #fff`));
    },
    transitions: {
      default: blocks,
      blocks,
    },
  });

  function blocks(a, cue, seed) {
    const {U, root} = a, {W, H} = a.geo;
    const cols = W > H ? 16 : 9, size = Math.ceil(W / cols), rows = Math.ceil(H / size);
    const el = U.node('div', 'ob', `width:${W}px;height:${H}px;overflow:hidden`);
    const cells = [], rand = U.rng(seed);
    for (let i = 0; i < cols * rows; i++) {
      const cell = U.node('div', '', `position:absolute;left:${(i % cols) * size}px;top:${Math.floor(i / cols) * size}px;width:${size + 1}px;height:${size + 1}px;background:${cue.color || NAVY}`);
      el.appendChild(cell); cells.push([cell, rand()]);
    }
    root.appendChild(el);
    a.items.push({el, cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      el.style.display = on ? '' : 'none';
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t), level = (p < .5 ? p : 1 - p) * 2.4;
      for (const [cell, r] of cells) cell.style.visibility = r < level ? 'visible' : 'hidden';
    }});
  }
})();
