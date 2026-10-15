
(() => {
  'use strict';
  const slides=Array.from(document.querySelectorAll('.slide'));
  const titles=slides.map(slide=>slide.dataset.title);
  const prev=document.getElementById('prev');
  const next=document.getElementById('next');
  const counter=document.getElementById('counter');
  const label=document.getElementById('slide-label');
  const live=document.getElementById('live-status');
  const outline=document.getElementById('outline');
  const outlineButton=document.getElementById('outline-button');
  let current=0;
  let touchStart=null;

  // Dimensioni del palco
  function fit(){
    if(document.documentElement.classList.contains("render-view"))return;
    const viewport=document.getElementById('viewport');
    const scale=Math.min((viewport.clientWidth-24)/1600,(viewport.clientHeight-20)/900);
    document.documentElement.style.setProperty('--slide-scale',String(Math.max(.05,scale)));
  }
  // Navigazione per hash e cambio slide
  function hashIndex(){
    const match=location.hash.match(/^#slide-(\d+)$/);
    return match ? Math.min(slides.length-1,Math.max(0,Number(match[1])-1)) : 0;
  }
  function show(index,updateHash=true){
    const oldSlide=slides[current];
    const focusWasInSlide=oldSlide && oldSlide.contains(document.activeElement);
    current=Math.min(slides.length-1,Math.max(0,index));
    slides.forEach((slide,i)=>{
      slide.hidden=i!==current;
      slide.classList.toggle('active',i===current);
      slide.setAttribute('aria-hidden',String(i!==current));
    });
    prev.disabled=current===0;
    next.disabled=current===slides.length-1;
    counter.textContent=String(current+1).padStart(2,'0')+' / '+String(slides.length).padStart(2,'0');
    label.textContent=titles[current];
    live.textContent='Slide '+(current+1)+' di '+slides.length+'. '+titles[current];
    document.querySelectorAll('[data-go]').forEach((button,i)=>{
      if(i===current)button.setAttribute('aria-current','step');
      else button.removeAttribute('aria-current');
    });
    if(focusWasInSlide && oldSlide!==slides[current])next.focus({preventScroll:true});
    document.dispatchEvent(new CustomEvent("thesis:slidechange",{detail:{index:current}}));
    if(updateHash){
      try{history.replaceState(null,'','#slide-'+(current+1));}
      catch(_){location.hash='slide-'+(current+1);}
    }
  }
  // Un solo percorso coordina passi, tastiera, pulsanti e swipe.
  function navigate(direction){
    if(window.ThesisSteps && window.ThesisSteps.navigate(direction,slides[current]))return;
    show(current+direction);
  }
  window.ThesisDeck={show,next:()=>navigate(1),previous:()=>navigate(-1),get current(){return current;}};
  // Modalità di resa: stessa pagina e stessi SVG a dimensione esatta.
  const renderWidth=Number(new URLSearchParams(location.search).get('render'));
  if([1600,1280].includes(renderWidth)){
    document.documentElement.classList.add('render-view');
    document.documentElement.style.setProperty('--render-width',renderWidth+'px');
    document.documentElement.style.setProperty('--render-height',renderWidth*9/16+'px');
    document.documentElement.style.setProperty('--render-scale',String(renderWidth/1600));
  }
  // Indice e schermo intero
  function closeOutline(){outline.close();outlineButton.focus();}
  function openOutline(){
    if(outline.open){closeOutline();return;}
    outline.showModal();
    const active=outline.querySelector('[aria-current="step"]');
    if(active)active.focus();
  }
  async function fullscreen(){
    if(!document.fullscreenElement){
      if(document.documentElement.requestFullscreen){
        try{await document.documentElement.requestFullscreen();}catch(_){live.textContent='Usa F11 per la modalità schermo intero.';}
      }else live.textContent='Usa F11 per la modalità schermo intero.';
    }else if(document.exitFullscreen){await document.exitFullscreen();}
  }
  // Mouse, tastiera e touch
  prev.addEventListener('click',()=>navigate(-1));
  next.addEventListener('click',()=>navigate(1));
  outlineButton.addEventListener('click',openOutline);
  document.getElementById('close-outline').addEventListener('click',closeOutline);
  document.getElementById('fullscreen').addEventListener('click',fullscreen);
  document.getElementById('print').addEventListener('click',()=>window.print());
  document.querySelectorAll('[data-go]').forEach(button=>button.addEventListener('click',()=>{show(Number(button.dataset.go));closeOutline();}));
  document.addEventListener('keydown',event=>{
    if(event.defaultPrevented)return;
    if(event.repeat && ['ArrowRight','ArrowLeft','PageDown','PageUp',' '].includes(event.key)){event.preventDefault();return;}
    if(event.altKey||event.ctrlKey||event.metaKey||event.target.closest('input,textarea,select,[contenteditable="true"]'))return;
    if(outline.open||document.getElementById('speaker-notes').open||document.getElementById('resstar-rule-dialog').open||document.getElementById('amf-rule-dialog').open)return;
    if(['ArrowRight','PageDown',' '].includes(event.key)){event.preventDefault();navigate(1);}
    else if(['ArrowLeft','PageUp'].includes(event.key)){event.preventDefault();navigate(-1);}
    else if(event.key==='Home'){event.preventDefault();show(0);}
    else if(event.key==='End'){event.preventDefault();show(slides.length-1);}
    else if(event.key.toLowerCase()==='f'){event.preventDefault();fullscreen();}
    else if(event.key.toLowerCase()==='i'){event.preventDefault();openOutline();}
    else if(event.key.toLowerCase()==='n'){event.preventDefault();openNotes();}
    else if(event.key.toLowerCase()==='p'){event.preventDefault();window.print();}
  });
  const viewport=document.getElementById('viewport');
  viewport.addEventListener('touchstart',event=>{
    if(event.touches.length===1)touchStart={x:event.touches[0].clientX,y:event.touches[0].clientY};
  },{passive:true});
  viewport.addEventListener('touchend',event=>{
    if(!touchStart||event.changedTouches.length!==1)return;
    const dx=event.changedTouches[0].clientX-touchStart.x;
    const dy=event.changedTouches[0].clientY-touchStart.y;
    if(Math.abs(dx)>60&&Math.abs(dx)>Math.abs(dy)*1.5)navigate(dx<0?1:-1);
    touchStart=null;
  },{passive:true});
  window.addEventListener('resize',fit);
  document.addEventListener('fullscreenchange',fit);
  window.addEventListener('hashchange',()=>show(hashIndex(),false));
  if(document.fonts)document.fonts.ready.then(fit);

  // Note del relatore
  const notesDialog=document.getElementById('speaker-notes');
  function openNotes(){
    document.getElementById('speaker-notes-title').textContent=String(current+1).padStart(2,'0')+' — '+titles[current];
    const seconds=Number(slides[current].dataset.seconds);
    document.getElementById('notes-duration').textContent='Budget indicativo: '+Math.floor(seconds/60)+':'+String(seconds%60).padStart(2,'0');
    document.getElementById('notes-body').textContent=slides[current].querySelector('.speaker-note').content.textContent;
    notesDialog.showModal();
  }
  document.getElementById('notes-button').addEventListener('click',openNotes);
  document.getElementById('close-notes').addEventListener('click',()=>{notesDialog.close();document.getElementById('notes-button').focus();});
  fit();show(hashIndex(),false);
})();

(() => {
 const dialog=document.getElementById('resstar-rule-dialog');
 const open=document.getElementById('open-resstar-rule');
 const close=document.getElementById('close-resstar-rule');
 open.addEventListener('click',()=>dialog.showModal());
 close.addEventListener('click',()=>{dialog.close();open.focus();});
})();

(() => {const d=document.getElementById('amf-rule-dialog'),o=document.getElementById('open-amf-rule');o.addEventListener('click',()=>d.showModal());document.getElementById('close-amf-rule').addEventListener('click',()=>{d.close();o.focus();});})();
