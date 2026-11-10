/* Style: outdoor (camp badge: trail-sign boxes, round badge, forest green, cream and orange). */
(function () {
  const GREEN = '#1f3d2b', CREAM = '#f3e9cf', ORANGE = '#e0752a';
  const pop = (e, rem) => {
    const s = e < .22 ? Math.max(VE.U.ease.outBack(e / .22, 2.2), 0) : 1;
    return {s: rem < .1 ? s * rem / .1 : s};
  };
  registerStyle({
    name: 'outdoor',
    holdFps: null,
    ink: CREAM,
    accent: ORANGE,
    highlight: ORANGE,
    stickerCss: `filter:drop-shadow(6px 6px 0 ${GREEN})`,
    css: `
      .style-outdoor .ot{font-family:var(--display,'K2D');font-weight:800;white-space:nowrap;line-height:1.45;border:5px solid ${GREEN};box-shadow:7px 7px 0 ${GREEN}}
      .style-outdoor .ow{font-family:var(--display,'K2D');font-weight:800;white-space:nowrap;line-height:1.3;paint-order:stroke fill}
      .style-outdoor .ostamp{font-family:var(--display,'K2D');font-weight:800;font-size:62px;color:${CREAM};background:${GREEN};border:6px solid ${CREAM};outline:6px solid ${GREEN};border-radius:999px;padding:4px 44px;white-space:nowrap;line-height:1.4}
      .style-outdoor .obadge{position:absolute;box-sizing:border-box;border:6px solid ${CREAM};outline:6px solid ${GREEN};border-radius:50%;background:${GREEN};color:${CREAM};display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:1.3;text-align:center;font-family:var(--display,'K2D');font-weight:800;font-size:27px}`,
    tilt: {comment: 2, label: -2, score: -2, tag: 2},
    text(kind, text, seed, cue, a) {
      const c = cue.color;
      const css = {
        speech: `font-size:50px;color:${GREEN};background:${c || CREAM};padding:4px 28px`,
        voice: `font-size:48px;color:${CREAM};background:${c || GREEN};padding:4px 28px;border-color:${CREAM};box-shadow:7px 7px 0 rgba(0,0,0,.35)`,
        comment: `font-size:46px;color:${GREEN};background:${c || ORANGE};padding:4px 26px`,
        label: `font-size:38px;color:${GREEN};background:${c || CREAM};padding:2px 24px`,
        score: `font-size:58px;color:${GREEN};background:${c || ORANGE};padding:2px 28px`,
        tag: `font-size:30px;color:${GREEN};background:${c || CREAM};padding:0 18px;border-width:4px;box-shadow:5px 5px 0 ${GREEN}`,
      }[kind];
      return a.U.node('div', 'ob ot', css, text);
    },
    word(w, k, seed, cue, a) {
      return a.U.node('div', 'ob', '', `<div class="ow" style="font-size:${cue.size || 160}px;color:${cue.color || CREAM};-webkit-text-stroke:14px ${GREEN};filter:drop-shadow(8px 8px 0 ${ORANGE})">${w}</div>`);
    },
    wordGap: 12,
    wordTilt: (k) => (k % 2 ? 3 : -3),
    stamp(text, cue, a) { return a.U.node('div', 'ob ostamp', '', text); },
    anim: {
      default: pop,
      impact: (e, rem) => ({s: Math.max(VE.U.spring(e, 2.2, 8), 0) * (rem < .1 ? rem / .1 : 1)}),
      stamp: (e) => {
        const p = Math.min(e / .12, 1);
        return {s: 2 - p * p, o: p, r: -14 * (1 - p)};
      },
    },
    frame(a) {
      const {U, C, root} = a, {W, H, win, framed} = a.geo;
      if (framed) {
        const css = `position:absolute;left:0;width:${W}px;box-sizing:border-box;background:repeating-radial-gradient(circle at 20% 130%,rgba(243,233,207,.09) 0 2px,transparent 2px 38px),${GREEN}`;
        root.appendChild(U.node('div', '', `${css};top:0;height:${win.y}px;border-bottom:6px solid ${CREAM}`));
        root.appendChild(U.node('div', '', `${css};top:${win.y + win.h}px;height:${H - win.y - win.h}px;border-top:6px solid ${CREAM}`));
      }
      if (!C.postmarks) return;
      const badge = U.node('div', 'obadge', `left:${W - 262}px;top:${a.geo.vertical ? 124 : 56}px;width:196px;height:196px;transform:rotate(8deg)`);
      root.appendChild(badge);
      a.decor.push((t) => {
        const html = U.latest(C.postmarks, t).lines.map(s => `<div>${s}</div>`).join('');
        if (badge.innerHTML !== html) badge.innerHTML = html;
      });
    },
    transitions: {
      default: badgeWipe,
      badge: badgeWipe,
    },
  });

  function badgeWipe(a, cue) {
    const {U, root} = a, {W, H} = a.geo, D = Math.hypot(W, H) * 1.15;
    const el = U.node('div', 'ob', `width:${D}px;height:${D}px;box-sizing:border-box;border-radius:50%;background:${cue.color || GREEN};border:22px solid ${CREAM}`);
    root.appendChild(el);
    a.items.push({el, cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      el.style.display = on ? '' : 'none';
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t);
      el.style.transform = `translate(${(W - D) / 2}px,${(H - D) / 2}px) scale(${p < .5 ? U.ease.outCubic(p * 2) : 1})`;
      el.style.opacity = p < .5 ? 1 : (1 - p) * 2;
    }});
  }
})();
