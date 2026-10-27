import test from 'node:test';
import assert from 'node:assert/strict';
import {quote} from './quote.mjs';
test('3 × 4 ft, two pieces totals ₱600 with ₱300 deposit',()=>{const q=quote({width:3,height:4,quantity:2});assert.equal(q.totalCents,60000);assert.equal(q.depositCents,30000);});
test('minimum area, rush and cent-precise delivery',()=>{const q=quote({width:1,height:1,quantity:1,rush:true,delivery:10.15});assert.equal(q.totalCents,19015);});
test('invalid inputs cannot produce a quote',()=>{for(const patch of [{width:NaN},{height:-1},{quantity:1.5},{delivery:.001},{delivery:Infinity},{rush:'yes'}])assert.throws(()=>quote({width:3,height:4,quantity:2,...patch}));});
