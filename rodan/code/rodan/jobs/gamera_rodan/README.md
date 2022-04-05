# gamera_rodan
Wrappers for Gamera tasks in Rodan.

While Rodan does come with functionality that auto-generates wrappers for Gamera, it is limited in that it will:

- exclude jobs that take image types as function arguments
- will fail in Rodan if the job is not pure Python (e.g. "TypeError: somemethod() takes no keyword arguments")
