
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

  function fit(){
    const viewport=document.getElementById('viewport');
    const scale=Math.min((viewport.clientWidth-24)/1600,(viewport.clientHeight-20)/900);
    document.documentElement.style.setProperty('--slide-scale',String(Math.max(.05,scale)));
  }
  function hashIndex(){
    const match=location.hash.match(/^#slide-(\d+)$/);
    return match ? Math.min(slides.length-1,Math.max(0,Number(match[1])-1)) : 0;
  }
  function show(index,updateHash=true){
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
    if(updateHash){
      try{history.replaceState(null,'','#slide-'+(current+1));}
      catch(_){location.hash='slide-'+(current+1);}
    }
  }
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
  prev.addEventListener('click',()=>show(current-1));
  next.addEventListener('click',()=>show(current+1));
  outlineButton.addEventListener('click',openOutline);
  document.getElementById('close-outline').addEventListener('click',closeOutline);
  document.getElementById('fullscreen').addEventListener('click',fullscreen);
  document.getElementById('print').addEventListener('click',()=>window.print());
  document.querySelectorAll('[data-go]').forEach(button=>button.addEventListener('click',()=>{show(Number(button.dataset.go));closeOutline();}));
  document.addEventListener('keydown',event=>{
    if(event.altKey||event.ctrlKey||event.metaKey||event.target.closest('input,textarea,select,[contenteditable="true"]'))return;
    if(outline.open)return;
    if(['ArrowRight','PageDown',' '].includes(event.key)){event.preventDefault();show(current+1);}
    else if(['ArrowLeft','PageUp'].includes(event.key)){event.preventDefault();show(current-1);}
    else if(event.key==='Home'){event.preventDefault();show(0);}
    else if(event.key==='End'){event.preventDefault();show(slides.length-1);}
    else if(event.key.toLowerCase()==='f'){event.preventDefault();fullscreen();}
    else if(event.key.toLowerCase()==='i'){event.preventDefault();openOutline();}
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
    if(Math.abs(dx)>60&&Math.abs(dx)>Math.abs(dy)*1.5)show(current+(dx<0?1:-1));
    touchStart=null;
  },{passive:true});
  window.addEventListener('resize',fit);
  document.addEventListener('fullscreenchange',fit);
  window.addEventListener('hashchange',()=>show(hashIndex(),false));
  if(document.fonts)document.fonts.ready.then(fit);
  fit();show(hashIndex(),false);
})();
