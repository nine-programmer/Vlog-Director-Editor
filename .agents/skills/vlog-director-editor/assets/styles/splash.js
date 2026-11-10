/* Style: splash (thin white type with bright liquid ribbons that whip past the words).
 *
 * The strokes are filled shapes, not outlines: a ribbon is thick in the body and pointed at both
 * ends, its head runs along a path, the tail follows and sheds drops, as liquid thrown in the air does.
 */
(function () {
  const COLORS = ['#1fb6ff', '#ff1f6b', '#8be21a', '#ffc21f', '#b51fff'];
  const DARK = '#101014';
  const NS = 'http://www.w3.org/2000/svg';
  const SHADOW = 'text-shadow:0 2px 12px rgba(0,0,0,.6),0 0 2px rgba(0,0,0,.5)';
  const tint = (seed, n = 0) => COLORS[(Math.floor(seed / 101) + n) % COLORS.length];
  const inOut = (x) => (x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const rise = (e, rem) => {
    const i = Math.min(e / .3, 1);
    return {o: i * Math.min(rem / .25, 1), dy: 18 * (1 - VE.U.ease.outCubic(i))};
  };
  /* A static pointed stroke for CSS backgrounds (comment underline, label bar). */
  const lens = (c, vertical) => `url("data:image/svg+xml,${encodeURIComponent(
    `<svg xmlns='http://www.w3.org/2000/svg' viewBox='${vertical ? '0 0 14 100' : '0 0 100 12'}' preserveAspectRatio='none'><path fill='${c}' d='${vertical
      ? 'M6,0 Q13,38 9,100 Q-2,60 6,0Z' : 'M0,7 Q30,-1 62,1 Q90,3 100,6 Q70,12 38,11 Q12,11 0,7Z'}'/></svg>`)}")`;

  /* Points and normals along a path, so a ribbon can be cut from any stretch of it. */
  function sample(svg, d) {
    const p = document.createElementNS(NS, 'path');
    p.setAttribute('d', d);
    svg.appendChild(p);
    const len = p.getTotalLength(), n = Math.max(24, Math.ceil(len / 10)), pts = [];
    for (let i = 0; i <= n; i++) { const q = p.getPointAtLength(len * i / n); pts.push([q.x, q.y]); }
    svg.removeChild(p);
    const nor = pts.map((_, i) => {
      const a = pts[Math.max(i - 1, 0)], b = pts[Math.min(i + 1, n)], l = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
      return [-(b[1] - a[1]) / l, (b[0] - a[0]) / l];
    });
    return {len, n, pts, nor};
  }
  function at(sm, f) {
    const x = Math.min(Math.max(f, 0), 1) * sm.n, i = Math.min(Math.floor(x), sm.n - 1), k = x - i;
    const a = sm.pts[i], b = sm.pts[i + 1], na = sm.nor[i], nb = sm.nor[i + 1];
    return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, na[0] + (nb[0] - na[0]) * k, na[1] + (nb[1] - na[1]) * k];
  }
  /* The outline of the ribbon between tail and head (fractions of the path). */
  function shape(sm, tail, head, w, seed) {
    const span = (head - tail) * sm.len;
    if (span < 3) return '';
    const steps = Math.max(8, Math.ceil(span / 9)), thick = w * Math.min(1, span / (w * 4)), L = [], R = [];
    for (let i = 0; i <= steps; i++) {
      const u = i / steps, f = tail + (head - tail) * u, [x, y, nx, ny] = at(sm, f);
      /* Thin tail, body thickest behind the head, blunt point at the head. */
      const prof = Math.pow(Math.sin(Math.PI * Math.pow(u, 1.7)), .7);
      const half = thick * prof * (1 + .16 * Math.sin(f * sm.len / 41 + seed)) / 2;
      L.push(`${(x + nx * half * 1.2).toFixed(1)},${(y + ny * half * 1.2).toFixed(1)}`);
      R.push(`${(x - nx * half * .8).toFixed(1)},${(y - ny * half * .8).toFixed(1)}`);
    }
    return `M${L.join('L')}L${R.reverse().join('L')}Z`;
  }
  const dot = (x, y, r) => (r < .4 ? '' : `M${(x - r).toFixed(1)},${y.toFixed(1)}a${r.toFixed(1)},${r.toFixed(1)} 0 1,0 ${(2 * r).toFixed(1)},0a${r.toFixed(1)},${r.toFixed(1)} 0 1,0 ${(-2 * r).toFixed(1)},0`);

  /* One ribbon. o: {c, w, from, grow, stay, drops, seed, dur}. Returns draw(e) for seconds since the cue began.
   * stay=false: the tail chases the head and the ribbon is gone in under a second.
   * stay=true: the ribbon rests on its path and its tail runs out as the cue ends. */
  function ribbon(svg, d, o) {
    const U = VE.U, sm = sample(svg, d), grow = o.grow ?? .42, from = o.from ?? 0, r = U.rng(o.seed + 17);
    const body = document.createElementNS(NS, 'path'), spray = document.createElementNS(NS, 'path');
    body.setAttribute('fill', o.c); spray.setAttribute('fill', o.c);
    svg.appendChild(body); svg.appendChild(spray);
    const head = (e) => U.ease.outCubic(U.clamp((e - from) / grow, 0, 1));
    const tail = o.stay
      ? (e) => inOut(U.clamp((e - (o.dur - .34)) / .3, 0, 1))
      : (e) => inOut(U.clamp((e - from - grow * .5) / (grow * 1.05), 0, 1));
    /* Drops leave the ribbon where the tail lets go of the path. */
    const drops = [];
    for (let i = 0; i < (o.drops || 0); i++) {
      const f = .12 + .8 * r(), side = r() < .5 ? -1 : 1, size = o.w * (.14 + .2 * r()), fly = 26 + 60 * r(), along = (r() - .3) * 70;
      let born = from;
      while (tail(born) < f && born < o.dur) born += 1 / 120;
      drops.push({f, side, size, fly, along, born, life: .3 + .25 * r()});
    }
    return (e) => {
      const h = head(e), t = tail(e);
      body.setAttribute('d', e < from || t >= 1 ? '' : shape(sm, t, Math.max(h, t), o.w, o.seed));
      let s = '';
      for (const p of drops) {
        const age = (e - p.born) / p.life;
        if (age <= 0 || age >= 1) continue;
        const [x, y, nx, ny] = at(sm, p.f), k = U.ease.outCubic(age);
        s += dot(x + nx * p.side * p.fly * k + ny * p.along * k, y + ny * p.side * p.fly * k - nx * p.along * k + 30 * age * age, p.size * (1 - age * age));
      }
      spray.setAttribute('d', s);
    };
  }

  /* A drop that pops in, hangs for a moment, splits in two and is gone. */
  function blob(svg, x, y, r, c, from) {
    const U = VE.U, el = document.createElementNS(NS, 'path');
    el.setAttribute('fill', c);
    svg.appendChild(el);
    const oval = (cx, cy, rx, ry) => (rx < .4 ? '' : `M${(cx - rx).toFixed(1)},${cy.toFixed(1)}a${rx.toFixed(1)},${ry.toFixed(1)} 0 1,0 ${(2 * rx).toFixed(1)},0a${rx.toFixed(1)},${ry.toFixed(1)} 0 1,0 ${(-2 * rx).toFixed(1)},0`);
    return (e) => {
      const t = e - from;
      if (t <= 0 || t >= .8) { el.setAttribute('d', ''); return; }
      if (t < .34) {
        const g = U.ease.outBack(Math.min(t / .2, 1), 2.4), st = 1 + .5 * Math.max(0, 1 - t / .2);
        el.setAttribute('d', oval(x, y - 40 * (1 - Math.min(t / .2, 1)), r * g / Math.sqrt(st), r * g * st));
      } else {
        const p = (t - .34) / .46, k = U.ease.outCubic(p), sh = 1 - p * p;
        el.setAttribute('d', oval(x - r * 1.1 * k, y + r * .5 * k, r * .72 * sh, r * .72 * sh) + oval(x + r * .9 * k, y - r * .7 * k, r * .5 * sh, r * .5 * sh));
      }
    };
  }

  /* A full-frame SVG layer whose shapes are redrawn on every seek. */
  function layer(a, cue, make) {
    const {U, root} = a, {W, H} = a.geo;
    const el = U.node('div', 'ob', `width:${W}px;height:${H}px`, `<svg width="${W}" height="${H}"></svg>`);
    root.appendChild(el);
    const draws = make(el.firstChild, cue.end - cue.t);
    a.items.push({el, cue, update(it, t) {
      const e = t - cue.t, on = e >= 0 && t < cue.end;
      el.style.display = on ? '' : 'none';
      if (on) draws.forEach(d => d(e));
    }});
  }

  /* A hand-drawn loop: slightly more than one turn, so the ends overlap. */
  function loop(cx, cy, rx, ry, rot = 0) {
    const c = Math.cos(rot), s = Math.sin(rot), p = [];
    for (let i = 0; i <= 44; i++) {
      const g = -2.5 + i / 44 * Math.PI * 2.16, k = 1 + .05 * i / 44;
      const x = Math.cos(g) * rx * k, y = Math.sin(g) * ry * k;
      p.push(`${(cx + x * c - y * s).toFixed(1)},${(cy + x * s + y * c).toFixed(1)}`);
    }
    return `M${p.join('L')}`;
  }

  registerStyle({
    name: 'splash',
    holdFps: null,
    ink: '#ffc21f',
    accent: '#ff1f6b',
    highlight: '#ffc21f',
    stickerCss: 'filter:drop-shadow(0 6px 14px rgba(0,0,0,.45))',
    css: `
      .style-splash .pt{font-family:'Anuphan';font-weight:500;white-space:nowrap;line-height:1.6;color:#fff;${SHADOW}}
      .style-splash .pd{font-family:var(--display,'Anuphan');font-weight:200;white-space:nowrap;line-height:1.4;color:#fff;${SHADOW}}`,
    text(kind, text, seed, cue, a) {
      const U = a.U, c = cue.color;
      const css = {
        speech: `font-size:46px;${c ? 'color:' + c : ''}`,
        voice: `font-size:44px;color:${c || '#ffe9a8'}`,
        comment: `font-size:46px;font-weight:300;padding:0 14px 12px;background:${lens(c || tint(seed))} left bottom/100% 16px no-repeat`,
        label: `font-size:34px;font-weight:300;letter-spacing:.18em;padding-left:30px;background:${lens(c || tint(seed), true)} left center/16px 82% no-repeat`,
        score: `font-size:72px;padding:0 18px 10px;background:${lens(c || tint(seed, 1))} left bottom/100% 18px no-repeat`,
        tag: `font-size:28px;font-weight:600;padding:0 22px;border-radius:999px;background:${c || tint(seed, 2)};text-shadow:none`,
      }[kind];
      return U.node('div', `ob ${kind === 'score' ? 'pd' : 'pt'}`, css, text);
    },
    word(w, k, seed, cue, a) {
      return a.U.node('div', 'ob pd', `font-size:${cue.size || 150}px;${cue.color ? 'color:' + cue.color : ''}`, w);
    },
    wordGap: 34,
    tilt: {stamp: -4},
    anim: {
      default: rise,
      impact: (e, rem) => ({clip: 100 * (1 - VE.U.ease.outCubic(Math.min(e / .45, 1))), o: Math.min(rem / .25, 1)}),
      stamp: (e, rem) => ({o: Math.min(e / .15, 1) * Math.min(rem / .2, 1), s: .85 + .15 * VE.U.ease.outBack(Math.min(e / .3, 1), 2)}),
    },
    build: {
      /* The verdict sits inside a loop of liquid that draws itself around it. */
      stamp(a, cue, seed) {
        const el = a.U.node('div', 'ob pd', 'font-size:76px;padding:14px 60px', cue.text);
        const pos = Object.assign(a.defaults('stamp'), cue.x !== undefined ? {x: cue.x} : {}, cue.y !== undefined ? {y: cue.y} : {});
        const tilt = cue.tilt ?? -4;
        const it = a.addItem(el, cue, {...pos, seed, tilt, anim: 'stamp', text: cue.text});
        layer(a, cue, (svg, dur) => [
          ribbon(svg, loop(pos.x, pos.y, it.w * .56, it.h * .62, tilt * Math.PI / 180), {c: cue.color || tint(seed, 1), w: 22, grow: .5, stay: true, dur, seed}),
          blob(svg, pos.x + it.w * .62, pos.y - it.h * .62, 20, tint(seed, 3), .3),
        ]);
      },
      ring(a, cue, seed) {
        layer(a, cue, (svg, dur) => [
          ribbon(svg, loop(cue.x, cue.y, cue.rx ?? 120, cue.ry ?? 90, -.12), {c: cue.color || tint(seed), w: 24, grow: .55, stay: true, dur, seed}),
        ]);
      },
      /* A ribbon thrown from one point to the other; the head is a second, short ribbon. */
      arrow(a, cue, seed) {
        const [x1, y1] = cue.from, [x2, y2] = cue.to, c = cue.color || tint(seed, 3);
        const mx = (x1 + x2) / 2 + (y2 - y1) * .25, my = (y1 + y2) / 2 - (x2 - x1) * .25;
        const g = Math.atan2(y2 - my, x2 - mx), L = 52;
        const tip = `M${x2 - L * Math.cos(g - .55)},${y2 - L * Math.sin(g - .55)} L${x2 + 6 * Math.cos(g)},${y2 + 6 * Math.sin(g)} L${x2 - L * Math.cos(g + .55)},${y2 - L * Math.sin(g + .55)}`;
        layer(a, cue, (svg, dur) => [
          ribbon(svg, `M${x1},${y1} Q${mx},${my} ${x2},${y2}`, {c, w: 20, grow: .4, stay: true, dur, seed}),
          ribbon(svg, tip, {c, w: 17, from: .28, grow: .22, stay: true, dur, seed: seed + 5}),
        ]);
      },
    },
    decorate: {
      /* A ribbon whips over the words and is gone, a second one settles under them, drops fly. */
      impact(a, cue, pos, seed, els) {
        const words = a.items.slice(-els.length), first = words[0], last = words[words.length - 1];
        const L = first.x - first.w * first.fit / 2, R = last.x + last.w * last.fit / 2, w = R - L, h = first.h * first.fit, y = pos.y;
        layer(a, cue, (svg, dur) => [
          ribbon(svg, `M${L - 90},${y + h * .55} C${L - 60},${y - h * .9} ${L + w * .55},${y - h * 1.15} ${R + 40},${y - h * .35} S${R + 60},${y + h * .7} ${R - w * .1},${y + h * .78}`,
            {c: tint(seed), w: 34, from: .04, grow: .5, drops: 8, dur, seed}),
          ribbon(svg, `M${L + w * .04},${y + h * .5} Q${L + w * .5},${y + h * .66} ${L + w * .9},${y + h * .46}`,
            {c: tint(seed, 1), w: 22, from: .34, grow: .36, stay: true, dur, seed: seed + 3}),
          ribbon(svg, `M${L - 20},${y - h * .1} q-50,-70 -10,-150`, {c: tint(seed, 3), w: 20, from: .22, grow: .3, drops: 3, dur, seed: seed + 9}),
          blob(svg, R + 34, y - h * .62, 24, tint(seed, 3), .46),
        ]);
      },
    },
    frame(a) {
      const {U, root} = a, {W, H, win, framed} = a.geo;
      if (!framed) return;
      const bar = (top, h, d, c, seed) => {
        const el = U.node('div', '', `position:absolute;left:0;top:${top}px;width:${W}px;height:${h}px;background:${DARK};overflow:hidden`, `<svg width="${W}" height="${h}"></svg>`);
        root.appendChild(el);
        const svg = el.firstChild, p = document.createElementNS(NS, 'path');
        p.setAttribute('fill', c);
        p.setAttribute('d', shape(sample(svg, d), 0, 1, 26, seed));
        svg.appendChild(p);
      };
      bar(0, win.y, `M${W * .5},70 Q${W * .78},20 ${W + 40},110`, COLORS[0], 2);
      const bh = H - win.y - win.h;
      bar(win.y + win.h, bh, `M${W * .55},${bh - 120} Q${W * .25},${bh - 60} -40,${bh - 150}`, COLORS[1], 5);
    },
    transitions: {
      default: swipe,
      swipe,
    },
  });

  function swipe(a, cue, seed) {
    const {U, root} = a, {W, H} = a.geo, D = Math.hypot(W, H);
    const bands = [0, 1, 2].map(i => {
      const el = U.node('div', 'ob', `width:${D * 1.5}px;height:${D * 1.3}px;border-radius:${D * .2}px;background:${cue.color && i === 1 ? cue.color : tint(seed, i)}`);
      root.appendChild(el);
      return el;
    });
    a.items.push({el: bands[0], cue, update(it, t) {
      const on = t >= cue.t && t < cue.end;
      bands.forEach(b => { b.style.display = on ? '' : 'none'; });
      if (!on) return;
      const p = (t - cue.t) / (cue.end - cue.t);
      bands.forEach((b, i) => {
        /* Each band follows the one before; the middle one covers the frame at the midpoint. */
        const q = U.clamp((p - i * .12) / .76, 0, 1);
        const x = q < .5 ? -D * 1.6 * (1 - U.ease.outCubic(q * 2)) : D * 1.6 * U.ease.inCubic((q - .5) * 2);
        b.style.transform = `translate(${(W - D * 1.5) / 2 + x}px,${(H - D * 1.3) / 2}px) rotate(-18deg)`;
      });
    }});
  }
})();
