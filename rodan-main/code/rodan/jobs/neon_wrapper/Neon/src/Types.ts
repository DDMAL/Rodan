/** Type definitions for Neon */

export type Attributes = { pname?: string; oct?: number; shape?: string; line?: number; ligated?: boolean };

/** An editing action sent to verovio as described [here](https://github.com/DDMAL/Neon/wiki/Toolkit-Actions). */
export type EditorAction = {
  action: string;
  param: object | EditorAction[];
};

/** A message sent to the verovio web worker. */
export type VerovioMessage = {
  action: string;
  id: string;
  mei?: string;
  elementId?: string;
  editorAction?: EditorAction;
};

export type VerovioResponse = {
  id: string;
  svg?: string;
  attributes?: Attributes;
  result?: boolean;
  mei?: string;
  info?: object;
};

/** Modeled after the [W3 Web Annotation Data Model.](https://www.w3.org/TR/annotation-model/) */
export type WebAnnotation = {
  id: string;
  type: string;
  body: string;
  target: string;
};

/** Required fields in the JSON-LD Neon manifest. */
export type NeonManifest = {
  '@context': Array<string | object> | string;
  '@id': string;
  title: string;
  timestamp: string;
  image: string;
  mei_annotations: WebAnnotation[];
};
