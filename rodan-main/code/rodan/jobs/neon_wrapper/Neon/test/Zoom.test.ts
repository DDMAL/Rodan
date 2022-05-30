/* eslint-env jest */

import { ViewBox } from '../src/SingleView/Zoom';

test('Check ViewBox constructor', () => {
  const viewBox = new ViewBox(300, 400);
  expect(viewBox.c).toBe(300);
  expect(viewBox.d).toBe(400);
});

test('Check \'get\' function', () => {
  const viewBox = new ViewBox(100, 100);
  viewBox.set(0, 0, 100, 100);
  expect(viewBox.get()).toBe('0 0 100 100');
});

test('Check \'translate\' function', () => {
  const viewBox = new ViewBox(100, 100);
  viewBox.set(0, 0, 100, 100);
  viewBox.translate(25, 35);
  expect(viewBox.a).toBe(25);
  expect(viewBox.b).toBe(35);
  expect(viewBox.c).toBe(100);
  expect(viewBox.d).toBe(100);
});

test('Check \'zoomTo\' function', () => {
  const viewBox = new ViewBox(100, 200);
  viewBox.zoomTo(2);
  expect(viewBox.c).toBe(50);
  expect(viewBox.d).toBe(100);
});
