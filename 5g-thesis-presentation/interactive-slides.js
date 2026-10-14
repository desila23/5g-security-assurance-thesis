/*
 * SLIDE 10 E 11 — spiegazione controllata dal relatore.
 * 01: testi e ordine dei passaggi. 02: stato. 03: SVG. 04: pulsanti e tastiera.
 * Nessun timer: ogni cambiamento richiede un comando esplicito.
 */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else {
    root.ThesisSteps = api;
    api.mount(document, window);
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  // TESTI MODIFICABILI: pulsanti e messaggio della vista completa.
  // Per le sole scritte cambia i valori, lasciando invariati i nomi a sinistra.
  const uiText = {
    start: 'Spiega per passi',
    full: 'Vista completa',
    previous: 'Indietro',
    next: 'Avanti',
    reset: 'Ricomincia',
    fullStatus: 'Vista completa · attiva i passaggi per spiegare la slide.'
  };

  // TESTI PASSI SLIDE 10: modifica solo label per cambiare la spiegazione.
  // visible e current controllano il disegno; GUIDA_TESTI.md elenca tutte le righe.
  const constructionSteps = [
    { label: 'La regola descrive A, B facoltativo e C.', visible: [] },
    { label: 'event.a AS a → Atom(event.a).', visible: ['atom-a'], current: 'a' },
    { label: 'event.b AS b → Atom(event.b).', visible: ['atom-a', 'atom-b'], current: 'b' },
    { label: 'event.c AS c → Atom(event.c).', visible: ['atom-a', 'atom-b', 'atom-c'], current: 'c' },
    { label: 'Dispongo i tre atomi nell’NFA; q5 diventa finale.', visible: ['atom-a', 'atom-b', 'atom-c', 'nfa'] },
    { label: 'Aggiungo ε tra A e B e tra B e C.', visible: ['atom-a', 'atom-b', 'atom-c', 'nfa', 'eps-links'] },
    { label: 'Aggiungo ε che salta B: è il gruppo OPTIONAL.', visible: ['atom-a', 'atom-b', 'atom-c', 'nfa', 'eps-links', 'eps-skip'] },
    { label: 'L’automa accetta A → B → C oppure A → C.', visible: ['atom-a', 'atom-b', 'atom-c', 'nfa', 'eps-links', 'eps-skip', 'paths'] }
  ];
  // TESTI PASSI SLIDE 11: anche qui la spiegazione è nel campo label.
  const matcherSteps = [
    { label: 'La regola attende un evento A.', bindings: [], atoms: [], cursor: -1, current: 'a' },
    { label: 'Riconosco A(1): creo a(1) e accendo Atom A.', bindings: [0], atoms: ['a'], cursor: 0, current: 'a' },
    { label: 'X(2) non contribuisce al match: continuo a cercare.', bindings: [0], atoms: ['a'], cursor: 1 },
    { label: 'Qui A(3) non è consumabile: chiudo il primo candidato e spengo Atom A.', bindings: [], atoms: [], cursor: 2, restart: true, current: 'a' },
    { label: 'Riconosco A(3): creo a(3) e riaccendo Atom A.', bindings: [2], atoms: ['a'], cursor: 2, restarted: true, current: 'a' },
    { label: 'Riconosco B(4): creo b(4) e accendo Atom B.', bindings: [2, 3], atoms: ['a', 'b'], cursor: 3, restarted: true, current: 'b' },
    { label: 'Ignoro X(5); il candidato continua da A(3), B(4).', bindings: [2, 3], atoms: ['a', 'b'], cursor: 4, restarted: true },
    { label: 'Riconosco C(6): creo c(6). Match A(3), B(4), C(6).', bindings: [2, 3, 5], atoms: ['a', 'b', 'c'], cursor: 5, restarted: true, current: 'c' }
  ];
  const steps = { construction: constructionSteps, matcher: matcherSteps };

  // 02. STATO — conserva il passo durante la navigazione tra slide.
  function initialState(kind) {
    if (!steps[kind]) throw new Error('Tipo di slide sconosciuto: ' + kind);
    return { kind, manual: false, index: 0 };
  }
  function transition(state, action) {
    const last = steps[state.kind].length - 1;
    switch (action) {
      case 'toggle': return { ...state, manual: !state.manual, index: 0 };
      case 'next': return state.manual ? { ...state, index: Math.min(last, state.index + 1) } : state;
      case 'previous': return state.manual ? { ...state, index: Math.max(0, state.index - 1) } : state;
      case 'reset': return { ...state, manual: true, index: 0 };
      case 'full': return { ...state, manual: false };
      default: throw new Error('Comando sconosciuto: ' + action);
    }
  }
  function view(state, printing = false) {
    const full = printing || !state.manual;
    const index = full ? steps[state.kind].length - 1 : state.index;
    const step = steps[state.kind][index];
    const result = { ...step, index, full, total: steps[state.kind].length };
    if (state.kind === 'matcher') {
      result.events = ['A', 'X', 'A', 'B', 'X', 'C'].map((_, i) => {
        if (step.bindings.includes(i)) return 'selected';
        if (i === 0 && (step.restart || step.restarted)) return full ? 'neutral' : 'discarded';
        if (i === 2 && step.restart) return 'restart';
        if (i === step.cursor) return 'skipped';
        if (i <= step.cursor) return 'neutral';
        return 'pending';
      });
    }
    return result;
  }

  // 03. DISEGNI SVG — gli ID corrispondono ai gruppi in index.html.
  function show(element, visible) {
    if (!element) return;
    element.style.opacity = visible ? '1' : '0';
    element.style.visibility = visible ? 'visible' : 'hidden';
    element.setAttribute('aria-hidden', String(!visible));
  }
  function colourAtom(element, active, slideNumber) {
    const colour = active ? '#278766' : '#99a7bb';
    element.dataset.active = String(active);
    element.querySelectorAll('circle').forEach(circle => {
      circle.style.stroke = colour;
      if (circle.getAttribute('fill') !== 'none') circle.style.fill = active ? '#eef8f3' : '#f2f5f9';
    });
    element.querySelectorAll('text').forEach(text => { text.style.fill = colour; });
    element.querySelectorAll('path').forEach(path => {
      path.style.stroke = colour;
      if (path.hasAttribute('marker-end')) path.setAttribute('marker-end', 'url(#arrow-' + slideNumber + '-' + (active ? 'green' : 'gray') + ')');
    });
  }
  function paintSVG(section, current) {
    const get = id => section.querySelector('#' + id);
    const kind = section.dataset.stepKind;
    const slideNumber = Number(section.id.slice('slide-'.length));
    if (kind === 'construction') {
      ['atom-a', 'atom-b', 'atom-c', 'nfa', 'eps-links', 'eps-skip', 'paths'].forEach(id => {
        show(get('construction-' + id), current.visible.includes(id));
      });
      ['a', 'b', 'c'].forEach(letter => {
        show(get('construction-link-' + letter), current.visible.includes('atom-' + letter));
      });
    } else {
      current.events.forEach((status, i) => {
        const event = get('matcher-event-' + i);
        event.dataset.state = status;
        event.style.opacity = status === 'discarded' ? '.28' : status === 'pending' ? '.42' : '1';
        event.removeAttribute('opacity');
        const rect = event.querySelector('rect');
        const text = event.querySelector('text');
        rect.style.fill = status === 'selected' ? '#eef8f3' : status === 'restart' ? '#fff7e9' : '#f2f5f9';
        rect.style.stroke = status === 'selected' ? '#278766' : status === 'restart' ? '#9d7139' : '#d5dff0';
        text.style.fill = status === 'selected' ? '#278766' : status === 'restart' ? '#9d7139' : '#65758b';
      });
      [0, 2, 3, 5].forEach(i => show(get('matcher-binding-' + i), current.bindings.includes(i)));
      ['a', 'b', 'c'].forEach(letter => colourAtom(get('matcher-atom-' + letter), current.atoms.includes(letter), slideNumber));
      colourAtom(get('matcher-eps-ab'), current.atoms.includes('b'), slideNumber);
      colourAtom(get('matcher-eps-bc'), current.atoms.includes('c'), slideNumber);
    }
    ['a', 'b', 'c'].forEach(letter => {
      const line = get(kind + '-code-' + letter);
      line.dataset.current = String(!current.full && current.current === letter);
    });
  }

  // 04. CONTROLLI — solo click e tastiera, senza riproduzione automatica.
  function mount(doc, win) {
    const controllers = [];
    doc.querySelectorAll('[data-step-kind]').forEach(section => {
      let state = initialState(section.dataset.stepKind);
      let printing = false;
      const button = action => section.querySelector('[data-step-action="' + action + '"]');
      const status = section.querySelector('.step-status');
      function paint() {
        const current = view(state, printing);
        paintSVG(section, current);
        button('toggle').textContent = state.manual ? uiText.full : uiText.start;
        ['previous', 'next', 'reset'].forEach(action => { button(action).textContent = uiText[action]; });
        button('toggle').setAttribute('aria-pressed', String(state.manual));
        ['previous', 'next', 'reset'].forEach(action => { button(action).hidden = !state.manual; });
        button('previous').disabled = state.index === 0;
        button('next').disabled = state.index === current.total - 1;
        status.textContent = state.manual ? (state.index + 1) + '/' + current.total + ' · ' + current.label : uiText.fullStatus;
      }
      function dispatch(action) { state = transition(state, action); paint(); }
      section.querySelectorAll('[data-step-action]').forEach(control => {
        control.addEventListener('click', () => dispatch(control.dataset.stepAction));
      });
      controllers.push({ section, dispatch, isManual: () => state.manual,
        setPrinting(value) { printing = value; paint(); } });
      paint();
    });
    // Intercetta soltanto i tasti dei passi; Page Up/Down continuano a cambiare slide.
    doc.addEventListener('keydown', event => {
      if (event.altKey || event.ctrlKey || event.metaKey) return;
      if (event.target.closest('input,textarea,select,[contenteditable="true"]')) return;
      if (event.key === ' ' && event.target.closest('button')) return;
      if (Array.from(doc.querySelectorAll('dialog')).some(dialog => dialog.open)) return;
      const active = controllers.find(controller => !controller.section.hidden && controller.isManual());
      if (!active || !['ArrowRight', 'ArrowLeft', ' '].includes(event.key)) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      if (event.repeat) return;
      active.dispatch(event.key === 'ArrowLeft' ? 'previous' : 'next');
    }, true);
    win.addEventListener('beforeprint', () => controllers.forEach(controller => controller.setPrinting(true)));
    win.addEventListener('afterprint', () => controllers.forEach(controller => controller.setPrinting(false)));
    return controllers;
  }
  return { initialState, transition, view, mount, paintSVG };
});
