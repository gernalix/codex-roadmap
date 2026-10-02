import test from 'node:test';
import assert from 'node:assert/strict';
import {batches, confirmation, movePosition, warning} from './model.mjs';
const state = {items: [
  {work_item_id:'batch',parent_id:null,kind:'goal',status:'pending',progress_percent:50},
  {work_item_id:'task',parent_id:'batch',kind:'task',status:'running',title:'Task'},
  {work_item_id:'child',parent_id:'task',kind:'step',status:'pending'},
  {work_item_id:'solo',parent_id:null,kind:'task',status:'pending'},
  {work_item_id:'done',parent_id:null,kind:'goal',status:'completed'}
]};
test('batch default and details use canonical progress and hierarchy',()=>{
 const result=batches(state);assert.deepEqual(result.map(i=>i.work_item_id),['batch','independent']);assert.equal(result[0].progress_percent,50);assert.equal(result[0].members.length,3);assert.equal(batches(state,true).length,3);
});
test('empty state and projection do not invent canonical items',()=>{assert.deepEqual(batches({items:[]}),[]);assert.equal(state.items.length,5);});
test('destructive confirmation lists exact IDs and canonical titles',()=>{assert.deepEqual(confirmation({affected:['task','missing']},state),[{id:'task',title:'Task'},{id:'missing',title:'missing'}]);});
test('ordering uses canonical sibling positions and clamps boundaries',()=>{assert.equal(movePosition(state,'solo',-1),0);assert.equal(movePosition(state,'batch',-1),0);});
test('prevented move explains exact blocking prerequisite',()=>{assert.match(warning({blocking_prerequisites:['task']},state),/Task \(task\)/);assert.equal(warning({},state),'');});
