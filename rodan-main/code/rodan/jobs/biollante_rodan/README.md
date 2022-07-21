# Biollante Rodan

This is [Gamera's](https://gamera.informatik.hsnr.de/) genetic algorithm optimizer for kNN classifiers ([Biollante](https://gamera.informatik.hsnr.de/docs/gamera-docs/ga_optimization.html#user-interface-biollante)) adapted for use in [Rodan](http://ddmal.music.mcgill.ca/Rodan/).

This is a work in progress.

## UPDATE FOR RUNNING IN PYTHON3
- Python3 does not convert between JSON objects and bytes automatically. Thus, you have to use encode and decode manually. 
- I created a function to sort a list of dictionaries for the settings of celery jobs. 
- Biollante now works in python3.
- For more information regarding how gamera runs in python3 you can refer to Rodan/rodan-main/code/rodan/jobs/gamera_rodan/gamera-rodan-Py3doc.md


## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
