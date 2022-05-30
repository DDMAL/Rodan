import { uuidv4 } from './random';

const notifications: Notification[] = new Array(0);
let currentModeMessage: Notification = null;
let notifying = false;

/**
 * Number of notifications to display at a time.
 */
const NUMBER_TO_DISPLAY = 3;

/**
 * Add a notification to the queue.
 * @param notification - Notification content.
 */
export function queueNotification (notification: string): void {
  const notif = new Notification(notification);
  notifications.push(notif);
  if (!notifying || document.getElementById('notification-content').querySelectorAll('.neon-notification').length < NUMBER_TO_DISPLAY) {
    startNotification();
  }
}

/**
 * Start displaying notifications. Called automatically.
 */
function startNotification (): void {
  if (notifications.length > 0) {
    notifying = true;
    const currentNotification = notifications.pop();
    displayNotification(currentNotification);
    currentNotification.setTimeoutId(window.setTimeout(clearOrShowNextNotification, 5000, currentNotification.getId()));
    document.getElementById(currentNotification.getId()).addEventListener('click', () => {
      window.clearTimeout(currentNotification.timeoutID);
      clearOrShowNextNotification(currentNotification.getId());
    });
  }
}

/**
 * Display a notification.
 * @param notification - Notification to display.
 */
function displayNotification (notification: Notification): void {
  if (notification.isModeMessage) {
    if (currentModeMessage === null) {
      currentModeMessage = notification;
    } else {
      window.clearTimeout(currentModeMessage.timeoutID);
      notifications.push(notification);
      clearOrShowNextNotification(currentModeMessage.getId());
      return;
    }
  }
  const notificationContent = document.getElementById('notification-content');
  notificationContent.innerHTML += '<div class=\'neon-notification\' id=\'' + notification.getId() + '\'>' + notification.message + '</div> ';
  notificationContent.style.display = '';
  notification.display();
}

/**
 * Clear the notifications if no more exist or display another from the queue.
 * @param currentId - The ID of the notification to be cleared.
 */
function clearOrShowNextNotification (currentId: string): void {
  document.getElementById(currentId).remove();
  if (currentModeMessage !== null && currentModeMessage.getId() === currentId) {
    currentModeMessage = null;
  }
  if (notifications.length > 0) {
    startNotification();
  } else if (document.querySelectorAll('.neon-notification').length === 0) {
    document.getElementById('notification-content').style.display = 'none';
    notifying = false;
  }
}

/**
 * A class to manage Neon notifications.
 */
class Notification {
  message: string;
  displayed: boolean;
  id: string;
  isModeMessage: boolean;
  timeoutID: number;
  /**
   * Create a new notification.
   * @param message - Notification content.
   */
  constructor (message: string) {
    this.message = message;
    this.displayed = false;
    this.id = uuidv4();
    this.isModeMessage = message.search('Mode') !== -1;
    this.timeoutID = -1;
  }

  /** Set the ID from setTimeout. */
  setTimeoutId (id: number): void {
    this.timeoutID = Math.max(id, -1);
  }

  /** Display the Notification. */
  display (): void {
    this.displayed = true;
  }

  /**
   * @returns The UUID for this notification.
   */
  getId (): string {
    return this.id;
  }
}
