/* Style: comic (comic-book impact: halftone, starbursts, speed lines, hard shadows). */
(function () {
  const RED = '#e5262a', YELLOW = '#ffd400';
  registerStyle({
    name: 'comic',
    holdFps: null,
    ink: '#000',
    accent: RED,
    stickerCss: 'filter:drop-shadow(8px 8px 0 #000)',
    css: `
      .style-comic .cb{font-family:'Bai Jamjuree';font-weight:700;white-space:nowrap;line-height:1.45;border:5px solid #000}
      .style-comic .cd{font-family:var(--display,'Prompt');font-weight:800;font-style:italic;white-space:nowrap;line-height:1.3;paint-order:stroke fill}
      .style-comic .cstamp{font-family:var(--display,'Prompt');font-weight:800;font-style:italic;font-size:66px;color:#fff;background:${RED};border:6px solid #000;padding:2px 30px;box-shadow:10px 10px 0 #000;white-space:nowrap;line-height:1.35}`,
    tilt: {comment: 2, label: -2, score: -3, tag: 2},
    text(kind, text, seed, cue, a) {
      const c = cue.color;
      const css = {
        speech: `font-size:50px;color:#000;background:${c || '#fff'};padding:4px 26px`,
        voice: `font-size:48px;color:#000;background:${c || '#fff6c8'};padding:4px 26px;font-style:italic`,
        comment: `font-size:48px;color:#000;background:${c || YELLOW};padding:4px 24px;box-shadow:7px 7px 0 #000`,
        label: `font-size:38px;color:#fff;background:${c || RED};padding:2px 20px`,
        score: `font-size:58px;color:#000;background:${c || YELLOW};padding:2px 26px;box-shadow:9px 9px 0 #000;font-family:'Prompt';font-weight:800;font-style:italic`,
        tag: `font-size:30px;color:#000;background:${c || '#fff'};padding:0 16px`,
      }[kind];
      return a.U.node('div', 'ob cb', css, text);
    },
    word(w, k, seed, cue, a) {
      return a.U.node('div', 'ob', '', `<div class="cd" style="font-size:${cue.size || 180}px;color:${cue.color || YELLOW};-webkit-text-stroke:16px #000;filter:drop-shadow(12px 12px 0 #000)">${w}</div>`);
    },
    wordGap: 6,
    wordTilt: (k) => (k % 2 ? 3 : -5),
    stamp(text, cue, a) { return a.U.node('div', 'ob cstamp', '', text); },
    anim: {
      default: (e, rem) => {
        const s = e < .2 ? Math.max(VE.U.ease.outBack(e / .2, 2.2), 0) : 1;
        return {s: rem < .08 ? s * rem / .08 : s};
      },
      speech: (e) => ({sx: Math.min(e / .12, 1)}),
      voice: (e) => ({sx: Math.min(e / .12, 1)}),
      impact: (e, rem) => {
        const p = Math.min(e / .1, 1);
        return {s: 3 - 2 * p * p, o: p, dx: e > .1 && e < .35 ? Math.sin(e * 90) * 8 * (1 - (e - .1) / .25) : 0};
      },
      stamp: (e) => {
        const p = Math.min(e / .1, 1);
        return {s: 2.4 - 1.4 * p * p, o: p};
      },
    },
    decorate: {
      impact(a, cue, pos, seed, els) {
        const {U, root} = a, {W, vertical} = a.geo;
        const r = U.rng(seed), pts = [];
        for (let i = 0; i < 32; i++) {
          const ang = i / 32 * Math.PI * 2, R = i % 2 ? 46 + r() * 4 : 29 + r() * 6;
          pts.push(`${(50 + Math.cos(ang) * R).toFixed(1)},${(50 + Math.sin(ang) * R).toFixed(1)}`);
        }
        const bw = vertical ? W * .98 : W * .62, bh = vertical ? 560 : 640;
        const burst = U.node('div', 'ob', `width:${bw}px;height:${bh}px`,
          `<svg viewBox="0 0 100 100" preserveAspectRatio="none" width="100%" height="100%"><polygon points="${pts.join(' ')}" fill="${RED}" stroke="#000" stroke-width=".8"/></svg>`);
        const lines = U.node('div', 'ob', `width:${W * 1.6}px;height:${W * 1.6}px;background:repeating-conic-gradient(from 0deg at 50% 50%,rgba(0,0,0,.85) 0 1.1deg,transparent 1.1deg 7deg);-webkit-mask:radial-gradient(circle,transparent 30%,#000 60%);mask:radial-gradient(circle,transparent 30%,#000 60%)`);
        root.insertBefore(lines, els[0]);
        root.insertBefore(burst, els[0]);
        a.items.push({el: burst, cue, update(it, t) {
          const e = t - cue.t, on = e >= 0 && t < cue.end;
          burst.style.display = on ? '' : 'none';
          if (on) burst.style.transform = `translate(${pos.x - bw / 2}px,${pos.y - bh / 2}px) scale(${Math.min(e / .08, 1)})`;
        }});
        a.items.push({el: lines, cue, update(it, t) {
          const e = t - cue.t, on = e >= 0 && e < .45;
          lines.style.display = on ? '' : 'none';
          if (on) lines.style.transform = `translate(${pos.x - W * .8}px,${pos.y - W * .8}px) rotate(${e * 20}deg)`;
        }});
      },
    },
    frame(a) {
      const {U, root} = a, {W, H, win, framed} = a.geo;
      if (!framed) return;
      const css = `position:absolute;left:0;width:${W}px;background:${YELLOW} radial-gradient(${RED} 28%,transparent 30%) 0 0/26px 26px`;
      root.appendChild(U.node('div', '', `${css};top:0;height:${win.y}px;border-bottom:10px solid #000`));
      root.appendChild(U.node('div', '', `${css};top:${win.y + win.h}px;height:${H - win.y - win.h}px;border-top:10px solid #000`));
    },
    transitions: {
      default: burstPanel,
      burst: burstPanel,
    },
  });

  function burstPanel(a, cue) {
    const {U, root} = a, {W, H} = a.geo;
    const el = U.node('div', 'ob', `width:${W}px;height:${H}px;background:${YELLOW} radial-gradient(${RED} 28%,transparent 30%) 0 0/34px 34px;border:12px solid #000;box-sizing:border-box`);
    root.appendChild(el);
    a.items.push({el, cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      el.style.display = on ? '' : 'none';
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t);
      const s = p < .5 ? U.ease.outCubic(p * 2) : 1;
      el.style.transform = `scale(${s}) rotate(${(1 - s) * 25}deg)`;
      el.style.opacity = p < .5 ? 1 : (1 - p) * 2;
    }});
  }
})();
