const slides=[...document.querySelectorAll('.slide')];
const current=document.getElementById('current');
const total=document.getElementById('total');
const dots=document.getElementById('dots');
let index=0;
total.textContent=slides.length;
slides.forEach((_,i)=>{const d=document.createElement('i');d.addEventListener('click',()=>show(i));dots.appendChild(d)});
function show(i){index=(i+slides.length)%slides.length;slides.forEach((s,n)=>s.classList.toggle('active',n===index));[...dots.children].forEach((d,n)=>d.classList.toggle('active',n===index));current.textContent=index+1;document.title=`${index+1}/${slides.length} · ${slides[index].dataset.title}`}
function next(){show(index+1)}function prev(){show(index-1)}
document.getElementById('next').addEventListener('click',next);document.getElementById('prev').addEventListener('click',prev);
document.addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();next()}if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();prev()}if(e.key==='Home')show(0);if(e.key==='End')show(slides.length-1);if(e.key.toLowerCase()==='f'&&document.fullscreenEnabled){document.documentElement.requestFullscreen?.()}});
let startX=null;document.addEventListener('touchstart',e=>startX=e.touches[0].clientX,{passive:true});document.addEventListener('touchend',e=>{if(startX===null)return;const dx=e.changedTouches[0].clientX-startX;if(Math.abs(dx)>50)(dx<0?next:prev)();startX=null},{passive:true});
show(0);