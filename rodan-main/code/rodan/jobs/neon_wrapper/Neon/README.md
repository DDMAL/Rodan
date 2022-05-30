Neon v4.1.0
=====
[![Build_Status](https://travis-ci.org/DDMAL/Neon.svg?branch=master)](https://travis-ci.org/DDMAL/Neon)
[![License: MIT](https://img.shields.io/github/license/DDMAL/Neon)](https://opensource.org/licenses/MIT)
[![dependencies Status](https://david-dm.org/DDMAL/Neon/status.svg)](https://david-dm.org/DDMAL/Neon)
[![devDependencies Status](https://david-dm.org/DDMAL/Neon/dev-status.svg)](https://david-dm.org/DDMAL/Neon?type=dev)

**N**eume **E**ditor **ON**line.


Neon is a browser-based music notation editor written in JavaScript using the Verovio music engraving library. The editor can be used to manipulate digitally encoded early musical scores in square-note notation.


Neon is a re-write of [Neon.JS](https://github.com/DDMAL/Neon.js) using a modified version of [Verovio](https://github.com/DDMAL/verovio) to render MEI-Neume files according to the MEI 4.0 specifications.

Requirements
------------
 * [yarn](https://yarnpkg.com/en/docs/install):
    * `brew install yarn` on Mac

Setup
-----

1. Install the dependencies using yarn:
```
yarn install
```

2. Build webpack:
```
yarn build
```

3. Start the server:
```
yarn start
```

4. Access the page at: <http://localhost:8080>.


Instructions
-----------

Neon has two main modes: viewer and editor. To learn how to use both, [read the instructions on our wiki.](https://github.com/DDMAL/Neon/wiki/Instructions)

Test
----

Follow the instructions from above first. The tests for Neon use [Selenium](https://docs.seleniumhq.org/) and use Firefox, Safari, and Chrome. Their respective webdrivers are required. Safari 12 or greater is required. On Mac, Firefox and Chrome can be installed by:
```shell
brew cask install firefox
brew cask install google-chrome
brew install geckodriver
brew cask install chromedriver
```
Then you can run the tests locally using `yarn test`. We use [jest](https://facebook.github.io/jest/) to script our tests.

*These tests require the server to be running on `localhost:8080`*

Verovio
-------

Verovio is present as an npm package under `verovio-util/verovio-dev` with the name `verovio-dev`. Its contents come from the `emscripten/npm-dev` folder in a Verovio project folder.
