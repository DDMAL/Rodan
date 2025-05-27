import RodanDashboardView from 'views/RodanDashboard/RodanDashboardView';
var Backbone = require('backbone');

var dashboard = new RodanDashboardView({
    model: new Backbone.Model({
        previewImage: undefined,
        glyphDictionary: {},
        classNames: [],
        trainingGlyphs: {}
    })
});

beforeAll(() =>
{
    dashboard.initialize();
});

test('Counts cannot be negative', function ()
{
    expect(dashboard.classifierCount).toBeGreaterThanOrEqual(0);
    expect(dashboard.pageCount).toBeGreaterThanOrEqual(0);
    expect(dashboard.selectedCount).toBeGreaterThanOrEqual(0);
});

test('All regions must be rendered', function ()
{
    expect(dashboard.classCreateRegion).toBeTruthy();
    expect(dashboard.glyphTreeRegion).toBeTruthy();
    expect(dashboard.glyphTableRegion).toBeTruthy();
    expect(dashboard.classifierTableRegion).toBeTruthy();
    expect(dashboard.glyphEditRegion).toBeTruthy();
    expect(dashboard.pagePreviewRegion).toBeTruthy();
    expect(dashboard.modalTestRegion).toBeTruthy();
});
