/* Style: scrapbook (paper scrapbook collage, stop-motion at 12 fps). */
(function () {
  const TEXT = {
    speech: {size: 56, bg: '#f5ebdd'},
    voice: {size: 54, bg: '#fffdf7', color: '#5a4636'},
    comment: {size: 52, bg: '#e3a72f'},
    label: {size: 42, bg: '#fffaf0', color: '#d9472b'},
    score: {size: 60, bg: '#d9472b', color: '#fff8ec'},
    tag: {size: 32, bg: '#6fb7a8', color: '#1f2b28'},
  };
  const PALETTE = ['#f5ebdd', '#e3a72f', '#6fb7a8'];
  const pop = (e) => ({s: 1 + (1 - Math.min(e / .25, 1)) * .38});

  function piece(U, cls, css, html) {
    const outer = U.node('div', 'ob'), sh = U.node('div', 'sb-sh'), p = U.node('div', cls, css, html);
    sh.appendChild(p); outer.appendChild(sh);
    return outer;
  }

  function barClip(U, W, H, edge, seed, side) {
    const n = 90, e = U.tornEdge(seed, n, 20), p = [];
    if (side === 'top') { p.push('0 0', `${W}px 0`); for (let i = n; i >= 0; i--) p.push(`${(i / n * W).toFixed(1)}px ${(edge + e[i] - 10).toFixed(1)}px`); }
    else { p.push(`0 ${H}px`, `${W}px ${H}px`); for (let i = n; i >= 0; i--) p.push(`${(i / n * W).toFixed(1)}px ${(edge - e[i] + 10).toFixed(1)}px`); }
    return `polygon(${p.join(',')})`;
  }

  function route(a) {
    const {U, C, root} = a, r = C.route, W = a.geo.W, y = r.y, x1 = r.x1, x2 = r.x2;
    const tent = `<path d="M${x1 - 56},${y + 28} L${x1 - 6},${y - 36} L${x1 + 4},${y - 36} L${x1 + 56},${y + 28} Z" fill="#e3a72f" stroke="#5b4630" stroke-width="4" stroke-linejoin="round"/>
      <path d="M${x1 - 16},${y + 28} L${x1},${y - 6} L${x1 + 16},${y + 28} Z" fill="#5b4630"/>
      <path d="M${x1 - 64},${y + 30} L${x1 + 64},${y + 30}" stroke="#5b4630" stroke-width="4" stroke-linecap="round"/>`;
    const swing = `<path d="M${x2 - 46},${y + 32} L${x2 - 40},${y - 38} M${x2 + 46},${y + 32} L${x2 + 40},${y - 38} M${x2 - 54},${y - 38} L${x2 + 54},${y - 38}" stroke="#5b4630" stroke-width="6" stroke-linecap="round"/>
      <path d="M${x2 - 14},${y - 38} L${x2 - 14},${y + 6} M${x2 + 14},${y - 38} L${x2 + 14},${y + 6}" stroke="#5b4630" stroke-width="2.5"/>
      <path d="M${x2 - 22},${y + 6} L${x2 + 22},${y + 6}" stroke="#d9472b" stroke-width="7" stroke-linecap="round"/>`;
    const el = U.node('div', 'sb-route', 'position:absolute;left:0;top:0',
      `<svg width="${W}" height="${a.geo.H}"><path class="track" d="M${x1 + 50},${y} C${(x1 + x2) / 2},${y - 40} ${(x1 + x2) / 2},${y + 40} ${x2 - 50},${y}" fill="none" stroke="#5b4630" stroke-width="5" stroke-dasharray="14 12" stroke-linecap="round"/>${tent}${swing}
       <text x="${x1}" y="${y + 70}" text-anchor="middle">${r.from}</text><text x="${x2}" y="${y + 70}" text-anchor="middle">${r.to}</text>
       <circle class="dot" r="15" fill="#d9472b" stroke="#fffaf0" stroke-width="5"/></svg>`);
    root.appendChild(el);
    const track = el.querySelector('.track'), dot = el.querySelector('.dot'), len = track.getTotalLength();
    a.decor.push((t) => {
      const pts = r.progress;
      let p = pts[pts.length - 1].p;
      for (let i = 1; i < pts.length; i++) if (t <= pts[i].t) { const A = pts[i - 1], B = pts[i]; p = A.p + (B.p - A.p) * Math.max(0, (t - A.t) / (B.t - A.t)); break; }
      const pt = track.getPointAtLength(len * p);
      dot.setAttribute('cx', pt.x); dot.setAttribute('cy', pt.y);
    });
  }

  registerStyle({
    name: 'scrapbook',
    holdFps: 12,
    boil: {fps: 6, rot: 1.6, px: 3},
    ink: '#2b2a28',
    accent: '#d9472b',
    stickerCss: 'filter:drop-shadow(4px 7px 5px rgba(40,25,10,.42))',
    css: `
      .style-scrapbook .sb-sh{filter:drop-shadow(4px 7px 5px rgba(40,25,10,.42))}
      .style-scrapbook .sb-piece{padding:12px 40px;color:#2b2a28;white-space:nowrap;line-height:1.5;font-family:var(--display,'Mali');font-weight:700}
      .style-scrapbook .sb-stamp{border:9px solid #c8323c;color:#c8323c;border-radius:16px;padding:4px 30px;font-family:var(--display,'Mali');font-weight:700;font-size:72px;line-height:1.45;white-space:nowrap;opacity:.9}
      .style-scrapbook .sb-tape{position:absolute;background:rgba(238,214,150,.72);box-shadow:0 1px 3px rgba(0,0,0,.25)}
      .style-scrapbook .sb-paper{position:absolute;left:0;top:0;width:100%}
      .style-scrapbook .sb-postmark{position:absolute;border:5px solid #d9472b;border-radius:50%;color:#d9472b;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:.82;line-height:1.3;text-align:center;font-family:var(--display,'Mali');font-weight:700;font-size:29px}
      .style-scrapbook .sb-route text{font-family:var(--display,'Mali');font-weight:700;font-size:28px;fill:#5b4630}`,
    tilt: {speech: -1, voice: 1, comment: 2, label: -2.5, score: -2, tag: 2},
    text(kind, text, seed, cue, a) {
      const s = TEXT[kind];
      return piece(a.U, 'sb-piece', `font-size:${s.size}px;background-color:${cue.color || s.bg};background-image:${a.U.grain()};clip-path:${a.U.tornBox(seed)};${s.color ? 'color:' + s.color : ''}`, text);
    },
    word(w, k, seed, cue, a) {
      return piece(a.U, 'sb-piece', `font-size:${cue.size || 160}px;background-color:${PALETTE[k % 3]};background-image:${a.U.grain()};clip-path:${a.U.tornBox(seed + k)}`, w);
    },
    wordTilt: (k) => (k % 2 ? 3.2 : -3.2),
    stamp(text, cue, a) { return a.U.node('div', 'ob sb-stamp', '', text); },
    anim: {
      default: pop,
      stamp: (e) => ({s: e < 2 / 12 ? 1.9 - e * 12 * .45 : 1}),
    },
    frame(a) {
      const {U, C, root} = a, {W, H, win, framed} = a.geo;
      const bars = [];
      if (framed) {
        [['top', win.y, 11, '0 6px 7px'], ['bottom', win.y + win.h, 29, '0 -6px 7px']].forEach(([side, edge, seed, sh]) => {
          const wrap = U.node('div', '', `position:absolute;inset:0;filter:drop-shadow(${sh} rgba(30,20,8,.5))`);
          const p = U.node('div', 'sb-paper', `height:${H}px;background-image:${U.grain()};clip-path:${barClip(U, W, H, edge, seed, side)}`);
          wrap.appendChild(p); root.appendChild(wrap); bars.push(p);
        });
      }
      const top = framed ? win.y : 0, bottom = framed ? win.y + win.h : H;
      [[70, top - 22, -14], [W - 230, top - 18, 11], [90, bottom - 26, 9], [W - 240, bottom - 30, -12]].forEach(([x, y, r]) =>
        root.appendChild(U.node('div', 'sb-tape', `left:${x}px;top:${Math.max(y, -10)}px;width:160px;height:46px;transform:rotate(${r}deg)`)));
      if (C.route && framed) route(a);
      let post = null;
      if (C.postmarks) {
        post = U.node('div', 'sb-postmark', `left:${W - 262}px;top:56px;width:196px;height:196px;transform:rotate(11deg)`);
        root.appendChild(post);
      }
      const tones = C.tones || [{t: 0, color: '#dcc9a8'}];
      a.decor.push((t) => {
        const tone = U.latest(tones, t).color;
        bars.forEach(b => b.style.backgroundColor = tone);
        if (post) {
          const html = U.latest(C.postmarks, t).lines.map(s => `<div>${s}</div>`).join('');
          if (post.innerHTML !== html) post.innerHTML = html;
        }
      });
    },
    transitions: {
      default: tear,
      tear,
    },
  });

  function tear(a, cue, seed) {
    const {U, root} = a, {W, H} = a.geo;
    const el = U.node('div', 'ob sb-sh', `width:${W}px;height:${H + 80}px`);
    el.appendChild(U.node('div', 'sb-paper', `height:${H + 80}px;background-color:${cue.color || '#efe4cf'};background-image:${U.grain()};clip-path:${U.tornBox(seed)}`));
    root.appendChild(el);
    a.items.push({el, cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      el.style.display = on ? '' : 'none';
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t);
      const y = p < .5 ? -H * (1 - p * 2) : H * (p - .5) * 2;
      el.style.transform = `translate(0,${y - 40}px) rotate(${(p - .5) * 3}deg)`;
    }});
  }
})();
