const $ = id => document.getElementById(id);
const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const safeLink = value => typeof value === "string" && /^https:\/\//i.test(value) ? value : "";
async function api(path) {
  const response = await fetch(path, {headers: {"Accept":"application/json"}});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error?.message || data.error || "Falha na consulta");
  return data;
}
function optionValues(id, values) {
  for (const value of values) { const o=document.createElement("option"); o.value=value; o.textContent=value; $(id).append(o); }
}
async function init() {
  const [facets, coverage, sources, graph, count] = await Promise.all([
    api("/api/v1/facets"), api("/api/v1/coverage"), api("/api/v1/sources"),
    api("/api/v1/graph"), api("/api/v1/search?limit=1")
  ]);
  optionValues("nature", facets.facets.document_nature);
  optionValues("institution", facets.facets.issuing_authority);
  optionValues("subject", facets.facets.subject_matter);
  optionValues("force", facets.facets.legal_force);
  optionValues("temporal", facets.facets.temporal_status);
  optionValues("verification", facets.facets.verification_status);
  renderStats(count.total, coverage, graph, sources.sources.length);
  renderCategories(facets.facets.subject_matter);
  renderSources(sources.sources);
  restoreUrlState();
  const initialRecord = new URLSearchParams(location.search).get("record");
  if (initialRecord) await openDocument(initialRecord); else await search(false);
  window.addEventListener("popstate", () => { const record = new URLSearchParams(location.search).get("record"); if (record) openDocument(record); else { $("document-view").hidden=true; $("pesquisa").hidden=false; $("grafo").hidden=true; restoreUrlState(); search(false); } });
}
function renderStats(total, coverage, graph, sourceCount) {
  const counts=coverage.target_counts;
  const unresolved=graph.nodes.filter(n=>n.verification_status==="unresolved_reference").length;
  const ambiguous=graph.nodes.filter(n=>n.verification_status==="ambiguous_reference").length;
  $("stats").innerHTML=`<div><strong>${total}</strong><span>registros no catálogo</span></div><div><strong>${counts.verified}</strong><span>alvos verificados na cobertura</span></div><div><strong>${sourceCount}</strong><span>fontes inventariadas</span></div><div><strong>${unresolved+ambiguous}</strong><span>referências por rever</span></div>`;
}
function renderCategories(subjects) {
  $("categories").innerHTML=subjects.map(s=>`<button class="category" data-subject="${escapeHtml(s)}">${escapeHtml(s)} <span aria-hidden="true">↗</span></button>`).join("");
  document.querySelectorAll("[data-subject]").forEach(b=>b.addEventListener("click",()=>{ $("subject").value=b.dataset.subject; location.hash="pesquisa"; search(); }));
}
function renderSources(sources) {
  $("sources").innerHTML=sources.map(s=>{const url=safeLink(s.source_url);return `<article class="source-card"><p class="eyebrow">${escapeHtml(s.source_type.replaceAll("_"," "))}</p><h3>${url?`<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(s.source_name)}</a>`:escapeHtml(s.source_name)}</h3><p>${escapeHtml(s.institution)}</p><p class="muted">${escapeHtml(s.jurisdiction_coverage)}</p><span class="status-chip">${escapeHtml(s.verification_status)}</span></article>`;}).join("");
}
function formState() {
  return {q:$("query").value,nature:$("nature").value,institution:$("institution").value,subject:$("subject").value,legal_force:$("force").value,temporal_status:$("temporal").value,verification_status:$("verification").value,date_from:$("date-from").value,date_to:$("date-to").value};
}
function restoreUrlState() {
  const p=new URLSearchParams(location.search);
  $("query").value=p.get("q")||"";
  $("nature").value=p.get("nature")||"";
  $("institution").value=p.get("institution")||"";
  $("subject").value=p.get("subject")||"";
  $("force").value=p.get("legal_force")||"";
  $("temporal").value=p.get("temporal_status")||"";
  $("verification").value=p.get("verification_status")||"";
  $("date-from").value=p.get("date_from")||"";
  $("date-to").value=p.get("date_to")||"";
}
async function search(updateUrl=true, offset=0) {
  $("results").setAttribute("aria-busy","true");
  $("results").innerHTML='<p class="loading" role="status">A pesquisar…</p>';
  const state=formState(), p=new URLSearchParams();
  for(const [k,v] of Object.entries(state)) if(v) p.set(k,v);
  p.set("limit","10");p.set("offset",String(offset));
  if(updateUrl) history.pushState(null,"","?"+p.toString()+"#pesquisa");
  try {
    const data=await api("/api/v1/search?"+p.toString());
    $("search-summary").textContent=`${data.total} resultado(s)`;
    $("results").innerHTML=data.results.map(renderResult).join("")||'<div class="empty"><h3>Sem resultados</h3><p>Tente outro termo ou remova alguns filtros.</p></div>';
    document.querySelectorAll("[data-document]").forEach(b=>b.addEventListener("click",()=>openDocument(b.dataset.document)));
    renderPagination(data);
  } catch(e) { showError(e); }
  finally {$("results").setAttribute("aria-busy","false");}
}
function renderResult(r) {
  return `<article class="result-card"><div><p class="eyebrow">${escapeHtml(r.document_nature)} · ${escapeHtml(r.date_published||"data desconhecida")}</p><h3><button class="text-link" data-document="${escapeHtml(r.record_id)}">${escapeHtml(r.title)}</button></h3><p>${escapeHtml(r.official_identifier||"Identificador não disponível")}</p><p class="muted">${escapeHtml(r.issuing_authority||"Entidade emissora desconhecida")}</p></div><div class="chips"><span>${escapeHtml(r.verification_status)}</span><span>força: ${escapeHtml(r.legal_force||"desconhecida")}</span><span>vigência: ${escapeHtml(r.temporal_status||"desconhecida")}</span></div></article>`;
}
function renderPagination(data) {
  const pages=Math.ceil(data.total/data.limit), current=Math.floor(data.offset/data.limit);
  if(pages<=1){$("pagination").innerHTML="";return;}
  $("pagination").innerHTML=`<button ${current===0?"disabled":""} id="prev-page">Anterior</button><span>Página ${current+1} de ${pages}</span><button ${current>=pages-1?"disabled":""} id="next-page">Seguinte</button>`;
  $("prev-page").onclick=()=>search(true,Math.max(0,data.offset-data.limit));
  $("next-page").onclick=()=>search(true,data.offset+data.limit);
}
function showError(error) {$("results").innerHTML=`<div class="error" role="alert"><strong>Não foi possível concluir a consulta.</strong><p>${escapeHtml(error.message)}</p><button id="retry">Tentar novamente</button></div>
  $("retry").onclick=()=>search();}
async function openDocument(id) {
  $("document-view").hidden=false;$("pesquisa").hidden=true;$("grafo").hidden=true;
  $("document-content").innerHTML='<p role="status">A carregar o registro…</p>';
  history.pushState(null,"","?record="+encodeURIComponent(id));
  try {
    const r=await api("/api/v1/documents/"+encodeURIComponent(id));
    $("document-content").innerHTML=renderDocument(r);
    const graph=await api("/api/v1/graph?record_id="+encodeURIComponent(id)+"&depth=1");
    $("grafo").hidden=false;renderGraph(graph);
  } catch(e) {$("document-content").innerHTML=`<div role="alert" class="error">${escapeHtml(e.message)}</div>`;}
  window.scrollTo(0,0);
}
function label(value, unknown="Desconhecido / não verificado") {return value===null||value===undefined||value===""?unknown:value;}
function renderDocument(r) {
  const source=safeLink(r.source_url), reuse=r.reuse_rights||{}, provenance=r.provenance||{}, version=r.versioning||{};
  const relationList=(r.related_identifiers||[]).map(x=>`<li>${escapeHtml(x.relation||"relação não especificada")}: ${escapeHtml(x.value)}</li>`).join("")||"<li>Sem relações registadas.</li>";
  return `<p class="eyebrow">REGISTRO JURÍDICO · ${escapeHtml(r.verification_status)}</p><h1 id="document-title">${escapeHtml(r.title)}</h1><p class="lead">${escapeHtml(label(r.official_identifier,"Identificador oficial não registado"))}</p>
  <div class="document-grid"><section><h2>Identificação</h2><dl>
  <dt>Natureza</dt><dd>${escapeHtml(label(r.document_nature))}</dd><dt>Entidade emissora</dt><dd>${escapeHtml(label(r.issuing_authority))}</dd><dt>Publicação</dt><dd>${escapeHtml(label(r.date_published,"Data desconhecida"))}</dd><dt>Força jurídica</dt><dd>${escapeHtml(label(r.legal_force,"Não verificada"))}</dd><dt>Estado temporal</dt><dd>${escapeHtml(label(r.temporal_status,"Desconhecido / não verificado"))}</dd><dt>Verificação</dt><dd>${escapeHtml(label(r.verification_status,"Não verificada"))}</dd><dt>Direitos de reutilização</dt><dd>${escapeHtml(label(reuse.status,"Desconhecidos"))} — ${escapeHtml(label(reuse.notes,"Condições não especificadas"))}</dd>
  </dl></section><section><h2>Fonte e proveniência</h2><p>${source?`<a href="${escapeHtml(source)}" target="_blank" rel="noopener noreferrer">Abrir fonte original</a>`:"Ligação de fonte não registada."}</p><p>${escapeHtml(label(provenance.source_description,"Proveniência não registada"))}</p><p><strong>Método:</strong> ${escapeHtml(label(provenance.method,"Método não registado"))}</p><h2>Versões</h2><p>${escapeHtml(label(version.version_label,"Histórico de versões não disponível"))} · tipo: ${escapeHtml(label(version.version_type))} · monitorização: ${escapeHtml(label(version.change_status))}</p></section></div>
  <section><h2>Relações declaradas</h2><ul>${relationList}</ul></section>`;
}
function renderGraph(graph) {
  const nodes=new Map(graph.nodes.map(n=>[n.id,n]));
  const items=graph.edges.map(e=>{
    const a=nodes.get(e.source),b=nodes.get(e.target);
    const endpoint=n=>{if(!n)return "";if(n.resolved)return "";let suggestions=(n.suggested_matches||[]).map(m=>{const c=nodes.get(m.record_id);return `<li>${escapeHtml(c?.title||m.record_id)} — sugestão ${escapeHtml(m.similarity)}</li>`;}).join("");return `<p class="warning">${n.verification_status==="ambiguous_reference"?"Referência ambígua":"Referência não resolvida"}; não confirma relação.${suggestions?`<ul>${suggestions}</ul>`:""}</p>`;};
    return `<article class="edge"><strong>${escapeHtml(a?.title||e.source)}</strong>${endpoint(a)}<span>→ ${escapeHtml(e.relation)} →</span><strong>${escapeHtml(b?.title||e.target)}</strong>${endpoint(b)}<p>${e.evidence.map(v=>v.url?safeLink(v.url)?`<a href="${escapeHtml(v.url)}" target="_blank" rel="noopener noreferrer">evidência</a>`:"URL indisponível":"URL não registada").join(" · ")} · estado: ${escapeHtml(e.evidence.map(v=>v.verification_status).join(", "))}</p></article>`;
  }).join("");
  $("graph").innerHTML=items||"<p>Sem relações registadas para este documento.</p>";
}
$("hero-form").addEventListener("submit",e=>{e.preventDefault();$("query").value=$("hero-query").value;location.hash="pesquisa";search();});
$("search-form").addEventListener("submit",e=>{e.preventDefault();search();});
$("clear-filters").addEventListener("click",()=>{$("search-form").reset();history.pushState(null,"","/");search(false);});
$("back-search").addEventListener("click",()=>{$("document-view").hidden=true;$("pesquisa").hidden=false;$("grafo").hidden=true;});
init().catch(showError);
