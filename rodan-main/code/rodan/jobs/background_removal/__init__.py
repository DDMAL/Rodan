__version__ = "1.0.0"

# Told rodan to load module here!
from rodan.jobs import module_loader
module_loader('rodan.jobs.background_removal.BgRemovalRodan')