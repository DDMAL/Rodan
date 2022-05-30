let toolkit;
const backlog = [];

/**
 * Parse and respond to messages sent by NeonCore.
 * @param {MessageEvent} evt
 */
function handleNeonEvent (evt) {
  const data = evt.data;
  const result = {
    id: data.id
  };

  switch (data.action) {
    case 'renderData':
      result.svg = toolkit.renderData(data.mei, {});
      break;
    case 'getElementAttr':
      result.attributes = toolkit.getElementAttr(data.elementId);
      break;
    case 'edit':
      result.result = toolkit.edit(data.editorAction);
      break;
    case 'getMEI':
      result.mei = toolkit.getMEI({
        pageNo: 0,
        scoreBased: true
      });
      break;
    case 'editInfo':
      result.info = toolkit.editInfo();
      break;
    case 'renderToSVG':
      result.svg = toolkit.renderToSVG(1);
      break;
    default:
      break;
  }
  postMessage(result);
}

var Module = {
  onRuntimeInitialized: () => {

    toolkit = new verovio.toolkit();
    toolkit.setOptions({
      from: 'mei',
      footer: 'none',
      header: 'none',
      pageMarginLeft: 0,
      pageMarginTop: 0,
      font: 'Bravura',
      useFacsimile: true,
    });
    console.debug("READY");
    onmessage = handleNeonEvent;
    for (const message of backlog) {
      handleNeonEvent(message);
    }
  }
};

importScripts('../assets/js/verovio-toolkit.js');

function tempHandler (evt) {
  backlog.push(evt);
}

onmessage = tempHandler;
