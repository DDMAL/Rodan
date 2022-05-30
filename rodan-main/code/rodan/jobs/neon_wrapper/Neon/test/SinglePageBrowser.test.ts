/* eslint-env jest */
const pathToResources = './test/resources/';
const pathToUploads = './deployment/public/uploads/';
const editUrl = 'http://localhost:8080/edit/test.jsonld';

import * as fs from 'fs';
import { Builder, By, Key, until } from 'selenium-webdriver';
import * as error from 'selenium-webdriver/lib/error';
import * as logging from 'selenium-webdriver/lib/logging';
import * as firefox from 'selenium-webdriver/firefox';
import * as chrome from 'selenium-webdriver/chrome';

const browserNames = ['firefox', 'chrome'];
/* Safari webdriver not working properly as of v13.0.4
if (require('os').platform() === 'darwin') {
  browserNames.push('safari');
}
*/
jest.setTimeout(20000);

beforeAll(async () => {
  // Link test MEI/png to public/uploads so we can use them
  fs.linkSync(pathToResources + 'test.png', pathToUploads + 'img/test.png');
  fs.linkSync(pathToResources + 'test.mei', pathToUploads + 'mei/test.mei');
  fs.linkSync(pathToResources + 'test.jsonld', pathToUploads + 'manifests/test.jsonld');
});

afterAll(() => {
  // Clean up test files
  fs.unlinkSync(pathToUploads + 'img/test.png');
  fs.unlinkSync(pathToUploads + 'mei/test.mei');
  fs.unlinkSync(pathToUploads + 'manifests/test.jsonld');
});

describe.each(browserNames)('Tests on %s', (title) => {
  let browser;
  const prefs = new logging.Preferences();
  prefs.setLevel(logging.Type.BROWSER, logging.Level.ALL);

  beforeAll(async () => {
    browser = await new Builder()
      .forBrowser(title)
      .setFirefoxOptions(new firefox.Options().headless())
      .setChromeOptions(new chrome.Options().headless().windowSize({ width: 1280, height: 800 }))
      .setLoggingPrefs(prefs)
      .build();
    await browser.get(editUrl);
  });

  afterAll(done => {
    if (title === 'chrome') {
      browser.manage().logs().get(logging.Type.BROWSER).then(entries => {
        entries.forEach(entry => {
          console.log(entry);
        });
      }).catch(err => { console.error(err); }).then(() => {
        browser.quit();
        done();
      });
    } else {
      browser.quit();
      done();
    }
  });

  describe('Neon Basics', () => {
    test('Render Page', async () => {
      const title = await browser.getTitle();
      expect(title).toBe('Neon');
    });
  });

  describe('Check Info Box', () => {
    test('Check Info Box Neumes', async () => {
      const neumeID = 'm-07ad2140-4fa1-45d4-af47-6733add00825';
      await browser.wait(until.elementLocated(By.id(neumeID)), 10000); // Wait ten seconds for elements to appear
      await browser.executeScript(() => { document.getElementById('displayInfo').click(); });
      await browser.wait(until.elementLocated(By.className('message-body')), 10000);
      await browser.executeScript((neumeID) => { document.getElementById(neumeID).dispatchEvent(new Event('mouseover')); }, neumeID);
      // await browser.executeScript((neumeID) => { document.getElementById(neumeID).dispatchEvent(new Event('mouseleave')); }, neumeID);
      const body = await browser.findElement(By.className('message-body'));
      await browser.wait(until.elementIsVisible(body), 10000);

      await browser.wait(until.elementTextContains(body, 'Clivis'), 10000);
      await browser.wait(until.elementTextContains(body, 'A2 G2'), 10000);
    });

    test('Check Info Box Clef', async () => {
      const clefId = 'm-45439068-5e0c-4595-a820-4faa16771422';
      await browser.wait(until.elementLocated(By.id(clefId)), 5000);
      await browser.executeScript((id) => { document.getElementById(id).dispatchEvent(new Event('mouseover')); }, clefId);
      const notification = await browser.findElement(By.className('message'));
      await browser.wait(until.elementTextMatches(notification, /clef/), 5000);
      const message = await browser.findElement(By.className('message-body')).getText();
      expect(message).toContain('Shape: C');
      expect(message).toContain('Line: 3');
    });

    test('Check Info Box Custos', async () => {
      const custosId = 'm-9e59174b-ed59-43a5-bba8-08e8eb276509';
      await browser.wait(until.elementLocated(By.id(custosId)), 2000);
      await browser.executeScript((id) => { document.getElementById(id).dispatchEvent(new Event('mouseover')); }, custosId);
      const message = await browser.findElement(By.className('message-body')).getText();
      expect(message).toContain('Pitch: G3');
    });
  });

  describe('Check Syl Bounding Box UI', () => {
    beforeAll(async () => {
      await browser.wait(until.elementLocated(By.id('edit_mode')), 5000);
      await browser.executeScript(() => { document.getElementById('edit_mode').click(); });
      await browser.executeScript(() => { document.getElementById('displayBBox').click(); });
      await browser.executeScript(() => { document.getElementById('selByBBox').click(); });
    });

    afterAll(async () => {
      await browser.executeScript(() => { document.getElementById('displayBBox').click(); });
    });

    test('Default BBox adding', async () => {
      const syls = (await browser.findElements(By.className('syl')));
      expect(syls.length).toBe(188);
      const bboxes = (await browser.findElements(By.className('sylTextRect-display')));
      expect(bboxes.length).toBe(188);
    });

    test('Click selecting BBox', async () => {
      await browser.executeScript(() => { document.getElementsByClassName('sylTextRect-display')[0].dispatchEvent(new Event('mousedown')); });
      const resizeRectCount = (await browser.findElements(By.id('resizeRect'))).length;
      expect(resizeRectCount).toBe(1);
      const sylSelectedCount = (await browser.findElements(By.className('syl selected'))).length;
      expect(sylSelectedCount).toBe(1);
      const actions = browser.actions();
      await actions.sendKeys(Key.ESCAPE).perform();
    });

    test('Drag selecting BBoxes', async () => {
      const canvas = await browser.findElement(By.id('svg_group'));
      const actions = browser.actions();
      await actions.move({ origin: canvas }).press().move({ x: 500, y: 500 }).perform();
      await browser.findElements(By.id('selectRect'));
      await actions.release().perform();
      const selected = await browser.findElements(By.css('g.syl.selected'));
      expect(selected.length).toBeGreaterThan(0);
      const resizeRects = await browser.findElements(By.id('resizeRect'));
      expect(resizeRects.length).toBe(selected.length === 1 ? 1: 0);
      await actions.move({ origin: canvas }).press().release().perform();
    });

    /*test('Syl BBox highlighting features', async () => {
      await browser.executeScript(() => { document.getElementById('highlight-button').dispatchEvent(new Event('click')); });
      await browser.executeScript(() => { document.getElementById('highlight-syllable').dispatchEvent(new Event('click')); });
      await browser.executeScript(() => { document.getElementsByClassName('sylTextRect-display')[3].dispatchEvent(new Event('mousedown')); });
      const colorCount = (await browser.findElements(By.css('.sylTextRect-display[style="fill: rgb(86, 180, 233);"]'))).length;
      expect(colorCount).toBeGreaterThan(0);

      await browser.executeScript(() => { document.getElementsByClassName('sylTextRect-display')[2].dispatchEvent(new Event('mousedown')); });
      const newColorCount = (await browser.findElements(By.css('.sylTextRect-display[style="fill: rgb(86, 180, 233);"]'))).length;
      expect(newColorCount).toBe(colorCount - 1);
      const canvas = await browser.findElement(By.id('svg_group'));
      const actions = browser.actions();
      await actions.sendKeys(Key.ESCAPE).perform();
    });*/

    test('Syl BBox highlighting features', async () => {
      // Turn on syllable highlighting
      await browser.executeScript(() => { document.getElementById('highlight-button').dispatchEvent(new Event('click')); });
      await browser.executeScript(() => { document.getElementById('highlight-syllable').dispatchEvent(new Event('click')); });
      // Get some highlighted bbox
      const bbox = await browser.findElement(By.className('sylTextRect-display'));
      let bboxColor = await bbox.getCssValue('fill');
      const syllable = await bbox.findElement(By.xpath('./../..'));
      const syllableColor = await syllable.getCssValue('fill');
      expect(bboxColor).toEqual(syllableColor);

      // Check that it's red when highlighted
      const sylId = await bbox.findElement(By.xpath('./..')).getAttribute('id');
      await browser.sleep(2000);
      await browser.executeScript((id) => { document.getElementById(id).getElementsByTagName('rect')[0].dispatchEvent(new Event('mousedown')); }, sylId);
      await browser.wait(until.elementLocated(By.className('resizePoint')), 10000);
      bboxColor = await browser.findElement(By.id(sylId)).findElement(By.tagName('rect')).getCssValue('fill');
      expect(bboxColor).toEqual('rgb(221, 0, 0)');

      const actions = browser.actions();
      await actions.sendKeys(Key.ESCAPE).perform();
      await browser.wait(async () => {
        return (await browser.findElements(By.className('selected'))).length === 0;
      }, 2000);
    });

    test('Test selecting neumes while in bbox selecting mode', async () => {
      await browser.executeScript(() => { document.getElementsByClassName('nc')[0].children[0].dispatchEvent(new Event('mousedown')); });
      const selCount = (await browser.findElements(By.className('selected'))).length;
      expect(selCount).toBe(0);
      const canvas = await browser.findElement(By.id('svg_group'));
      const actions = browser.actions();
      await actions.move({ origin: canvas }).press().move({ x: 500, y: 500 }).perform();
      await browser.findElements(By.id('selectRect'));
      await actions.release().perform();
      const goodSelCount = (await browser.findElements(By.className('selected'))).length;
      expect(goodSelCount).toBeGreaterThan(0);
      const badSelCount = (await browser.findElements(By.css('.selected:not(.syl)'))).length;
      expect(badSelCount).toBe(0);
      await actions.sendKeys(Key.ESCAPE).perform();
    });
  });

  describe('Check Controls UI', () => {
    // Can't get viewBox from selenium for some reason so we can't check more than this
    test('Check Zoom Controls', async () => {
      const zoomSlider = await browser.findElement(By.id('zoomSlider'));
      const maxZoom = await zoomSlider.getAttribute('max');
      const actions = browser.actions();
      const rect = await zoomSlider.getRect();
      await actions.dragAndDrop(zoomSlider, { x: Math.round(rect.width / 2), y: 0 }).perform();
      let output = await browser.findElement(By.id('zoomOutput')).getText();
      expect(output).toBe(maxZoom);

      const zoomButton = await browser.findElement(By.id('reset-zoom'));
      await actions.click(zoomButton).perform();
      output = await browser.findElement(By.id('zoomOutput')).getText();
      expect(output).toBe('100');
    });

    test('Check Panning', async () => {
      const originalTransform = await browser.executeScript(() => { return document.getElementById('svg_group').getAttribute('viewBox'); });
      const actions = browser.actions();
      const svgGroup = await browser.findElement(By.id('svg_group'));
      await actions.keyDown(Key.SHIFT).dragAndDrop(svgGroup, { x: 50, y: 50 }).keyUp(Key.SHIFT).perform();
      const newTransform = await browser.executeScript(() => { return document.getElementById('svg_group').getAttribute('viewBox'); });

      const originalSplit = originalTransform.split(' ');
      const newSplit = newTransform.split(' ');
      expect(parseInt(originalSplit[0])).toBeGreaterThan(parseInt(newSplit[0]));
      expect(parseInt(originalSplit[1])).toBeGreaterThan(parseInt(newSplit[1]));
    });

    test('Check MEI Opacity Controls', async () => {
      const opacitySlider = await browser.findElement(By.id('opacitySlider'));
      const actions = browser.actions();
      const rect = await opacitySlider.getRect();
      await actions.dragAndDrop(opacitySlider, { x: -1 * parseInt(rect.width), y: 0 }).perform();
      let meiStyle = await browser.findElement(By.className('neon-container')).getAttribute('style');
      expect(meiStyle).toContain('opacity: 0;');

      const opacityButton = await browser.findElement(By.id('reset-opacity'));
      await actions.click(opacityButton).perform();
      meiStyle = await browser.findElement(By.className('neon-container')).getAttribute('style');
      expect(meiStyle).toContain('opacity: 1;');
    });

    test('Check Image Opacity Controls', async () => {
      const opacitySlider = await browser.findElement(By.id('bgOpacitySlider'));
      const actions = browser.actions();
      const rect = await opacitySlider.getRect();
      await actions.dragAndDrop(opacitySlider, { x: -1 * parseInt(rect.width), y: 0 }).perform();
      let imgStyle = await browser.findElement(By.id('bgimg')).getAttribute('style');
      expect(imgStyle).toContain('opacity: 0;');

      const opacityButton = await browser.findElement(By.id('reset-bg-opacity'));
      await actions.click(opacityButton).perform();
      imgStyle = await browser.findElement(By.id('bgimg')).getAttribute('style');
      expect(imgStyle).toContain('opacity: 1;');
    });

    /// TEST EDIT MODE ///
    describe('Edit Mode', () => {
      describe('Selection', () => {
        test('Test drag selection', async () => {
          if (title === 'firefox') {
            // Weird issues with dragging rect in Firefox.
            return;
          }
          const canvas = await browser.findElement(By.id('svg_group'));
          const actions = browser.actions();
          await actions.move({ origin: canvas }).press().move({ x: 200, y: 200 }).perform();
          await browser.wait(until.elementLocated(By.id('selectRect')), 10000);
          await browser.findElement(By.id('selectRect'));
          await actions.release().perform();
          await browser.findElement(By.className('selected'));
          const selected = await browser.findElements(By.className('selected'));
          expect(selected.length).toBeGreaterThan(0);
        });

        test('Test click select .nc', async () => {
          const selByNcButton = await browser.findElement(By.id('selByNc'));
          await browser.executeScript(() => { document.getElementById('selByNc').scrollIntoView(true); });
          const actions = browser.actions();
          await actions.click(selByNcButton).perform();
          const nc = await browser.findElement(By.className('nc'));
          await browser.executeScript((id) => { document.getElementById(id).children[0].dispatchEvent(new Event('mousedown')); }, (await nc.getAttribute('id')));
          const ncClass = await nc.getAttribute('class');
          expect(ncClass).toBe('nc selected');
          await actions.sendKeys(Key.ESCAPE).perform();
        });

        test('Click select syllable', async () => {
          const selBySylButton = await browser.findElement(By.id('selBySyl'));
          const actions = browser.actions();
          await actions.click(selBySylButton).perform();
          expect(await selBySylButton.getAttribute('class')).toContain('is-active');
          const syl = await browser.findElement(By.id('m-9eea945f-9acf-4f85-9dee-ce24fde486f1'));
          const sylNc = await syl.findElement(By.className('nc'));
          // await actions.click(sylNc).perform();
          await browser.executeScript((id) => { document.getElementById(id).children[0].dispatchEvent(new Event('mousedown')); }, (await sylNc.getAttribute('id')));
          const sylClass = await syl.getAttribute('class');
          expect(sylClass).toBe('syllable selected');
          await actions.sendKeys(Key.ESCAPE).perform();
        });

        test('Click select split syllable', async () => {
          const selBySylButton = await browser.findElement(By.id('selBySyl'));
          const actions = browser.actions();
          await actions.click(selBySylButton).perform();
          expect(await selBySylButton.getAttribute('class')).toContain('is-active');
          const firstHalf = await browser.findElement(By.id('m-eefa04b9-e43e-41a9-8d63-d5b093834442'));
          const secondHalf = await browser.findElement(By.id('m-23a8ef14-9b60-47dd-b072-fa2b6bc2e8bd'));
          const firstHalfNc = await firstHalf.findElement(By.className('nc'));
          await browser.executeScript((id) => { document.getElementById(id).children[0].dispatchEvent(new Event('mousedown')); }, (await firstHalfNc.getAttribute('id')));
          const firstHalfClass = await firstHalf.getAttribute('class');
          const secondHalfClass = await secondHalf.getAttribute('class');
          expect(firstHalfClass).toBe('syllable selected');
          expect(secondHalfClass).toBe('syllable selected');
          await actions.sendKeys(Key.ESCAPE).perform();
        });

        test('Click select neume', async () => {
          const selByNeumeButton = await browser.findElement(By.id('selByNeume'));
          const actions = browser.actions();
          await actions.click(selByNeumeButton).perform();
          expect(await selByNeumeButton.getAttribute('class')).toContain('is-active');
          const neume = await browser.findElement(By.className('neume'));
          const neumeNc = await neume.findElement(By.className('nc'));
          // await actions.click(neumeNc).perform();
          await browser.executeScript((id) => { document.getElementById(id).children[0].dispatchEvent(new Event('mousedown')); }, (await neumeNc.getAttribute('id')));
          const neumeClass = await neume.getAttribute('class');
          expect(neumeClass).toBe('neume selected');
          await actions.sendKeys(Key.ESCAPE).perform();
        });

        test('Click select staff', async () => {
          const selByStaff = await browser.findElement(By.id('selByStaff'));
          const actions = browser.actions();
          expect(await selByStaff.isDisplayed()).toBeTruthy();
          await browser.executeScript(() => { document.getElementById('selByStaff').scrollIntoView(true); });
          await actions.click(selByStaff).perform();
          expect(await selByStaff.getAttribute('class')).toContain('is-active');
          const staff = await browser.findElement(By.className('staff'));
          const nc = await staff.findElement(By.className('nc'));
          await browser.executeScript((id) => { document.getElementById(id).children[0].dispatchEvent(new Event('mousedown')); }, await nc.getAttribute('id'));
          const staffClass = await staff.getAttribute('class');
          expect(staffClass).toBe('staff selected');
          await actions.sendKeys(Key.ESCAPE).perform();
        });
      });

      test('Delete element', async () => {
        expect.assertions(1);
        const selBySylButton = await browser.findElement(By.id('selBySyl'));
        const actions = browser.actions();
        await actions.click(selBySylButton).perform();
        const syl = await browser.findElement(By.className('syllable'));
        const sylNc = await syl.findElement(By.className('nc'));
        const id = await sylNc.getAttribute('id');
        await browser.executeScript((id) => { document.getElementById(id).children[0].dispatchEvent(new Event('mousedown')); }, id);
        const deleteButton = await browser.findElement(By.id('delete'));
        await actions.click(deleteButton).perform();
        await browser.wait(until.stalenessOf(syl), 1000);
        return expect(browser.findElement(By.id(id))).rejects.toThrowError(error.NoSuchElementError);
      });

      test('Undo/Redo', async () => {
        const undoButton = await browser.findElement(By.id('undo'));
        const actions = browser.actions();
        let element = await browser.findElement(By.className('nc'));
        const origCount = (await browser.findElements(By.className('nc'))).length;
        await actions.click(undoButton).perform();
        await browser.wait(until.stalenessOf(element), 5000);
        let newCount = (await browser.findElements(By.className('nc'))).length;
        expect(newCount).toBeGreaterThan(origCount);
        element = browser.findElement(By.className('nc'));
        // await actions.click(redoButton).perform();
        await browser.executeScript(() => { document.getElementById('redo').dispatchEvent(new Event('click')); });
        await browser.wait(until.stalenessOf(element), 5000);
        newCount = (await browser.findElements(By.className('nc'))).length;
        expect(newCount).toEqual(origCount);
      });

      describe('Insert Test', () => {
        // Doesn't test location of insert, only that the handler works.
        test('Insert Punctum', async () => {
          const insertPunctum = await browser.findElement(By.id('punctum'));
          const ncCount = (await browser.findElements(By.className('nc'))).length;
          const someNc = await browser.findElement(By.className('nc'));
          await browser.executeScript((id) => { document.getElementById(id).scrollIntoView(true); }, (await someNc.getAttribute('id')));
          const isDisp = await insertPunctum.isDisplayed();
          expect(isDisp).toEqual(true);
          await insertPunctum.click();
          const clickedInsertPunctum = await browser.findElement(By.id('punctum'));
          const buttonClass = await clickedInsertPunctum.getAttribute('class');
          expect(buttonClass).toContain('is-active');
          // await browser.actions().move({ origin: someNc, x: 100, y: 100 }).click().perform();
          await browser.executeScript(() => { document.getElementById('svg_group').dispatchEvent(new MouseEvent('click', { bubbles: true })); });
          await browser.wait(until.stalenessOf(someNc), 5000);
          const newNcCount = (await browser.findElements(By.className('nc'))).length;
          expect(newNcCount).toBe(ncCount + 1);
        });

        test('Insert Pes', async () => {
          await browser.executeScript(() => { document.getElementById('groupingTab').dispatchEvent(new Event('click')); });
          const pesButton = await browser.findElement(By.id('pes'));
          await pesButton.click();
          // Get initial neume and nc counts
          const neumeCount = (await browser.findElements(By.className('neume'))).length;
          const ncCount = (await browser.findElements(By.className('nc'))).length;
          // Check that insert panel heading title is selected (check if bold)
          const insertHeader = await browser.findElement(By.id('insertMenu'));
          expect(await insertHeader.getCssValue('font-weight')).toMatch(/(700|bold)/);
          // Move mouse and click
          await browser.executeScript(() => { document.getElementById('svg_group').dispatchEvent(new MouseEvent('click', { bubbles: true })); });
          // Get new counts
          await browser.wait(async () => {
            const count = (await browser.findElements(By.className('neume'))).length;
            return count === neumeCount + 1;
          }, 2000);
          const newNcCount = (await browser.findElements(By.className('nc'))).length;
          // Compare
          expect(newNcCount).toBe(ncCount + 2);
        });
      });
    });
  });
});
