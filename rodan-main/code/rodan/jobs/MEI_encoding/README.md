# MEI Encoding Rodan Job

Encodes the output from [`Pitch Finding`](https://github.com/DDMAL/heuristic-pitch-finding) into an [MEI](http://music-encoding.org/) file, as a job in the workflow builder [```Rodan```](https://github.com/DDMAL/Rodan). Requires a matching MEI mapping CSV that associates glyphs with snippets of MEI, created with the [`MEI Mapping Tool`](https://github.com/DDMAL/mei-mapping-tool).

Can take additional JSON input from [Text Alignment](https://github.com/DDMAL/text-alignment), so that textual information will be included in the MEI and the neumes will be correctly partitioned into syllables. If this input is not present the output will still be valid MEI, just with "blank" syllables.

**Updated to Python 3**. Requires numpy>=1.16.0. Scripts requiring PIL>=6.1.0 are in ```visualize_alignment.py``` for local development.
