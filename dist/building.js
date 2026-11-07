import {showLongText,refreshCompact} from './compact.js';
const $=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num=v=>typeof v==='number'?v.toLocaleString('en-GB',{maximumFractionDigits:3}):'Not recorded';
const colours={comercio:'#c4a66d',oficinas:'#b67b5e',vivienda:'#5a9787',nucleo:'#68726e'};
let model,levelIndex=10,mode='building',rotation=0,spaceIndex=-1;
function loops(polys){return (polys||[]).flatMap(p=>[p.o,...(p.h||[])])}
function transform(){const a=rotation*Math.PI/2;return ([x,y],z=0)=>{const xx=x*Math.cos(a)-y*Math.sin(a),yy=x*Math.sin(a)+y*Math.cos(a);return mode==='plan'?[xx,-yy]:[(xx-yy)*.85,(xx+yy)*.34-z]}}
function render(){if(!model)return;const l=model.levels[levelIndex],use=$('skyUse').value,explode=Number($('skyExplode').value),project=transform();let rawPoints=[];
 if(mode==='building'){for(const [i,f] of model.levels.entries())for(const ring of loops(f.plate.poly))for(const p of ring)rawPoints.push(project(p,f.elev+i*explode));}
 else rawPoints=loops(l.plate.poly).flatMap(r=>r.map(p=>project(p)));
 const xs=rawPoints.map(p=>p[0]),ys=rawPoints.map(p=>p[1]),minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys),scale=Math.min(320/(maxX-minX),340/(maxY-minY));
 const point=(p,z=0)=>{const [x,y]=project(p,z);return [240+(x-(minX+maxX)/2)*scale,200+(y-(minY+maxY)/2)*scale]};
 const path=(polys,z=0)=>loops(polys).map(r=>r.map((p,i)=>(i?'L':'M')+point(p,z).join(',')).join('')+'Z').join('');
 let svg='<defs><pattern id="skyGrid" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="#d7dfd3" stroke-width=".55"/></pattern></defs><rect width="480" height="420" fill="url(#skyGrid)"/>';
 if(mode==='building'){
  svg+='<text x="22" y="30" class="sky-svg-note">SOURCE POLYGONS / AXONOMETRIC</text>';
  for(const [i,f] of model.levels.entries()){
   const z=f.elev+i*explode,selected=i===levelIndex,related=use==='all'||use==='nucleo'||(f.depts||[]).includes(use),fill=colours[f.dept]||'#aaa';
   const label=`${f.en}; elevation ${num(f.elev)}; floor plate ${num(f.plate.area)} source area units`;
   svg+=`<g class="sky-floor ${selected?'selected':''}" data-level="${i}" role="button" tabindex="0" aria-label="${esc(label)}" aria-pressed="${selected}" opacity="${related?selected?1:.65:.12}"><title>${esc(label)}</title>`;
   for(const p of f.plate.poly){const ring=p.o;for(let k=0;k<ring.length;k++){const a=ring[k],b=ring[(k+1)%ring.length];svg+=`<polygon points="${[point(a,z-.14),point(b,z-.14),point(b,z),point(a,z)].map(p=>p.join(',')).join(' ')}" fill="${fill}" stroke="none"/>`}}
   svg+=`<path d="${path(f.plate.poly,z)}" fill="${fill}" fill-rule="evenodd" stroke="${selected?'#263b35':'#667a6d'}" stroke-width="${selected?2:.65}"/>`;
   if(f.core?.poly)svg+=`<path d="${path(f.core.poly,z+.03)}" fill="#68726e" fill-rule="evenodd" stroke="#465b50" stroke-width=".5" opacity=".85"/>`;
   if(selected){const [x,y]=point([10,0],z);svg+=`<path d="M${x+5} ${y}H425" stroke="#bb623d" stroke-width="1"/><text x="430" y="${y+4}" class="sky-svg-label">${esc(f.id)}</text>`}svg+='</g>';
  }
 }else{
  svg+='<text x="22" y="30" class="sky-svg-note">SOURCE POLYGONS / FLOOR PLAN</text>';
  svg+=`<path d="${path(l.plate.poly)}" fill="#e7e7dc" fill-rule="evenodd" stroke="#556e60" stroke-width="1.5"/>`;
  for(const z of l.zones||[])svg+=`<path d="${path(z.poly)}" fill="${colours[z.dept]||'#c0c6bb'}" fill-rule="evenodd" stroke="#fffefa" stroke-width="1" opacity="${(use==='all'||z.dept===use)?0.85:0.15}"><title>${esc(z.label)} · ${num(z.area)} source area units</title></path>`;
  if(l.core?.poly)svg+=`<path d="${path(l.core.poly)}" fill="#68726e" fill-rule="evenodd" stroke="#263b35" stroke-width="1" opacity="${(use==='all'||use==='nucleo')?0.9:0.35}"/>`;
  (l.rooms||[]).forEach((r,i)=>{if(!r.pos)return;const [x,y]=point([r.pos[0],r.pos[2]]);svg+=`<g class="sky-space" data-space="${i}" tabindex="0" role="button" aria-label="${esc(r.en||r.name)}" aria-pressed="${spaceIndex===i}"><title>${esc(r.en||r.name)} · ${r.num||'No space ID'}</title><circle cx="${x}" cy="${y}" r="${spaceIndex===i?10:7}" fill="${spaceIndex===i?'#bb623d':'#fffefa'}" stroke="#263b35" stroke-width="1"/><text x="${x}" y="${y+2.8}" text-anchor="middle" font-size="8" fill="${spaceIndex===i?'#fffefa':'#263b35'}">${i+1}</text></g>`});
 }
 $('skyDrawing').innerHTML=svg;$('skyDrawing').setAttribute('aria-label',mode==='building'?'Sky Fragment floor-plate model; select a level':`Sky Fragment ${l.en} source floor plan and space markers`);
 $('skyDrawing').querySelectorAll('[data-level]').forEach(el=>{el.onclick=()=>{levelIndex=Number(el.dataset.level);spaceIndex=-1;update()};el.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();el.onclick()}}});
 $('skyDrawing').querySelectorAll('[data-space]').forEach(el=>{el.onclick=()=>{spaceIndex=Number(el.dataset.space);render()};el.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();el.onclick()}}});
 $('skyArea').textContent=num(l.plate.area);$('skyCore').textContent=num(l.core?.area);$('skyElevation').textContent=num(l.elev);$('skySpaces').textContent=String(l.rooms?.length||0);$('skySelected').textContent=l.en+' · '+l.id;$('skySelectedUse').textContent=(l.depts||[l.dept]).map(d=>model.depts[d]?.en||d).join(' / ');$('skyLevel').value=String(levelIndex);
 $('skyBuilding').setAttribute('aria-pressed',String(mode==='building'));$('skyFloorPlan').setAttribute('aria-pressed',String(mode==='plan'));$('skyExplodeLabel').hidden=mode!=='building';$('skySpaceLabel').hidden=mode!=='plan';$('skySpace').value=String(spaceIndex);
 const r=l.rooms?.[spaceIndex];$('skySpaceInfo').textContent=r?`${r.en||r.name} · ${r.num||'No ID'} · area: ${num(r.area)}${r.area===null?'':'*'}`:'';
 $('skyStatus').textContent=use!=='all'&&use!=='nucleo'&&!(l.depts||[]).includes(use)?'No '+(model.depts[use]?.en||use)+' zone is recorded on the selected level. Highlight another use or select another level.':'';refreshCompact();
}
function update(){const l=model.levels[levelIndex];$('skySpace').innerHTML='<option value="-1">Choose a space marker</option>'+(l.rooms||[]).map((r,i)=>`<option value="${i}">${i+1}. ${esc(r.en||r.name)}</option>`).join('');render()}
$('skyBuilding').onclick=()=>{mode='building';render()};$('skyFloorPlan').onclick=()=>{mode='plan';render()};$('skyLevel').onchange=()=>{levelIndex=Number($('skyLevel').value);spaceIndex=-1;update()};$('skyUse').onchange=render;$('skyExplode').oninput=render;$('skyRotate').onclick=()=>{rotation=(rotation+1)%4;render()};$('skySpace').onchange=()=>{spaceIndex=Number($('skySpace').value);render()};$('skyEvidence').onclick=()=>{location.hash='evidence';[...document.querySelectorAll('#evidence .compact-tabs button')].find(b=>b.textContent==='Space')?.click()};
$('skyDetails').onclick=()=>showLongText('Sky Fragment — source and limitations',model?`Source: ${model.source}\nSupplied file: model.json (SHA-256 37be1d892a57404b7e7e3e13d09d5c9d6f25250234ba66d92503547720392b12)\n\n${model.levels.length} level entries, including mezzanine and roof. ${model.levels.reduce((n,l)=>n+l.rooms.length,0)} room/space entries, not dwelling units.\nReported height: ${model.height}; reported floor-plate sum: ${model.totals.gfa}; source units are not declared. Polygon areas agree with reported floor-plate areas to rounding.\n\nThe viewer procedurally renders supplied polygons and small floor-slab edges. Detailed shell/level GLB meshes were referenced but not supplied. Room markers use the supplied local positions; they are not surveyed flat boundaries. Repeated typical-floor zones do not identify individual dwellings.\n\nNo London site/application link, explicit existing/proposed phase comparison, daylight assessment, declared area convention or self-contained dwelling schedule is supplied. None of the planning records is promoted to verified by this model.`:'Model still loading.');
fetch('sky-fragment.json').then(r=>{if(!r.ok)throw new Error('Model file could not be loaded');return r.json()}).then(m=>{model=m;levelIndex=Math.max(0,model.levels.findIndex(l=>l.id==='N09'));$('skyLevel').innerHTML=model.levels.map((l,i)=>`<option value="${i}">${esc(l.en+' · '+l.id)}</option>`).join('');update()}).catch(e=>{$('skyStatus').textContent=e.message;$('skySelected').textContent='Model unavailable';});

function showRoomCheck(){document.querySelectorAll('.model-evidence-table tbody tr').forEach((r,i)=>r.hidden=i!==Number($('roomCheck').value));refreshCompact()}
$('roomCheck').onchange=showRoomCheck;showRoomCheck();
