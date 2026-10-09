import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import ts from 'typescript';

// Load the actual trusted source with the existing compiler, including Node 20
// environments that cannot import TypeScript directly. No copied implementation.
const source = readFileSync(new URL('../src/server/route-path.ts', import.meta.url), 'utf8');
const { outputText } = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
});
const exports = {};
new Function('exports', outputText)(exports);
const { decodeRoutePath } = exports;

test('decodes the existing encoded absolute-path API contract', () => {
  assert.equal(decodeRoutePath(['%2Fdata%2Fdataset%2Ftrain.png']), '/data/dataset/train.png');
});
test('joins catch-all segments with slashes rather than commas', () => {
  assert.equal(decodeRoutePath(['data', 'dataset', 'train.png']), 'data/dataset/train.png');
});
test('preserves spaces, unicode and literal commas in file names', () => {
  assert.equal(decodeRoutePath([encodeURIComponent('/data/客室, 图.png')]), '/data/客室, 图.png');
});
test('does not normalize traversal before the resource route checks its allowed roots', () => {
  assert.equal(decodeRoutePath(['data', '..', 'outside.txt']), 'data/../outside.txt');
});
test('rejects malformed URL encoding', () => {
  assert.throws(() => decodeRoutePath(['%E0%A4']), URIError);
});
