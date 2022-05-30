# neon-wrapper
Rodan wrapper for [Neon](https://github.com/DDMAL/Neon)

# Setup

Since this is a Rodan job, the first step is to set up and install [rodan-docker](https://github.com/DDMAL/rodan-docker). After that, clone this repository into
the `jobs` folder of `rodan-docker`
```
git clone --recurse-submodules https://github.com/DDMAL/neon-wrapper
```

Neon2 is a submodule of this and tracks the develop branch. To update this, run
```
git submodule update --remote
```
from the root of `neon-wrapper`.

Replace all instances of `demojob` with `neon-wrapper` in `jobs/settings.py` and `docker-compose.job-dev.yml`. For more information, refer to the setup for `rodan-docker`.

# Building Neon

You need to use webpack to build Neon. Ensure you have [Yarn](https://yarnpkg.com) installed first. Run
```
yarn install
yarn build
```
before trying to access Neon in Rodan.
