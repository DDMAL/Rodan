# MEI Encoding Rodan Job

Encodes the output from Pitch Finding into an [MEI](http://music-encoding.org/) file, as a job in the workflow builder [```Rodan```](https://github.com/DDMAL/Rodan). Requires a matching MEI mapping CSV that associates glyphs with snippets of MEI, created with the [`MEI Mapping Tool`](https://github.com/DDMAL/mei-mapping-tool).

Can take additional JSON input from Text Alignment, so that textual information will be included in the MEI and the neumes will be correctly partitioned into syllables. If this input is not present the output will still be valid MEI, just with "blank" syllables.

Can also take addition JSON input from Column Splitting which contains the dimensions of the original image, and where the splits were made. In Rodan, multi column folios are cut and stacked so all systems are on top of one another. This is necessary for heuristic pitch finding, staff finding, and text alignment. However, the mei file should have all bounding box information for where things were on the original image. Mei encoding will move all the bounding boxes back if given column splitting data.

**Currently uses Python 3**
xml.etree has replaced LibMEI in this job.

This job uses state machines to handle the logic of when syllables should be made, ended, and when glyphs should be added to the inside or outside of syllables. state_machine.excalidraw is a diagram for the state machine used to build MEI files, and test_state_machine.excalidraw is a diagram for the state machine used to validate MEI files. Excalidraw files can be viewed through the excalidraw VS code extension, or the website.
