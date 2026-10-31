// AlgoMaster highlighter helpers. Paste into javascript_tool on a chapter page, in the user's signed-in Chrome.
//
//   await HL.check(list)            -> problems (MISS / OVERLAP / DUPTEXT) BEFORE applying; fix the list until []
//   await HL.apply(list.slice(0,5)) -> adds highlights. 5 per call at most: the browser tool times out at 45s.
//   await HL.missing(list)          -> indices not saved yet. THE source of truth; the page DOM is optimistic.
//   await HL.removeFromPanel(texts) -> deletes highlights by exact text (Notebook panel must be open on Highlights).
//
// list = [['P','exact sentence'], ['Y','another']]   colors: Y yellow, G green, B blue, P pink, R red
// Window state is lost on reload: after location.reload() paste this file again (or eval it from sessionStorage).
(() => {
  const RGB = {Y: '254, 240, 138', G: '187, 247, 208', B: '191, 219, 254', P: '251, 207, 232', R: '252, 165, 165'};
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const norm = x => x.replace(/[‘’]/g, "'").replace(/\s+/g, ' ').trim();

  // Chapter text lives in .payload-richtext. Build one string plus the offset of every text node in it.
  const index = () => {
    const root = document.querySelector('.payload-richtext');
    const nodes = [];
    const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = tw.nextNode())) nodes.push(n);
    let s = '';
    const map = nodes.map(x => { const st = s.length; s += x.data; return st; });
    return {root, nodes, map, s};
  };
  const find = (s, p) => {
    let q = p, i = s.indexOf(q);
    if (i < 0) { q = p.replace(/'/g, '’'); i = s.indexOf(q); }   // page may use curly apostrophes
    return {i, q};
  };

  // The course key in the API is the 3rd path segment, e.g. /learn/system-design/x -> system-design.
  // Verified for system-design only. For another course, check the Network tab for GET /api/v1/user/notebook?pageType=...
  const notebook = async () => {
    const pageType = location.pathname.split('/')[2];
    const j = await (await fetch('/api/v1/user/notebook?pageType=' + pageType)).json();
    return j.highlights.filter(h => h.link === location.pathname);
  };

  // Select a phrase and make the floating color toolbar appear. It only shows for the FULL mouse-event
  // sequence, and only on the second round, so callers select twice.
  const select = p => {
    const {root, nodes, map, s} = index();
    const {i, q} = find(s, p);
    if (i < 0) return false;
    const e = i + q.length;
    const a = map.findLastIndex(m => m <= i), b = map.findLastIndex(m => m < e);
    const r = document.createRange();
    r.setStart(nodes[a], i - map[a]);
    r.setEnd(nodes[b], e - map[b]);
    const el = nodes[a].parentElement;
    el.scrollIntoView({block: 'center'});
    const sel = getSelection();
    sel.removeAllRanges();
    sel.addRange(r);
    const bb = r.getBoundingClientRect();
    const fire = (t, tg) => tg.dispatchEvent(new MouseEvent(t, {bubbles: true, cancelable: true, composed: true, view: window,
      clientX: bb.x + bb.width / 2, clientY: bb.y + bb.height / 2, button: 0}));
    ['mousedown', 'mouseup', 'click', 'pointerup'].forEach(t => fire(t, el));
    ['mouseup', 'pointerup'].forEach(t => { fire(t, root); fire(t, document); });
    document.dispatchEvent(new Event('selectionchange'));
    return true;
  };

  const apply = async (list, gap = 3000) => {
    const out = [];
    for (const [c, p] of list) {
      if (!select(p)) { out.push('MISS'); continue; }
      await sleep(200); select(p); await sleep(500);
      const btn = [...document.querySelectorAll('button')].find(b => {
        const w = b.getBoundingClientRect().width;
        return w > 8 && w < 30 && getComputedStyle(b).backgroundColor.includes(RGB[c]);
      });
      if (!btn) { out.push('NOBTN'); continue; }   // text already highlighted, or the toolbar did not show
      ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(t =>
        btn.dispatchEvent(new MouseEvent(t, {bubbles: true, cancelable: true, view: window})));
      await sleep(gap);                              // faster than ~1 per 2s gets HTTP 503 and the save is silently lost
      getSelection().removeAllRanges();
      out.push(c);
    }
    return out;
  };

  const missing = async list => {
    const have = new Set((await notebook()).map(h => norm(h.text)));
    return list.map((l, i) => [i, l]).filter(([, l]) => !have.has(norm(l[1]))).map(([i]) => i);
  };

  const check = async (list, replacing = []) => {
    const {s} = index();
    const gone = new Set(replacing.map(norm));
    const spans = (await notebook()).filter(h => !gone.has(norm(h.text))).map(h => {
      const i = find(s, h.text.replace(/\s+/g, ' ')).i;
      return [i, i + h.text.length];
    });
    return list.map(([, p]) => {
      const {i, q} = find(s, p);
      if (i < 0) return 'MISS: ' + p.slice(0, 50);
      if (spans.some(([a, b]) => a >= 0 && a < i + q.length && b > i)) return 'OVERLAP: ' + p.slice(0, 50);
      if (s.indexOf(q, i + 1) >= 0) return 'DUPTEXT (first match wins): ' + p.slice(0, 50);
      return null;
    }).filter(Boolean);
  };

  const removeFromPanel = async texts => {
    const inp = document.querySelector('input[placeholder*="Search highlights"]');
    let p = inp, sc = null;
    while (p && !sc) { p = p.parentElement; sc = [...p.querySelectorAll('div')].find(d => /overflow-y-auto/.test(d.className) && d.scrollHeight > d.clientHeight); }
    const out = [];
    for (const t of texts) {
      const card = [...sc.querySelectorAll('div.rounded-md.border')].find(c =>
        norm([...c.querySelectorAll('p span')].map(s => s.textContent).join(' ')) === norm(t));
      if (!card) { out.push('nocard'); continue; }
      card.querySelector('button[aria-label="Delete highlight"]').click();
      out.push('deleted');
      await sleep(2500);
    }
    return out;   // the page still shows deleted highlights until you reload it
  };

  window.HL = {index, select, apply, missing, check, notebook, removeFromPanel};
})();
