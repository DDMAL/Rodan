import { NeonManifest } from '../Types';
const NeonSchema = require('./manifest/NeonSchema.json');
const NeonContext = require('./manifest/context.json');

import { validate } from 'jsonschema';
/**
 * Check if the provided Neon manifest is parseable.
 * @param {string} manifestString - The Neon manifest as a string.
 */
export function parseManifest (manifestString: NeonManifest): boolean {
  const results = validate(manifestString, NeonSchema);
  const instance = results.instance;
  if (results.errors.length > 0) {
    console.error(results.errors);
    return false;
  }
  const context = instance['@context'];
  if (context === 'https://ddmal.music.mcgill.ca/Neon/contexts/1/manifest.jsonld') {
    return true;
  }
  if ((context[0] === NeonContext[0]) &&
      (context[1]['schema'] === NeonContext[1]['schema']) &&
      (context[1]['title'] === NeonContext[1]['title']) &&
      (context[1]['timestamp'] === NeonContext[1]['timestamp']) &&
      (context[1]['image']['@id'] === NeonContext[1]['image']['@id']) &&
      (context[1]['image']['@type'] === NeonContext[1]['image']['@type']) &&
      (context[1]['mei_annotations']['@id'] === NeonContext[1]['mei_annotations']['@id']) &&
      (context[1]['mei_annotations']['@type'] === NeonContext[1]['mei_annotations']['@type']) &&
      (context[1]['mei_annotations']['@container'] === NeonContext[1]['mei_annotations']['@container'])) {
    return true;
  } else {
    console.error('Context mismatch');
    console.error(context);
    console.error(NeonContext);
    return false;
  }
}
