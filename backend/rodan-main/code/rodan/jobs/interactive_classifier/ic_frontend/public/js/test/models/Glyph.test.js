import Glyph from "models/Glyph";
import ClassNameUtils from "utils/ClassNameUtils";

var glyph = new Glyph();

beforeAll(() =>
{
    glyph.onCreate();
});

describe('Attributes are valid after change', function ()
{
    glyph.changeClass("");
    glyph.renameGlyph("UNCLASSIFIED");
    var confidence = glyph.get("confidence");
    var name = glyph.get("class_name");
    name = ClassNameUtils.sanitizeClassName(name);
    it('Confidence is between 0 and 1', function()
    {
        expect(confidence).toBeGreaterThanOrEqual(0) &&
          confidence.toBeLessThanOrEqual(1);
    });
    it('Class name is valid', function ()
    {
        console.log(name);
        expect(name).not.toMatch("unclassified") && name.not.toMatch("");
    })
});

test('Reset attributes after unclassifying', function ()
{
    glyph.unclassify();
    expect(glyph.get("confidence")).toBe(0);
    expect(glyph.get("class_name")).toMatch("UNCLASSIFIED");
    expect(glyph.get("id_state_manual")).toBe(false);
});
