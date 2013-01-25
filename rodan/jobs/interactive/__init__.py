print "Loading rodan interactive jobs"
from rodan.jobs.interactive.despeckle import despeckle
despeckle.load_interactive_job()

from rodan.jobs.interactive.crop import crop
crop.load_interactive_job()
