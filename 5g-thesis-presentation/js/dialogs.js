/* Apertura e chiusura dei contenuti integrali: tutto funziona anche offline. */
(() => {
 const dialogs=[
  {dialog:'report-json-dialog',open:'open-report-json',close:'close-report-json'}
 ];
 dialogs.forEach(item=>{
  const dialog=document.getElementById(item.dialog),open=document.getElementById(item.open),close=document.getElementById(item.close);
  if(!dialog||!open||!close)return;
  open.addEventListener('click',()=>dialog.showModal());
  close.addEventListener('click',()=>{dialog.close();open.focus();});
 });
})();
