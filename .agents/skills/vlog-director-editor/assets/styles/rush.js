/* Style: rush (action promo: heavy italic words in white, magenta and cyan over a giant ghost word, slanted bars). */
(function () {
  const CYAN = '#19f0e6', MAGENTA = '#ff1fb4', YELLOW = '#fff01f', BLACK = '#0b0b10';
  const WORDS = ['#ffffff', MAGENTA, CYAN, YELLOW];
  const SLANT = 'clip-path:polygon(20px 0,100% 0,calc(100% - 20px) 100%,0 100%)';
  const slide = (e, rem) => {
    const i = VE.U.ease.outExpo(Math.min(e / .3, 1));
    return {o: Math.min(e / .08, 1) * Math.min(rem / .1, 1), dx: -70 * (1 - i)};
  };
  registerStyle({
    name: 'rush',
    holdFps: null,
    ink: CYAN,
    accent: MAGENTA,
    highlight: YELLOW,
    stickerCss: `filter:drop-shadow(8px 8px 0 ${MAGENTA})`,
    css: `
      .style-rush .rt{font-family:'Kanit';font-weight:700;white-space:nowrap;line-height:1.45}
      .style-rush .rd{font-family:var(--display,'Kanit');font-weight:900;font-style:italic;white-space:nowrap;line-height:1.3}
      .style-rush .rghost{position:absolute;font-family:var(--display,'Kanit');font-weight:900;font-style:italic;white-space:nowrap;line-height:1.3;color:rgba(255,255,255,.17)}`,
    text(kind, text, seed, cue, a) {
      const U = a.U, c = cue.color;
      if (kind === 'speech' || kind === 'voice') {
        return U.node('div', 'ob rt', `font-size:${kind === 'speech' ? 50 : 48}px;color:${c || (kind === 'voice' ? CYAN : '#fff')};-webkit-text-stroke:8px ${BLACK};paint-order:stroke fill`, text);
      }
      const box = {
        comment: `font-size:44px;color:#fff;background:${c || MAGENTA};padding:2px 44px`,
        label: `font-size:36px;color:${CYAN};background:${c || BLACK};padding:2px 40px`,
        score: `font-size:60px;color:${BLACK};background:${c || CYAN};padding:0 48px`,
        tag: `font-size:28px;color:${BLACK};background:${c || YELLOW};padding:0 34px`,
      }[kind];
      return U.node('div', 'ob', '', `<div class="${kind === 'score' ? 'rd' : 'rt'}" style="${box};${SLANT}">${text}</div>`);
    },
    word(w, k, seed, cue, a) {
      const c = cue.color || WORDS[k % WORDS.length];
      return a.U.node('div', 'ob', '', `<div class="rd" style="font-size:${cue.size || 170}px;padding:0 .12em;color:${c};filter:drop-shadow(0 6px 0 ${BLACK}) drop-shadow(0 0 14px ${c === '#ffffff' ? CYAN : c})">${w}</div>`);
    },
    wordGap: 0,
    tilt: {stamp: -6},
    stamp(text, cue, a) {
      return a.U.node('div', 'ob', '', `<div class="rd" style="font-size:70px;color:${BLACK};background:${YELLOW};padding:0 56px;${SLANT}">${text}</div>`);
    },
    anim: {
      default: slide,
      speech: (e, rem) => ({o: Math.min(e / .1, 1) * Math.min(rem / .08, 1)}),
      voice: (e, rem) => ({o: Math.min(e / .1, 1) * Math.min(rem / .08, 1)}),
      impact: (e, rem) => {
        const i = VE.U.ease.outExpo(Math.min(e / .35, 1));
        return {o: Math.min(e / .06, 1) * Math.min(rem / .1, 1), dx: -260 * (1 - i), sx: 1 + .25 * (1 - i)};
      },
      stamp: (e) => {
        const p = Math.min(e / .14, 1);
        return {s: 1.8 - .8 * p * p, o: p};
      },
    },
    decorate: {
      /* The same words, huge and faint, drift behind the real ones. */
      impact(a, cue, pos, seed, els) {
        const {U, root} = a, {W, H, win, framed} = a.geo;
        const boxH = framed ? win.y : H, size = framed ? 300 : 440;
        const el = U.node('div', 'ob', `width:${W}px;height:${boxH}px;overflow:hidden`,
          `<div class="rghost" style="font-size:${size}px">${cue.words.join(' ')}</div>`);
        root.insertBefore(el, root.children[1] || null);
        const ghost = el.firstChild, gw = ghost.offsetWidth, gh = ghost.offsetHeight;
        a.items.push({el, cue, update(it, t) {
          const e = t - cue.t, rem = cue.end - t, on = e >= 0 && rem > 0;
          el.style.display = on ? '' : 'none';
          if (!on) return;
          ghost.style.transform = `translate(${pos.x - gw / 2 + 90 - e * 50}px,${pos.y - gh / 2}px)`;
          el.style.opacity = Math.min(e / .2, 1) * Math.min(rem / .15, 1);
        }});
      },
    },
    frame(a) {
      const {U, root} = a, {W, H, win, framed} = a.geo;
      if (!framed) return;
      const css = `position:absolute;left:0;width:${W}px;box-sizing:border-box;background:${BLACK} radial-gradient(rgba(255,255,255,.2) 20%,transparent 22%) 0 0/26px 26px`;
      root.appendChild(U.node('div', '', `${css};top:0;height:${win.y}px;border-bottom:8px solid ${MAGENTA}`));
      root.appendChild(U.node('div', '', `${css};top:${win.y + win.h}px;height:${H - win.y - win.h}px;border-top:8px solid ${CYAN}`));
    },
    transitions: {
      default: bars,
      bars,
    },
  });

  function bars(a, cue) {
    const {U, root} = a, {W, H} = a.geo, colors = [MAGENTA, cue.color || CYAN, YELLOW], h = Math.ceil(H / 3);
    const els = colors.map((c, i) => {
      const el = U.node('div', 'ob', `width:${W * 1.3}px;height:${h + 1}px;background:${c}`);
      root.appendChild(el);
      return el;
    });
    a.items.push({el: els[0], cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      els.forEach(e => { e.style.display = on ? '' : 'none'; });
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t);
      els.forEach((e, i) => {
        /* All three cover the frame at the midpoint; they arrive and leave one after another. */
        const x = p < .5 ? -W * 1.4 * (1 - U.ease.outExpo(U.clamp(p * 2 * (1 + i * .25), 0, 1)))
                         : W * 1.4 * U.ease.inCubic(U.clamp(((p - .5) * 2 - (2 - i) * .12) / .76, 0, 1));
        e.style.transform = `translate(${-W * .15 + x}px,${i * h}px) skewX(-14deg)`;
      });
    }});
  }
})();
