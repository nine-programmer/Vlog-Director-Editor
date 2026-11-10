/* Style: mono (black-and-white type: thin against heavy, hard cuts, a title card whose letters are windows onto the footage). */
(function () {
  const SHADOW = 'text-shadow:0 2px 12px rgba(0,0,0,.65),0 0 2px rgba(0,0,0,.6)';
  const cut = (e, rem) => ({clip: 100 * (1 - Math.min(e / .18, 1)), o: rem < .06 ? 0 : 1});
  registerStyle({
    name: 'mono',
    holdFps: null,
    ink: '#ffffff',
    accent: '#ffffff',
    highlight: '#ffffff',
    stickerCss: 'filter:grayscale(1) drop-shadow(0 6px 14px rgba(0,0,0,.5))',
    css: `
      .style-mono .hl{text-decoration:underline;text-decoration-thickness:.08em;text-underline-offset:.16em}
      .style-mono .mt{font-family:'Anuphan';font-weight:500;white-space:nowrap;line-height:1.6;color:#fff;${SHADOW}}
      .style-mono .mh{font-family:var(--display,'Prompt');font-weight:800;white-space:nowrap;line-height:1.3;color:#fff}
      .style-mono .ml{font-family:'Anuphan';font-weight:200;white-space:nowrap;line-height:1.3;color:#fff}
      .style-mono .mcut{font-family:var(--display,'Prompt');font-weight:800}`,
    text(kind, text, seed, cue, a) {
      const U = a.U, c = cue.color;
      const map = {
        speech: ['mt', `font-size:46px;${c ? 'color:' + c : ''}`],
        voice: ['mt', `font-size:44px;font-weight:300;${c ? 'color:' + c : ''}`],
        comment: ['mh', `font-size:38px;color:#000;background:${c || '#fff'};padding:2px 22px`],
        label: ['mt', 'font-size:26px;font-weight:600;letter-spacing:.3em;border-top:2px solid #fff;border-bottom:2px solid #fff;padding:4px 2px'],
        score: ['mh', `font-size:70px;${SHADOW}`],
        tag: ['mt', 'font-size:26px;font-weight:600;letter-spacing:.14em;border:2px solid #fff;padding:0 16px'],
      }[kind];
      return U.node('div', `ob ${map[0]}`, map[1], text);
    },
    /* Thin, heavy, thin: the pairing is the look. */
    word(w, k, seed, cue, a) {
      return a.U.node('div', `ob ${k % 2 ? 'mh' : 'ml'}`, `font-size:${cue.size || 150}px;${SHADOW};${cue.color ? 'color:' + cue.color : ''}`, w);
    },
    wordGap: 26,
    anim: {
      default: cut,
      impact: (e, rem) => ({o: rem < .06 ? 0 : Math.min(e / .04, 1), sx: 1 + .12 * (1 - VE.U.ease.outExpo(Math.min(e / .3, 1)))}),
    },
    build: {
      /* Black covers the picture and the footage shows through the letters. */
      stamp(a, cue, seed) {
        const {U, root} = a, {W, H, win, framed} = a.geo;
        const top = framed ? win.y : 0, h = framed ? win.h : H;
        const text = String(cue.text).replace(/<[^>]+>/g, '');
        const probe = U.node('div', 'ob mh', 'font-size:300px', text);
        root.appendChild(probe);
        const size = Math.min(300 * (framed ? 820 : W * .84) / Math.max(probe.offsetWidth, 1), h * .46);
        const tw = probe.offsetWidth * size / 300;
        root.removeChild(probe);
        const x = cue.x ?? W / 2, y = cue.y ?? top + h / 2, id = `mono-cut-${seed}`;
        const el = U.node('div', 'ob', `width:${W}px;height:${h}px`,
          `<svg width="${W}" height="${h}"><defs><mask id="${id}"><rect width="${W}" height="${h}" fill="#fff"/><text class="mcut" x="${x}" y="${y - top}" text-anchor="middle" dominant-baseline="central" font-size="${size}" fill="#000">${text}</text></mask></defs><rect width="${W}" height="${h}" fill="#000" mask="url(#${id})"/></svg>`);
        root.appendChild(el);
        const glyphs = el.querySelector('text');
        glyphs.style.transformOrigin = `${x}px ${y - top}px`;
        a.items.push({el, cue, kind: 'stamp', text, start: cue.t, end: cue.end, fit: 1, x, y, ax: .5, ay: .5, w: tw, h: size * 1.3,
          update(it, t) {
            const on = t >= cue.t && t < cue.end;
            el.style.display = on ? '' : 'none';
            if (!on) return;
            el.style.transform = `translate(0,${top}px)`;
            glyphs.style.transform = `scale(${1 + .07 * (t - cue.t) / (cue.end - cue.t)})`;
          }});
      },
    },
    frame(a) {
      const {U, root} = a, {W, H, win, framed} = a.geo;
      if (!framed) return;
      const css = `position:absolute;left:0;width:${W}px;box-sizing:border-box;background:#000`;
      root.appendChild(U.node('div', '', `${css};top:0;height:${win.y}px;border-bottom:2px solid #fff`));
      root.appendChild(U.node('div', '', `${css};top:${win.y + win.h}px;height:${H - win.y - win.h}px;border-top:2px solid #fff`));
    },
    transitions: {
      default: split,
      split,
    },
  });

  function split(a, cue) {
    const {U, root} = a, {W, H} = a.geo;
    const halves = [-1, 1].map(() => {
      const el = U.node('div', 'ob', `width:${W / 2 + 2}px;height:${H}px;background:${cue.color || '#000'}`);
      root.appendChild(el);
      return el;
    });
    a.items.push({el: halves[0], cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      halves.forEach(e => { e.style.display = on ? '' : 'none'; });
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t);
      const shut = p < .5 ? U.ease.outExpo(p * 2) : 1 - U.ease.inCubic((p - .5) * 2);
      halves[0].style.transform = `translate(${-W / 2 * (1 - shut)}px,0)`;
      halves[1].style.transform = `translate(${W / 2 - 2 + W / 2 * (1 - shut)}px,0)`;
    }});
  }
})();
