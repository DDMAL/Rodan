import sys
from gamera.core import load_image, init_gamera
from gamera import gamera_xml

from StaffFinding import StaffFinder
from PitchFinding import PitchFinder

import json

init_gamera()

if __name__ == "__main__":
    # given CC and a staff image, will generate a complete JSOMR file

    (tmp, inCC, inImage) = sys.argv

    image = load_image(inImage)
    glyphs = gamera_xml.glyphs_from_xml(inCC)
    kwargs = {
        'lines_per_staff': 4,
        'staff_finder': 0,
        'binarization': 1,
        'interpolation': True,

        'discard_size': 12,
    }

    sf = StaffFinder(**kwargs)
    pf = PitchFinder(**kwargs)

    page = sf.get_page_properties(image)
    staves = sf.get_staves(image)
    pitches = pf.get_pitches(glyphs, staves)

    jsomr = {
        'page': page,
        'staves': staves,
        'glyphs': pitches,
    }

    with open('jsomr_output.json', 'w') as f:
        f.write(json.dumps(jsomr))
        # print jsomr
