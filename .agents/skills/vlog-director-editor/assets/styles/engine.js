/* Overlay engine shared by every style, the style preview page and the renderer.
 *
 * A style file calls registerStyle({...}). A composition (comp) selects it with comp.style.
 * The engine is seek-based: seek(t) draws the exact frame for time t, so preview and
 * render produce identical frames.
 *
 * Public API (window): init(comp, host?) -> Promise, seek(t), layout() -> text boxes for QA.
 */
(function () {
  const STYLES = {};
  window.registerStyle = (s) => { STYLES[s.name] = s; };
  window.listStyles = () => Object.values(STYLES);

  const TEXT_KINDS = ['speech', 'voice', 'comment', 'label', 'score', 'tag'];

  const U = {
    clamp: (v, a, b) => Math.min(Math.max(v, a), b),
    lerp: (a, b, p) => a + (b - a) * p,
    rng(seed) { let s = Math.abs(Math.floor(seed)) % 2147483646 + 1; return () => (s = s * 16807 % 2147483647) / 2147483647; },
    hash(n) { const r = U.rng(n * 7919 + 13); r(); return r(); },
    ease: {
      outCubic: (x) => 1 - Math.pow(1 - x, 3),
      inCubic: (x) => x * x * x,
      outBack: (x, k = 1.9) => 1 + (k + 1) * Math.pow(x - 1, 3) + k * Math.pow(x - 1, 2),
      inOutSine: (x) => -(Math.cos(Math.PI * x) - 1) / 2,
      outExpo: (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x)),
    },
    /* damped spring from 0 to 1 with overshoot */
    spring: (x, freq = 2.2, damp = 7) => 1 - Math.exp(-damp * x) * Math.cos(2 * Math.PI * freq * x),
    node(tag, cls, css, html) {
      const e = document.createElement(tag);
      if (cls) e.className = cls;
      if (css) e.style.cssText = css;
      if (html !== undefined) e.innerHTML = html;
      return e;
    },
    tornEdge(seed, steps, depth) { const r = U.rng(seed), o = []; for (let i = 0; i <= steps; i++) o.push((i % 3 === 0 ? r() : r() * .45) * depth); return o; },
    tornBox(seed) {
      const n = 26, top = U.tornEdge(seed, n, 9), bot = U.tornEdge(seed + 5, n, 9), p = [];
      top.forEach((d, i) => p.push(`${(i / n * 100).toFixed(2)}% ${d.toFixed(2)}%`));
      bot.reverse().forEach((d, i) => p.push(`${(100 - i / n * 100).toFixed(2)}% ${(100 - d).toFixed(2)}%`));
      return `polygon(${p.join(',')})`;
    },
    grain(alpha = .34, rgb = '.32 .24 .14') {
      const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='320' height='320'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.75' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 ${rgb.split(' ')[0]} 0 0 0 0 ${rgb.split(' ')[1]} 0 0 0 0 ${rgb.split(' ')[2]} 0 0 0 ${alpha} 0'/></filter><rect width='320' height='320' filter='url(#n)'/></svg>`;
      return `url("data:image/svg+xml,${encodeURIComponent(svg)}")`;
    },
    latest(list, t) { let v = list[0]; for (const x of list) if (x.t <= t + 1e-6) v = x; return v; },
  };

  window.VE = {U};

  let C, S, root, items, decor, api, frameHost;

  function geometry() {
    const W = C.format.w, H = C.format.h;
    const win = C.video_window || {y: 0, h: H};
    const vertical = H > W, framed = win.h < H - 1;
    return {W, H, win, vertical, framed};
  }

  /* Default positions per kind, so a timeline can omit x and y. */
  function defaults(kind) {
    const {W, H, win, framed} = api.geo;
    const topBar = framed ? win.y : 0;
    const impactY = framed ? topBar * .6 : H * .3;
    const d = {
      impact: {x: W / 2, y: impactY},
      score: {x: W / 2, y: impactY},
      stamp: {x: W / 2, y: framed ? topBar * .7 : H * .32},
      speech: {x: W / 2, y: framed ? win.y + win.h + 75 : H * .86},
      voice: {x: W / 2, y: framed ? win.y + win.h + 75 : H * .86},
      comment: framed ? {x: W / 2, y: win.y - 80} : {x: W * .96, y: H * .7, ax: 1},
      label: {x: framed ? 56 : 60, y: framed ? 165 : 70, ax: 0},
      tag: {x: W / 2, y: framed ? win.y + win.h - 60 : H * .72},
    };
    return Object.assign({ax: .5}, d[kind] || {x: W / 2, y: H / 2});
  }

  function addItem(el, cue, o) {
    root.appendChild(el);
    const it = {
      el, cue, start: o.start ?? cue.t, end: o.end ?? cue.end, x: o.x, y: o.y, ax: o.ax ?? .5, ay: o.ay ?? .5,
      tilt: o.tilt ?? 0, seed: o.seed ?? 1, fit: o.fit ?? 1, anim: o.anim || 'default', flip: o.flip ? -1 : 1,
      w: el.offsetWidth, h: el.offsetHeight, update: o.update, kind: o.kind || cue.type, text: o.text,
    };
    el.style.transformOrigin = `${it.w / 2}px ${it.h / 2}px`;
    items.push(it);
    return it;
  }

  const DEFAULT_ANIM = (e) => ({s: e < .2 ? U.ease.outBack(e / .2) : 1});

  function standardUpdate(it, tt) {
    const e = tt - it.start, rem = it.end - tt, on = e >= 0 && rem > 0;
    it.el.style.display = on ? '' : 'none';
    if (!on) return;
    const fn = (S.anim && (S.anim[it.anim] || S.anim.default)) || DEFAULT_ANIM;
    const st = Object.assign({s: 1, sx: 1, sy: 1, o: 1, dx: 0, dy: 0, r: 0, blur: 0}, fn(e, rem, it));
    let br = 0, bx = 0, by = 0;
    if (S.boil) {
      const b = Math.floor(tt * S.boil.fps + 1e-6);
      br = (U.hash(b + it.seed) - .5) * S.boil.rot;
      bx = (U.hash(b + it.seed + 3) - .5) * S.boil.px;
      by = (U.hash(b + it.seed + 7) - .5) * S.boil.px;
    }
    const s = st.s * it.fit;
    it.el.style.transform = `translate(${it.x - it.w * it.ax + st.dx + bx}px,${it.y - it.h * it.ay + st.dy + by}px) ` +
      `rotate(${it.tilt + st.r + br}deg) scale(${s * st.sx * it.flip},${s * st.sy})`;
    it.el.style.opacity = st.o;
    it.el.style.filter = st.blur > .05 ? `blur(${st.blur}px)` : '';
    it.el.style.clipPath = st.clip ? `inset(0 ${st.clip}% 0 0)` : '';
  }

  /* Vertical framed layouts keep text clear of the app's right-hand buttons (x > 960). */
  function textWidth() {
    const {W, vertical, framed} = api.geo;
    return vertical && framed ? 840 : W * .9;
  }

  function fitScale(el, maxW) {
    root.appendChild(el);
    const f = Math.min(1, maxW / Math.max(el.offsetWidth, 1));
    root.removeChild(el);
    return f;
  }

  const BUILD = {
    text(cue, seed) {
      const el = S.text(cue.type, cue.text, seed, cue, api);
      const pos = Object.assign(defaults(cue.type), pick(cue));
      const fit = fitScale(el, S.maxWidth?.(api.geo) ?? textWidth());
      addItem(el, cue, {...pos, seed, fit, tilt: cue.tilt ?? S.tilt?.[cue.type] ?? 0, anim: cue.type, text: cue.text});
    },
    impact(cue, seed) {
      const pos = Object.assign(defaults('impact'), pick(cue));
      const els = cue.words.map((w, k) => { const e = S.word(w, k, seed, cue, api); root.appendChild(e); return e; });
      const gap = S.wordGap ?? 18;
      const total = els.reduce((a, e) => a + e.offsetWidth, 0) + gap * (els.length - 1);
      const fit = Math.min(1, (S.maxWidth?.(api.geo) ?? api.geo.W * .9) / total);
      let x = pos.x - total * fit / 2;
      els.forEach((e, k) => {
        const w = e.offsetWidth * fit;
        root.removeChild(e);
        addItem(e, cue, {start: cue.t + k * (cue.stagger ?? .22), x: x + w / 2, y: pos.y, seed: seed + k * 3, fit,
          tilt: S.wordTilt ? S.wordTilt(k) : 0, anim: 'impact', kind: 'impact', text: cue.words[k]});
        x += w + gap * fit;
      });
      S.decorate?.impact?.(api, cue, pos, seed, els);
    },
    stamp(cue, seed) {
      const el = S.stamp(cue.text, cue, api);
      const pos = Object.assign(defaults('stamp'), pick(cue));
      addItem(el, cue, {...pos, seed, tilt: cue.tilt ?? S.tilt?.stamp ?? -9, anim: 'stamp', text: cue.text});
    },
    sticker(cue, seed) {
      const el = U.node('img', 'ob', `width:${cue.w}px;${S.stickerCss || ''}`);
      el.src = cue.src;
      addItem(el, cue, {x: cue.x, y: cue.y, seed, tilt: cue.tilt ?? 0, flip: cue.flip, anim: 'sticker'});
    },
    march(cue, seed) {
      for (let i = 0; i < (cue.count || 4); i++) {
        const el = U.node('img', 'ob', `width:${cue.w}px;${S.stickerCss || ''}`);
        el.src = cue.src;
        addItem(el, cue, {x: 0, y: cue.y, seed: seed + i, flip: cue.flip, update(it, tt) {
          const on = tt >= cue.t && tt < cue.end;
          it.el.style.display = on ? '' : 'none';
          if (!on) return;
          const p = (tt - cue.t) / Math.max(cue.end - cue.t, .01);
          const step = Math.floor(tt * 8 + i);
          const x = cue.from + (cue.to - cue.from) * p + i * (cue.spacing ?? 150);
          it.el.style.transform = `translate(${x - it.w / 2}px,${cue.y - it.h / 2 + (step % 2 ? -7 : 0)}px) rotate(${step % 2 ? -4 : 3}deg) scale(${it.flip},1)`;
        }});
      }
    },
    arrow(cue) {
      const {W, H} = api.geo, [x1, y1] = cue.from, [x2, y2] = cue.to;
      const mx = (x1 + x2) / 2 + (y2 - y1) * .25, my = (y1 + y2) / 2 - (x2 - x1) * .25;
      const ang = Math.atan2(y2 - my, x2 - mx), L = 34;
      const head = `M${x2 - L * Math.cos(ang - .5)},${y2 - L * Math.sin(ang - .5)} L${x2},${y2} L${x2 - L * Math.cos(ang + .5)},${y2 - L * Math.sin(ang + .5)}`;
      const ink = cue.color || S.ink || '#2b2a28';
      const el = U.node('div', 'ob', `width:${W}px;height:${H}px`,
        `<svg width="${W}" height="${H}" fill="none" stroke="${ink}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"><path class="body" d="M${x1},${y1} Q${mx},${my} ${x2},${y2}"/><path class="head" d="${head}"/></svg>`);
      root.appendChild(el);
      const body = el.querySelector('.body'), headEl = el.querySelector('.head'), len = body.getTotalLength();
      body.style.strokeDasharray = len;
      items.push({el, cue, update(it, tt) {
        const on = tt >= cue.t && tt < cue.end;
        el.style.display = on ? '' : 'none';
        if (!on) return;
        const p = U.clamp((tt - cue.t) / .5, 0, 1);
        body.style.strokeDashoffset = len * (1 - p);
        headEl.style.display = p >= 1 ? '' : 'none';
      }});
    },
    ring(cue) {
      const {W, H} = api.geo, cx = cue.x, cy = cue.y, rx = cue.rx ?? 120, ry = cue.ry ?? 90;
      const ink = cue.color || S.accent || '#ff7a1a';
      const el = U.node('div', 'ob', `width:${W}px;height:${H}px`,
        `<svg width="${W}" height="${H}" fill="none"><path stroke="${ink}" stroke-width="8" stroke-linecap="round" d="M${cx - rx},${cy - ry * .15} C${cx - rx * 1.05},${cy - ry * 1.2} ${cx + rx * 1.1},${cy - ry * 1.25} ${cx + rx},${cy} C${cx + rx * 1.02},${cy + ry * 1.2} ${cx - rx * 1.15},${cy + ry * 1.15} ${cx - rx * 1.03},${cy - ry * .3}"/></svg>`);
      root.appendChild(el);
      const path = el.querySelector('path'), len = path.getTotalLength();
      path.style.strokeDasharray = len;
      items.push({el, cue, update(it, tt) {
        const on = tt >= cue.t && tt < cue.end;
        el.style.display = on ? '' : 'none';
        if (on) path.style.strokeDashoffset = len * (1 - U.clamp((tt - cue.t) / .6, 0, 1));
      }});
    },
    transition(cue, seed) {
      const make = (S.transitions && (S.transitions[cue.variant] || S.transitions.default)) || defaultTransition;
      make(api, cue, seed);
    },
  };
  BUILD.tear = (cue, seed) => BUILD.transition({...cue, variant: 'tear'}, seed);

  function defaultTransition(a, cue) {
    const {W, H} = a.geo;
    const el = U.node('div', 'ob', `width:${W}px;height:${H}px;background:${cue.color || '#fff'}`);
    a.root.appendChild(el);
    a.items.push({el, cue, update(it, tt) {
      const on = tt >= cue.t && tt < cue.end;
      el.style.display = on ? '' : 'none';
      if (!on) return;
      const p = (tt - cue.t) / (cue.end - cue.t);
      el.style.opacity = p < .5 ? p * 2 : (1 - p) * 2;
    }});
  }

  function pick(cue) {
    const o = {};
    for (const k of ['x', 'y', 'ax']) if (cue[k] !== undefined) o[k] = cue[k];
    return o;
  }

  async function loadFonts() {
    const css = (C.fonts || []).map(f =>
      `@font-face{font-family:'${f.family}';font-weight:${f.weight};src:url('${C.fonts_uri}/${f.file}')}`).join('');
    document.head.appendChild(U.node('style', '', '', css));
    await Promise.all((C.fonts || []).map(f => document.fonts.load(`${String(f.weight).split(' ')[0]} 40px '${f.family}'`, 'ไทย').catch(() => {})));
  }

  window.init = async (comp, host) => {
    C = comp;
    S = STYLES[comp.style || 'scrapbook'];
    if (!S) throw new Error(`unknown style: ${comp.style}`);
    items = []; decor = [];
    if (!document.getElementById('engine-css')) {
      const st = U.node('style', '', '', '.ob{position:absolute;left:0;top:0}.hl{color:var(--hl)}');
      st.id = 'engine-css'; document.head.appendChild(st);
    }
    root = host || document.getElementById('root');
    root.innerHTML = '';
    root.className = `style-${S.name}`;
    root.style.position = 'relative'; root.style.overflow = 'hidden';
    root.style.width = C.format.w + 'px'; root.style.height = C.format.h + 'px';
    if (comp.font) root.style.setProperty('--display', `'${comp.font}'`); else root.style.removeProperty('--display');
    /* The chosen option's own weight, for styles whose options differ in weight (the option is the last face of its family). */
    const face = comp.font && (comp.fonts || []).filter(f => f.family === comp.font).pop();
    if (face) root.style.setProperty('--display-weight', String(face.weight).split(' ').pop()); else root.style.removeProperty('--display-weight');
    root.style.setProperty('--hl', S.highlight || S.accent || '#ffd400');
    await loadFonts();
    api = {C, S, U, root, items, decor, geo: geometry(), addItem, defaults};
    if (S.css && !document.getElementById(`css-${S.name}`)) {
      const st = U.node('style', '', '', S.css); st.id = `css-${S.name}`; document.head.appendChild(st);
    }
    /* The style's bars live in their own layer so full-frame shots (comp.fills) can hide them. */
    frameHost = U.node('div', 'ob', `width:${C.format.w}px;height:${C.format.h}px`);
    root.appendChild(frameHost);
    api.root = frameHost;
    S.frame?.(api);
    api.root = root;
    (C.cues || []).forEach((cue, i) => {
      const seed = (i + 1) * 101;
      if (S.build?.[cue.type]) S.build[cue.type](api, cue, seed);
      else if (TEXT_KINDS.includes(cue.type)) BUILD.text(cue, seed);
      else if (BUILD[cue.type]) BUILD[cue.type](cue, seed);
      else console.warn(`style ${S.name} has no builder for ${cue.type}`);
    });
    await Promise.all([...root.querySelectorAll('img')].map(img => img.decode().catch(() => {})));
    for (const it of items) {
      if (!it.w && it.el.offsetWidth) {
        it.w = it.el.offsetWidth; it.h = it.el.offsetHeight;
        it.el.style.transformOrigin = `${it.w / 2}px ${it.h / 2}px`;
      }
    }
    window.seek(0);
  };

  window.seek = (t) => {
    const tt = S.holdFps ? Math.floor(t * S.holdFps + 1e-6) / S.holdFps : t;
    frameHost.style.display = (C.fills || []).some(f => t >= f.t - 1e-6 && t < f.end - 1e-6) ? 'none' : '';
    for (const d of decor) d(tt);
    for (const it of items) (it.update || standardUpdate)(it, tt);
  };

  /* Approximate box of every readable item, used by QA to check safe zones. */
  window.layout = () => items.filter(it => it.text).map(it => {
    const w = it.w * it.fit, h = it.h * it.fit;
    return {kind: it.kind, text: it.text, t: it.start, end: it.end, fit: it.fit,
            box: [it.x - w * it.ax, it.y - h * it.ay, it.x - w * it.ax + w, it.y - h * it.ay + h]};
  });
})();
