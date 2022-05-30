import NeonView from '../../src/NeonView';
import DisplayPanel from '../../src/DisplayPanel/DisplayPanel';
import DivaView from '../../src/DivaView';
import DivaEdit from '../../src/SquareEdit/DivaEditMode';
import SingleView from '../../src/SingleView/SingleView';
import SingleEditMode from '../../src/SquareEdit/SingleEditMode';
import InfoModule from '../../src/InfoModule';
import TextView from '../../src/TextView';
import TextEditMode from '../../src/TextEditMode';
import { NeonManifest } from '../../src/Types';

declare let manifestText: string;

let view: NeonView;

async function init (): Promise<void> {
  if (manifestText !== '') {
    const manifest: NeonManifest = JSON.parse(manifestText);
    const params = {
      manifest: manifest,
      Display: DisplayPanel,
      Info: InfoModule,
      TextView: TextView,
      TextEdit: TextEditMode,
      View: undefined,
      NeumeEdit: undefined
    };
    let singlePage: boolean;
    switch (manifest.mei_annotations.length) {
      case 0:
        throw new Error('Cannot load Neon without any MEI files!');
        break;
      case 1:
        singlePage = true;
        break;
      default:
        singlePage = false;
    }

    params.View = singlePage ? SingleView : DivaView;
    params.NeumeEdit = singlePage ? SingleEditMode : DivaEdit;

    view = new NeonView(params);
    view.start();
  }
}

init();
