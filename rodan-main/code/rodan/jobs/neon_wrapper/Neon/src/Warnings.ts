/** @module Warnings */

/**
 * Warn when grouped neume components form an unrecognized neume.
 */
export function groupingNotRecognized () {
  if (!(window.confirm('Neon does not recognize this neume grouping. Would you like to create a compound neume?'))) {
    document.getElementById('undo').click();
  }
}
