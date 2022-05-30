/**
 * Formats raw UUID data into the proper string format.
 * @param data - Raw UUID data.
 * @returns Formatted UUID string.
 */
function uint8ToUuid (data: Uint8Array): string {
  if (data.length !== 16) {
    return '';
  }

  function cb (previous: string, current: number): string {
    return previous + current.toString(16).padStart(2, '0');
  }

  return data.slice(0, 4).reduce(cb, '') +
    '-' + data.slice(4, 6).reduce(cb, '') +
    '-' + data.slice(6, 8).reduce(cb, '') +
    '-' + data.slice(8, 10).reduce(cb, '') +
    '-' + data.slice(10).reduce(cb, '');
}

/**
 * @returns A [version 4 UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)).
 */
export function uuidv4 (): string {
  // Check for crypto API
  if (window.crypto === undefined) {
    return uint8ToUuid(new Uint8Array(16));
  }

  // Get 16 octets for UUID
  const octets = new Uint8Array(16);
  const modifiers = Uint8Array.from([
    parseInt('01000000', 2),  // Version bits (4 => 0100)
    parseInt('10000000', 2),  // Variant bits (10x)
    parseInt('00001111', 2),  // Mask to zero higher bits, version
    parseInt('00111111', 2)   // Mask to zero higher bits, variant
  ]);
  window.crypto.getRandomValues(octets);
  // Set version bits and variant bits
  octets[6] = (octets[6] & modifiers[2]) | modifiers[0];
  octets[8] = (octets[8] & modifiers[3]) | modifiers[1];

  return uint8ToUuid(octets);
}
