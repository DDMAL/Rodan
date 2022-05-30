const schemaResponse = fetch(__ASSET_PREFIX__ + 'assets/mei-all.rng');
let worker: Worker, schema: string, statusField: HTMLSpanElement;

/**
 * Update the UI with the validation results. Called when the WebWorker finishes validating.
 */
function updateUI (message: { data: string[] }): void {
  const errors = message.data;
  if (errors === null) {
    statusField.textContent = 'VALID';
    statusField.style.color = 'green';
    for (const child of statusField.children) {
      child.remove();
    }
  } else {
    let log = '';
    errors.forEach(line => {
      log += line + '\n';
    });
    statusField.textContent = '';
    statusField.style.color = 'red';
    const link = document.createElement('a');
    link.setAttribute('href', 'data:text/plain;charset=utf-8,' +
      encodeURIComponent(log));
    link.setAttribute('download', 'validation.log');
    link.textContent = 'INVALID';
    statusField.appendChild(link);
  }
}

/**
 * Add the validation information to the display and create the WebWorker
 * for validation MEI.
 */
export async function init (): Promise<void> {
  const displayContents = document.getElementById('displayContents');
  if (displayContents !== null) {
    const panelBlock = document.createElement('div');
    panelBlock.classList.add('panel-block');
    const pNotif = document.createElement('p');
    pNotif.textContent = 'MEI Status: ';
    const span = document.createElement('span');
    span.id = 'validation_status';
    span.textContent = 'unknown';
    pNotif.appendChild(span);
    panelBlock.appendChild(pNotif);
    displayContents.appendChild(panelBlock);
    statusField = document.getElementById('validation_status');
    worker = new Worker(__ASSET_PREFIX__ + 'workers/Worker.js');
    worker.onmessage = updateUI;
  }
}

/**
 * Send the contents of an MEI file to the WebWorker for validation.
 * @param {string} meiData
 */
export async function sendForValidation (meiData: string): Promise<void> {
  if (statusField === undefined) {
    return;
  }
  if (schema === undefined) {
    const response = await schemaResponse;
    schema = await response.text();
  }
  statusField.textContent = 'checking...';
  statusField.style.color = 'gray';
  worker.postMessage({
    mei: meiData,
    schema: schema
  });
}

/**
 * Update the message on a blank page when there is no MEI.
 */
export function blankPage (): void {
  for (const child of statusField.children) {
    child.remove();
  }
  statusField.textContent = 'No MEI';
  statusField.style.color = 'color:gray';
}
