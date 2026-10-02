export const terminal = new Set(['completed', 'cancelled', 'superseded', 'waived']);
export function descendants(items, id) {
  const ids = new Set([id]);
  let changed = true;
  while (changed) {
    changed = false;
    for (const i of items) if (ids.has(i.parent_id) && !ids.has(i.work_item_id)) { ids.add(i.work_item_id); changed = true; }
  }
  return items.filter(i => ids.has(i.work_item_id));
}
export function batches(state, includeDone = false) {
  const items = state.items;
  const roots = items.filter(i => !i.parent_id);
  const grouped = roots.filter(i => i.kind === 'goal' || i.kind === 'phase' || items.some(c => c.parent_id === i.work_item_id));
  const result = grouped.filter(i => includeDone || !terminal.has(i.status)).map(i => ({...i, members: descendants(items, i.work_item_id)}));
  const independent = roots.filter(i => !grouped.includes(i));
  const shown = independent.filter(i => includeDone || !terminal.has(i.status));
  if (shown.length) result.push({work_item_id: 'independent', title: 'Independent tasks', kind: 'projection',
    display_state: shown.some(i => i.status === 'running') ? 'running' : 'pending', priority: 'mixed',
    progress_percent: independent.length ? Math.round(independent.filter(i => terminal.has(i.status)).length / independent.length * 100) : 0, members: shown});
  return result;
}
export function confirmation(plan, state) {
  const lookup = new Map(state.items.map(i => [i.work_item_id, i]));
  return plan.affected.map(id => ({id, title: lookup.get(id)?.title ?? id}));
}
export function movePosition(state, id, direction) {
  const item = state.items.find(i => i.work_item_id === id);
  const siblings = state.items.filter(i => i.parent_id === item.parent_id);
  return Math.max(0, Math.min(siblings.length - 1, siblings.findIndex(i => i.work_item_id === id) + direction));
}
export function warning(result, state) {
  const names = new Map(state.items.map(i => [i.work_item_id, i.title]));
  return result.blocking_prerequisites?.length ? 'Dependency constrained this move: ' + result.blocking_prerequisites.map(id => (names.get(id) ?? id) + ' (' + id + ')').join(', ') : '';
}
