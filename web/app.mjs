import {batches, confirmation, movePosition, warning} from './model.mjs';
let state = {items: [], dependencies: []};
let busy = false;
let dragged = null;
const $ = id => document.getElementById(id);
function node(tag, text, className) { const el = document.createElement(tag); if (text !== undefined) el.textContent = text; if (className) el.className = className; return el; }
function message(id, text) { $(id).textContent = text; $(id).hidden = !text; }
async function api(path, body) {
  const response = await fetch(path, body ? {method: 'POST', headers: {'Content-Type': 'application/json', 'X-C3-Intent': 'explicit-user'}, body: JSON.stringify(body)} : {cache: 'no-store'});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error ?? ('HTTP ' + response.status));
  return data;
}
function button(text, fn, danger = false) { const b = node('button', text, danger ? 'danger' : ''); b.type = 'button'; b.disabled = busy; b.addEventListener('click', fn); return b; }
function actions(item) {
  const bar = node('div', undefined, 'actions');
  bar.append(button(item.paused ? 'Resume' : 'Pause', () => act(item, item.paused ? 'resume' : 'pause')),
    button('Stop', () => act(item, 'stop')), button('Cancel', () => act(item, 'cancel'), true), button('Delete', () => act(item, 'delete'), true));
  const priority = node('select'); priority.setAttribute('aria-label', 'Priority for ' + item.title);
  for (const value of ['normal', 'p0', 'p1', 'p2']) { const opt = node('option', value.toUpperCase()); opt.value = value; opt.selected = value === item.priority; opt.disabled = value === 'normal'; priority.append(opt); }
  priority.disabled = busy || item.status === 'running';
  priority.addEventListener('change', () => act(item, 'force-priority', {priority: priority.value}));
  bar.append(priority, button('Move earlier', () => act(item, 'move', {position: movePosition(state, item.work_item_id, -1)})), button('Move later', () => act(item, 'move', {position: movePosition(state, item.work_item_id, 1)})));
  return bar;
}
function confirmed(plan, action) {
  $('confirm-text').textContent = action.toUpperCase() + ': ' + plan.affected.length + ' canonical item(s), including ' + plan.downstream.length + ' downstream item(s).';
  $('affected').replaceChildren(...confirmation(plan, state).map(i => node('li', i.title + ' — ' + i.id)));
  const dialog = $('confirm'); dialog.returnValue = ''; dialog.showModal();
  return new Promise(resolve => dialog.addEventListener('close', () => resolve(dialog.returnValue === 'yes'), {once: true}));
}
async function act(item, action, extra = {}) {
  if (busy) return;
  busy = true; render(); message('error', ''); message('notice', '');
  try {
    const plan = await api('/api/preview', {work_item_id: item.work_item_id, action});
    if (plan.requires_confirmation && !await confirmed(plan, action)) return;
    message('notice', 'Applying user intent through the canonical writer…');
    const response = await api('/api/override', {work_item_id: item.work_item_id, action, ...extra,
      precondition: plan.precondition, request_id: crypto.randomUUID(),
      ...(plan.requires_confirmation ? {confirmed_affected: plan.affected} : {})});
    state = response.state;
    message('notice', warning(response.result, state) || (action + ' applied and verified in canonical state.'));
    $('updated').textContent = 'Canonical readback ' + new Date().toLocaleTimeString();
  } catch (error) { message('error', error.message + '. Refresh canonical state before trying again.'); message('notice', ''); }
  finally { busy = false; render(); }
}
function render() {
  const opened = new Set([...document.querySelectorAll('details[open]')].map(el => el.dataset.id));
  const cards = batches(state, $('done').checked).map(batch => {
    const card = node('article', undefined, 'batch'); card.dataset.id = batch.work_item_id;
    const top = node('div', undefined, 'batch-top'); top.append(node('h2', batch.title));
    const badges = node('div'); badges.append(node('span', batch.display_state ?? batch.status, 'badge state-' + (batch.display_state ?? batch.status)), node('span', batch.priority.toUpperCase(), 'badge')); top.append(badges); card.append(top);
    const progress = node('progress'); progress.max = 100; progress.value = batch.progress_percent ?? 0; progress.setAttribute('aria-label', 'Progress for ' + batch.title);
    card.append(progress, node('div', Math.round(batch.progress_percent ?? 0) + '% complete', 'progress-label'));
    if (batch.kind !== 'projection') {
      card.append(actions(batch)); card.draggable = !busy && batch.status !== 'running';
      card.addEventListener('dragstart', e => { dragged = batch.work_item_id; e.dataTransfer.setData('text/plain', dragged); });
      card.addEventListener('dragover', e => e.preventDefault());
      card.addEventListener('drop', e => { e.preventDefault(); if (!dragged || dragged === batch.work_item_id) return; const item = state.items.find(i => i.work_item_id === dragged); const siblings = state.items.filter(i => i.parent_id === item.parent_id); act(item, 'move', {position: siblings.findIndex(i => i.work_item_id === batch.work_item_id)}); dragged = null; });
    }
    const detail = node('details'); detail.dataset.id = batch.work_item_id; detail.open = opened.has(batch.work_item_id);
    detail.append(node('summary', 'Details · ' + batch.members.length + ' item(s)'));
    const populate = () => {
      if (detail.children.length > 1) return;
    for (const item of batch.members) {
      const task = node('section', undefined, 'task'); task.dataset.id = item.work_item_id;
      task.append(node('h3', item.title), node('div', item.work_item_id, 'id'), node('span', (item.display_state ?? item.status) + ' · ' + item.priority, 'badge'));
      if (item.objective) task.append(node('p', item.objective));
      if (item.blocker) task.append(node('p', 'Blocked: ' + item.blocker));
      if (item.next_action) task.append(node('p', 'Next action: ' + item.next_action));
      if (item.work_item_id !== batch.work_item_id) task.append(actions(item));
      detail.append(task);
    }
    };
    if (detail.open) populate();
    detail.addEventListener('toggle', () => { if (detail.open) populate(); });
    card.append(detail); return card;
  });
  $('batches').replaceChildren(...(cards.length ? cards : [node('p', 'No batches to display.', 'empty')]));
  $('refresh').disabled = busy;
}
async function refresh() {
  if (busy) return;
  try { const next = await api('/api/state'); if (busy) return; state = next; render(); message('error', ''); $('updated').textContent = 'Canonical state ' + new Date().toLocaleTimeString(); }
  catch (error) { message('error', 'Cannot load canonical state: ' + error.message); $('updated').textContent = 'Refresh failed'; }
}
$('refresh').addEventListener('click', refresh); $('done').addEventListener('change', render);
await refresh();
setInterval(() => { if (!document.hidden) refresh(); }, 10000);
