print "Loading gamera modules"
from rodan.jobs.gamera import binarization
binarization.load_module()

from rodan.jobs.gamera import threshold
threshold.load_module()

from rodan.jobs.gamera import image_conversion
image_conversion.load_module()

from rodan.jobs.gamera import transformation
transformation.load_module()

try:
    from rodan.jobs.gamera.toolkits import border_removal
    border_removal.load_module()
except ImportError as e:
    print "No Border Removal Toolkit Installed. Skipping."

try:
    from rodan.jobs.gamera.toolkits import staff_removal
    staff_removal.load_module()
except ImportError as e:
    print "No Staff Removal Toolkit Installed. Skipping."

try:
    from rodan.jobs.gamera.toolkits import background_estimation
    background_estimation.load_module()
except ImportError as e:
    print "No Background Estimation Toolkit Installed. Skipping."

try:
    from rodan.jobs.gamera.toolkits import lyric_extraction
    lyric_extraction.load_module()
except ImportError as e:
    print "No Lyric Extraction Toolkit Installed. Skipping."

try:
    from rodan.jobs.gamera.toolkits import musicstaves
    musicstaves.load_module()
except ImportError as e:
    print "No Music Staves Toolkit Installed. Skipping."
