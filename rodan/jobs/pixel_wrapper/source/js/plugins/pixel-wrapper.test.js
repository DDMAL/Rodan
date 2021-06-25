// jshint ignore:start

const {Builder, By, Key, until} = require('selenium-webdriver');
const firefox = require('selenium-webdriver/firefox');
// this is a Pixel.js job in Rodan
const url = 'http://localhost:9001/index_test.html';

jest.setTimeout('45000');

var browser = null;

beforeAll(async () => {
    // Set up the webdriver
    let options = new firefox.Options()
        .headless()
        .addArguments('--width=1920','--height=1200');
    browser = await new Builder()
        .forBrowser('firefox')
        .setFirefoxOptions(options)
        .build();

    await browser.get(url);
});

afterAll(() => {
    browser.quit();
});

describe('Checking Proper Plugin Creation', () => {
    test('page title matches (Pixel.js was loaded properly)', async () => {
        let title = await browser.getTitle();
        expect(title).toBe('Pixel.js');
    });

    var pluginIcon;
    test('plugin icon exists on the page', async () => {
        pluginIcon = await browser.wait(until.elementLocated(By.id('diva-1-pixel-icon-glyph')), 5000);
        expect(pluginIcon).toBeDefined();
    });

    test('activating plugin creates prompt for number of layers, input 2', async () => {
        // activate plugin
        const actions = browser.actions();
        await actions.click(pluginIcon).perform();

        // handle alert
        let alert = await browser.switchTo().alert();
        expect(await alert.getText()).toContain("How many layers will you classify?");
        // create 1 layer
        await alert.sendKeys('2');
        await alert.accept();
    });

    test('tutorial is created after the prompt is closed', async () => {
        // activate plugin
        const actions = browser.actions();
        await actions.click(pluginIcon).perform();

        let tutorialDiv = await browser.findElement(By.id('tutorial-div'));
        expect(await tutorialDiv.isDisplayed()).toBeTruthy();

        // close tutorial 
        await browser.sleep(500);
        let tutorialFooter = await browser.findElement(By.id('modal-footer'));
        await actions.click(tutorialFooter).perform();
    });

    test('the 2 layers were created properly (layer 2 selector is visible)', async () => {
        let layer2 = await browser.findElement(By.id('layer-2-selector'));
        expect(await layer2.isDisplayed()).toBeTruthy();
    });
});

describe('Checking Functionality', () => {
    test('selecting the brush tool creates brush-size slider', async () => {
        // expect to be hidden at first
        let brushSlider = await browser.findElement(By.id('brush-size'));
        let isVisible = await brushSlider.isDisplayed();
        expect(isVisible).toBeFalsy();

        // select on brush tool (b)
        const actions = browser.actions();
        await actions.keyDown(66).keyUp(66).perform();

        // expect to now be visible
        isVisible = await brushSlider.isDisplayed();
        expect(isVisible).toBeTruthy();
    });

    test('tooltip creates tooltip-text on mouse hover', async () => {
        let tooltip = await browser.findElement(By.className('tooltip'));
        let tooltipText = await browser.findElement(By.className('tooltiptext'));

        // should be hidden before hover
        expect(await tooltipText.isDisplayed()).toBeFalsy();

        // hover and should be visible
        const actions = browser.actions();
        await actions.click(tooltip).perform();
        await browser.sleep(1000); // time for opacity transition
        expect(await tooltipText.isDisplayed()).toBeTruthy();
    });

    test('clicking export as png button creates download links', async () => {
        // check for button
        let exportPNGButton = await browser.findElement(By.id('png-export-button'));
        expect(await exportPNGButton.isDisplayed()).toBeTruthy();

        // click on button
        const actions = browser.actions();
        await actions.click(exportPNGButton).perform();

        // links should now be visible
        let links = await browser.wait(until.elementLocated(By.id('png-links-div')), 1000);
        expect(await links.isEnabled()).toBeTruthy();
    });

    // next three tests are linked and use the submitButton variable    
    var submitButton;
    test('submit to rodan without selection regions creates alert', async () => {
        // click on button
        submitButton = await browser.findElement(By.id('rodan-export-button'));
        const actions = browser.actions();
        await actions.click(submitButton).perform();

        // check for alert
        let alert = await browser.switchTo().alert();
        expect(await alert.getText()).toBe("You haven't created any select regions!");
        await alert.accept();
    });
    test.skip('drawing select region then submit to rodan creates progress bar', async () => {
        let canvas = await browser.findElement(By.id('layer--1-canvas'));
        const actions = browser.actions();
        // select rectangle tool and draw one
        await actions.keyDown(82).keyUp(82).perform();
        await actions.dragAndDrop(canvas, {x: 300, y: 300}).perform();

        await actions.click(submitButton).perform();
        // progress bar should be visible
        await browser.sleep(1000);
        let progressBar = await browser.findElement(By.id('pbar-inner-div'));
        expect(await progressBar.isDisplayed()).toBeTruthy();
    });
    test.skip('cancel progress bar button removes the progress div', async () => {
        let cancelButton = await browser.findElement(By.id('cancel-export-div'));
        const actions = browser.actions();
        await actions.click(cancelButton).perform();

        await browser.sleep(1000);
        expect(await browser.findElements(By.id('pixel-export-div'))).toEqual([]); // empty list since not found
    });

    test('layer 1 activation toggle changes its class to deactivated', async () => {
        let layer1Toggle = await browser.findElement(By.id('layer-1-activation'));
        expect(await layer1Toggle.getAttribute('class')).toBe('layer-activated');

        const actions = browser.actions();
        await actions.click(layer1Toggle).perform();

        expect(await layer1Toggle.getAttribute('class')).toBe('layer-deactivated');
    });
});
