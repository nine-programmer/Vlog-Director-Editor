/* Style: pop (flat colour pop: blue, lime and pink discs and rings, heavy white type with a hard shadow). */
(function () {
  const BLUE = '#3a22e8', LIME = '#c6e600', PINK = '#ff6fb5';
  const pop = (e, rem) => {
    const s = e < .26 ? Math.max(VE.U.ease.outBack(e / .26, 2.4), 0) : 1;
    return {s: rem < .1 ? s * rem / .1 : s};
  };
  registerStyle({
    name: 'pop',
    holdFps: null,
    ink: '#ffffff',
    accent: LIME,
    highlight: LIME,
    stickerCss: `filter:drop-shadow(8px 8px 0 ${BLUE})`,
    css: `
      .style-pop .ot{font-family:'Kanit';font-weight:700;white-space:nowrap;line-height:1.45}
      .style-pop .od{font-family:var(--display,'Kanit');font-weight:900;white-space:nowrap;line-height:1.25}
      .style-pop .ostamp{font-family:var(--display,'Kanit');font-weight:900;font-size:60px;color:#fff;background:${BLUE};border:5px dashed #fff;outline:12px solid ${BLUE};border-radius:999px;padding:14px 50px;white-space:nowrap;line-height:1.35}`,
    tilt: {comment: -2, score: 2, tag: -2},
    text(kind, text, seed, cue, a) {
      const c = cue.color;
      const css = {
        speech: `font-size:52px;color:${c || '#fff'};-webkit-text-stroke:9px ${BLUE};paint-order:stroke fill`,
        voice: `font-size:50px;color:${c || LIME};-webkit-text-stroke:9px ${BLUE};paint-order:stroke fill`,
        comment: `font-size:46px;color:#fff;background:${c || BLUE};padding:4px 34px;border-radius:999px;box-shadow:7px 7px 0 ${LIME}`,
        label: `font-size:38px;color:${BLUE};background:${c || LIME};padding:2px 26px;border-radius:14px`,
        score: `font-size:58px;color:#fff;background:${c || PINK};padding:2px 36px;border-radius:999px;box-shadow:7px 7px 0 ${BLUE}`,
        tag: `font-size:30px;color:${BLUE};background:${c || '#fff'};padding:0 22px;border-radius:999px;border:4px solid ${BLUE}`,
      }[kind];
      return a.U.node('div', 'ob ot', css, text);
    },
    word(w, k, seed, cue, a) {
      return a.U.node('div', 'ob od', `font-size:${cue.size || 170}px;color:${cue.color || '#fff'};text-shadow:7px 7px 0 ${BLUE},14px 14px 0 ${PINK}`, w);
    },
    wordGap: 22,
    stamp(text, cue, a) { return a.U.node('div', 'ob ostamp', '', text); },
    anim: {
      default: pop,
      speech: (e, rem) => ({o: Math.min(e / .12, 1) * Math.min(rem / .08, 1), dy: 12 * (1 - Math.min(e / .12, 1))}),
      voice: (e, rem) => ({o: Math.min(e / .12, 1) * Math.min(rem / .08, 1), dy: 12 * (1 - Math.min(e / .12, 1))}),
      impact: (e, rem) => ({s: Math.max(VE.U.spring(e, 2.2, 8), 0) * (rem < .1 ? rem / .1 : 1)}),
      stamp: (e) => ({s: e < .3 ? Math.max(VE.U.ease.outBack(e / .3, 2.8), 0) : 1, r: 40 * Math.exp(-e * 8)}),
    },
    decorate: {
      /* A pink disc and a lime ring pop up behind the words. */
      impact(a, cue, pos, seed, els) {
        const {U, root} = a, flip = seed % 2 ? 1 : -1, k0 = a.geo.framed ? .72 : 1;
        const shapes = [
          {d: 430 * k0, dx: -150 * flip * k0, dy: 10, css: `background:${PINK}`, at: 0},
          {d: 300 * k0, dx: 250 * flip * k0, dy: -60 * k0, css: `border:${46 * k0}px solid ${LIME};box-sizing:border-box`, at: .08},
        ].map(s => {
          const el = U.node('div', 'ob', `width:${s.d}px;height:${s.d}px;border-radius:50%;${s.css}`);
          root.insertBefore(el, root.children[1] || null);
          return {...s, el};
        });
        a.items.push({el: shapes[0].el, cue, update(it, t) {
          const rem = cue.end - t;
          for (const s of shapes) {
            const e = t - cue.t - s.at, on = e >= 0 && rem > 0;
            s.el.style.display = on ? '' : 'none';
            if (!on) continue;
            const k = Math.max(U.ease.outBack(Math.min(e / .3, 1), 1.8), 0) * (rem < .12 ? rem / .12 : 1);
            s.el.style.transform = `translate(${pos.x + s.dx - s.d / 2}px,${pos.y + s.dy - s.d / 2}px) scale(${k})`;
          }
        }});
      },
    },
    frame(a) {
      const {U, root} = a, {W, H, win, framed} = a.geo;
      if (!framed) return;
      const dots = `radial-gradient(rgba(255,255,255,.55) 24%,transparent 26%) 0 0/22px 22px`;
      const bar = (top, h, html) => root.appendChild(U.node('div', '', `position:absolute;left:0;top:${top}px;width:${W}px;height:${h}px;background:${BLUE};overflow:hidden`, html));
      const disc = (css) => `<div style="position:absolute;border-radius:50%;box-sizing:border-box;${css}"></div>`;
      bar(0, win.y, disc(`right:-170px;top:-190px;width:480px;height:480px;border:90px solid ${LIME}`) +
        disc(`left:-230px;bottom:-250px;width:440px;height:440px;background:${PINK}`) +
        `<div style="position:absolute;left:420px;top:60px;width:132px;height:110px;background:${dots}"></div>`);
      const bh = H - win.y - win.h;
      bar(win.y + win.h, bh, disc(`right:-140px;bottom:-200px;width:460px;height:460px;border:86px solid ${LIME}`) +
        disc(`left:-200px;bottom:-240px;width:420px;height:420px;background:${PINK}`) +
        `<div style="position:absolute;left:300px;bottom:70px;width:132px;height:110px;background:${dots}"></div>`);
    },
    transitions: {
      default: circles,
      circles,
    },
  });

  function circles(a, cue) {
    const {U, root} = a, {W, H} = a.geo, D = Math.hypot(W, H) * 2.1;
    const spots = [[0, H, PINK], [W, 0, LIME], [W / 2, H / 2, cue.color || BLUE]].map(([x, y, c]) => {
      const el = U.node('div', 'ob', `width:${D}px;height:${D}px;border-radius:50%;background:${c}`);
      root.appendChild(el);
      return {el, x, y};
    });
    a.items.push({el: spots[0].el, cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      spots.forEach(s => { s.el.style.display = on ? '' : 'none'; });
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t);
      spots.forEach((s, i) => {
        /* Pink, lime, then blue; blue covers the frame at the midpoint and then shrinks away. */
        const grow = U.ease.outCubic(U.clamp((p * 2 - i * .22) / .56, 0, 1));
        const k = p < .5 ? grow : (i === 2 ? 1 - U.ease.inCubic((p - .5) * 2) : 0);
        s.el.style.transform = `translate(${s.x - D / 2}px,${s.y - D / 2}px) scale(${Math.max(k, .0001)})`;
      });
    }});
  }
})();
