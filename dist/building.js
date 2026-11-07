import {refreshCompact} from './compact.js';
document.getElementById('skyEvidence').onclick=()=>{location.hash='evidence';[...document.querySelectorAll('#evidence .compact-tabs button')].find(b=>b.textContent==='Space')?.click();};
function showRoomCheck(){document.querySelectorAll('.model-evidence-table tbody tr').forEach((row,i)=>row.hidden=i!==Number(document.getElementById('roomCheck').value));refreshCompact();}
document.getElementById('roomCheck').onchange=showRoomCheck;showRoomCheck();
