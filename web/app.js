const $ = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
async function api(path) {
  const response = await fetch(path);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Falha na consulta");
  return data;
}
function fillSelect(id, values) {
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value; option.textContent = value; $(id).append(option);
  }
}
async function loadFacets() {
  const {facets} = await api("/api/v1/facets");
  fillSelect("nature", facets.document_nature);
  fillSelect("verification", facets.verification_status);
  fillSelect("temporal", facets.temporal_status);
  fillSelect("institution", facets.issuing_authority);
  fillSelect("force", facets.legal_force);
}
async function search() {
  const params = new URLSearchParams();
  const values = {q:$("query").value,nature:$("nature").value,legal_force:$("force").value,verification_status:$("verification").value,temporal_status:$("temporal").value,institution:$("institution").value,subject:$("subject").value,date_from:$("date-from").value,date_to:$("date-to").value};
  for (const [key,value] of Object.entries(values)) if (value) params.set(key,value);
  const data = await api("/api/v1/search?" + params);
  $("count").textContent = "(" + data.total + ")";
  $("results").innerHTML = data.results.map(item => `<article class="result"><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.official_identifier || "")}</p><p class="tags">${escapeHtml(item.verification_status)} · força: ${escapeHtml(item.legal_force)} · vigência: ${escapeHtml(item.temporal_status)}</p><button data-record="${escapeHtml(item.record_id)}">Ver relações</button></article>`).join("") || "<p>Nenhum registro encontrado.</p>";
  document.querySelectorAll("[data-record]").forEach(button => button.addEventListener("click", () => loadGraph(button.dataset.record)));
}
async function loadCoverage() {
  const data = await api("/api/v1/coverage");
  const c = data.target_counts;
  $("coverage").innerHTML = `<p><strong>${data.targets.length}</strong> alvos nesta revisão</p><ul><li>Verificados: ${c.verified}</li><li>Pendentes: ${c.pending_verification}</li><li>Não localizados: ${c.not_located}</li></ul><p class="muted">${escapeHtml(data.scope_note)}</p>`;
}
async function loadGraph(recordId) {
  const data = await api("/api/v1/graph?record_id=" + encodeURIComponent(recordId) + "&depth=1");
  $("graph").innerHTML = data.edges.map(edge => {
    const from = data.nodes.find(node => node.id === edge.source);
    const to = data.nodes.find(node => node.id === edge.target);
    const evidence = edge.evidence.map(item => item.url ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noopener">evidência</a>` : "sem URL").join(", ");
    return `<article class="edge"><strong>${escapeHtml(from?.title || edge.source)}</strong><span>→ ${escapeHtml(edge.relation)} →</span><strong>${escapeHtml(to?.title || edge.target)}</strong><p>${evidence} · ${escapeHtml(edge.evidence.map(item => item.verification_status).join(", "))}</p></article>`;
  }).join("") || "<p>Sem relações registadas para este documento.</p>";
}
$("search-form").addEventListener("submit", event => {event.preventDefault(); search().catch(showError);});
function showError(error) {$("results").innerHTML = `<p class="error">${escapeHtml(error.message)}</p>`;}
Promise.all([loadFacets(), search(), loadCoverage()]).catch(showError);
