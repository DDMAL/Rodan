/* eslint-env jest */

import * as Notification from '../src/utils/Notification';

beforeEach(() => {
  document.body.innerHTML =
        '<div id="notification-content">' +
        '</div>';
});

afterEach(() => {
  document.body.innerHTML = '';
});

test('Ensure notification displays and can be dismissed', () => {
  Notification.queueNotification('Test');
  expect(document.getElementsByClassName('neon-notification')[0].innerHTML).toBe('Test');
  document.getElementsByClassName('neon-notification')[0].dispatchEvent(new MouseEvent('click'));
  expect(document.getElementsByClassName('neon-notification').length).toBe(0);
});

test('Ensure maximum number of notifications is not exceeded', () => {
  expect(document.getElementsByClassName('neon-notification').length).toBe(0);
  // Queue the maximum number of notifications, ensure they all appear
  Notification.queueNotification('Test 1');
  Notification.queueNotification('Test 2');
  Notification.queueNotification('Test 3');
  expect(document.getElementsByClassName('neon-notification').length).toBe(3);
  Notification.queueNotification('Test 4');
  expect(document.getElementsByClassName('neon-notification').length).toBe(3);
});

test('Ensure at most one \'Mode\' notification appears', () => {
  expect(document.getElementsByClassName('neon-notification').length).toBe(0);
  Notification.queueNotification('Edit Mode');
  expect(document.getElementsByClassName('neon-notification')[0].innerHTML).toBe('Edit Mode');
  Notification.queueNotification('Insert Mode');
  expect(document.getElementsByClassName('neon-notification')[0].innerHTML).toBe('Insert Mode');
  expect(document.getElementsByClassName('neon-notification').length).toBe(1);
  // Make sure another notification will still appear
  Notification.queueNotification('Something Else');
  expect(document.getElementsByClassName('neon-notification').length).toBe(2);
});
