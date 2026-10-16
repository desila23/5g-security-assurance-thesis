/* Testi dei passi e durate. Per il layout modifica slides/*.html; per i colori css/presentation.css. */
(function(root){
  const uiText = {
    start: 'Spiega per passi',
    full: 'Vista completa',
    previous: 'Indietro',
    next: 'Avanti',
    reset: 'Ricomincia',
    fullStatus: 'Vista completa · Avanti apre la slide successiva.'
  };

  // TESTI PASSI SLIDE 10: modifica solo label per cambiare la spiegazione.
  // visible e current controllano il disegno; GUIDA_TESTI.md elenca gli ID e i testi.
  const constructionSteps = [
    { label: 'La regola richiede A, ammette B opzionale e termina con C.', visible: [] },
    { label: 'A diventa un frammento elementare dell’automa.', visible: ['atom-a'], current: 'a' },
    { label: 'Anche B viene rappresentato da un frammento elementare.', visible: ['atom-a', 'atom-b'], current: 'b' },
    { label: 'C completa i tre frammenti di partenza.', visible: ['atom-a', 'atom-b', 'atom-c'], current: 'c' },
    { label: 'Dispongo gli atomi nell’NFA, con q5 come stato finale.', visible: ['atom-a', 'atom-b', 'atom-c', 'nfa'] },
    { label: 'Le transizioni ε uniscono i frammenti senza consumare eventi.', visible: ['atom-a', 'atom-b', 'atom-c', 'nfa', 'eps-links'] },
    { label: 'Una transizione ε permette di saltare B (OPTIONAL).', visible: ['atom-a', 'atom-b', 'atom-c', 'nfa', 'eps-links', 'eps-skip'] },
    { label: 'L’NFA accetta A → B → C oppure A → C.', visible: ['atom-a', 'atom-b', 'atom-c', 'nfa', 'eps-links', 'eps-skip', 'paths'] }
  ];
  // TESTI PASSI SLIDE 11: anche qui la spiegazione è nel campo label.
  const matcherSteps = [
    { label: 'La regola attende A come primo evento.', bindings: [], atoms: [], cursor: -1, current: 'a' },
    { label: 'A(1) avvia un candidato ed è associato all’alias a.', bindings: [0], atoms: ['a'], cursor: 0, current: 'a' },
    { label: 'X(2) non soddisfa B: il candidato resta in attesa.', bindings: [0], atoms: ['a'], cursor: 1 },
    { label: 'A(3) non completa il primo candidato: lo chiudo.', bindings: [], atoms: [], cursor: 2, restart: true, current: 'a' },
    { label: 'Riavvio da A(3), associandolo all’alias a.', bindings: [2], atoms: ['a'], cursor: 2, restarted: true, current: 'a' },
    { label: 'B(4) viene riconosciuto e associato all’alias b.', bindings: [2, 3], atoms: ['a', 'b'], cursor: 3, restarted: true, current: 'b' },
    { label: 'X(5) è ignorato; il candidato rimane valido.', bindings: [2, 3], atoms: ['a', 'b'], cursor: 4, restarted: true },
    { label: 'C(6) completa il Match: A(3), B(4), C(6).', bindings: [2, 3, 5], atoms: ['a', 'b', 'c'], cursor: 5, restarted: true, current: 'c' }
  ];
  const rationaleSteps = [
    {label:'PRIMA · un verificatore diverso per ciascun test.',visible:['legacy']},
    {label:'DOPO · regole diverse, uno stesso motore.',visible:['pipeline']}
  ];
  const bindingSteps = [
    {label:'Il Match raccoglie gli eventi riconosciuti e i loro alias.',visible:['overview']},
    {label:'Nel BindingContext, ogni alias dà accesso al MessageEvent associato.',visible:['closeup']}
  ];

 const config={uiText,constructionSteps,matcherSteps,rationaleSteps,bindingSteps,
   rationaleCaptions:['Un verificatore per ogni test','Regole diverse, stesso motore di verifica'],
   motion:{rationale:560,bindingZoom:850,bindingStartMatrix:'matrix(0.403343,0,0,0.48,887.8256,262.8)'}
 };
 if(typeof module==='object'&&module.exports)module.exports=config;else root.DeckConfig=config;
})(typeof globalThis!=='undefined'?globalThis:this);
