/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 0);
/******/ })
/************************************************************************/
/******/ ({

/***/ "./node_modules/array.prototype.fill/index.js":
/*!****************************************************!*\
  !*** ./node_modules/array.prototype.fill/index.js ***!
  \****************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


(function () {
  if (Array.prototype.fill) return;

  var fill = function fill(value) {
    // Steps 1-2.
    if (this == null) {
      throw new TypeError("this is null or not defined");
    }

    var O = Object(this);

    // Steps 3-5.
    var len = O.length >>> 0;

    // Steps 6-7.
    var start = arguments[1];
    var relativeStart = start >> 0;

    // Step 8.
    var k = relativeStart < 0 ? Math.max(len + relativeStart, 0) : Math.min(relativeStart, len);

    // Steps 9-10.
    var end = arguments[2];
    var relativeEnd = end === undefined ? len : end >> 0;

    // Step 11.
    var last = relativeEnd < 0 ? Math.max(len + relativeEnd, 0) : Math.min(relativeEnd, len);

    // Step 12.
    while (k < last) {
      O[k] = value;
      k++;
    }

    // Step 13.
    return O;
  };

  if (Object.defineProperty) {
    try {
      Object.defineProperty(Array.prototype, 'fill', {
        value: fill,
        configurable: true,
        enumerable: false,
        writable: true
      });
    } catch (e) {}
  }

  if (!Array.prototype.fill) {
    Array.prototype.fill = fill;
  }
})(undefined);

/***/ }),

/***/ "./node_modules/debug/src/browser.js":
/*!*******************************************!*\
  !*** ./node_modules/debug/src/browser.js ***!
  \*******************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
/* WEBPACK VAR INJECTION */(function(process) {

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

/**
 * This is the web browser implementation of `debug()`.
 *
 * Expose `debug()` as the module.
 */

exports = module.exports = __webpack_require__(/*! ./debug */ "./node_modules/debug/src/debug.js");
exports.log = log;
exports.formatArgs = formatArgs;
exports.save = save;
exports.load = load;
exports.useColors = useColors;
exports.storage = 'undefined' != typeof chrome && 'undefined' != typeof chrome.storage ? chrome.storage.local : localstorage();

/**
 * Colors.
 */

exports.colors = ['#0000CC', '#0000FF', '#0033CC', '#0033FF', '#0066CC', '#0066FF', '#0099CC', '#0099FF', '#00CC00', '#00CC33', '#00CC66', '#00CC99', '#00CCCC', '#00CCFF', '#3300CC', '#3300FF', '#3333CC', '#3333FF', '#3366CC', '#3366FF', '#3399CC', '#3399FF', '#33CC00', '#33CC33', '#33CC66', '#33CC99', '#33CCCC', '#33CCFF', '#6600CC', '#6600FF', '#6633CC', '#6633FF', '#66CC00', '#66CC33', '#9900CC', '#9900FF', '#9933CC', '#9933FF', '#99CC00', '#99CC33', '#CC0000', '#CC0033', '#CC0066', '#CC0099', '#CC00CC', '#CC00FF', '#CC3300', '#CC3333', '#CC3366', '#CC3399', '#CC33CC', '#CC33FF', '#CC6600', '#CC6633', '#CC9900', '#CC9933', '#CCCC00', '#CCCC33', '#FF0000', '#FF0033', '#FF0066', '#FF0099', '#FF00CC', '#FF00FF', '#FF3300', '#FF3333', '#FF3366', '#FF3399', '#FF33CC', '#FF33FF', '#FF6600', '#FF6633', '#FF9900', '#FF9933', '#FFCC00', '#FFCC33'];

/**
 * Currently only WebKit-based Web Inspectors, Firefox >= v31,
 * and the Firebug extension (any Firefox version) are known
 * to support "%c" CSS customizations.
 *
 * TODO: add a `localStorage` variable to explicitly enable/disable colors
 */

function useColors() {
  // NB: In an Electron preload script, document will be defined but not fully
  // initialized. Since we know we're in Chrome, we'll just detect this case
  // explicitly
  if (typeof window !== 'undefined' && window.process && window.process.type === 'renderer') {
    return true;
  }

  // Internet Explorer and Edge do not support colors.
  if (typeof navigator !== 'undefined' && navigator.userAgent && navigator.userAgent.toLowerCase().match(/(edge|trident)\/(\d+)/)) {
    return false;
  }

  // is webkit? http://stackoverflow.com/a/16459606/376773
  // document is undefined in react-native: https://github.com/facebook/react-native/pull/1632
  return typeof document !== 'undefined' && document.documentElement && document.documentElement.style && document.documentElement.style.WebkitAppearance ||
  // is firebug? http://stackoverflow.com/a/398120/376773
  typeof window !== 'undefined' && window.console && (window.console.firebug || window.console.exception && window.console.table) ||
  // is firefox >= v31?
  // https://developer.mozilla.org/en-US/docs/Tools/Web_Console#Styling_messages
  typeof navigator !== 'undefined' && navigator.userAgent && navigator.userAgent.toLowerCase().match(/firefox\/(\d+)/) && parseInt(RegExp.$1, 10) >= 31 ||
  // double check webkit in userAgent just in case we are in a worker
  typeof navigator !== 'undefined' && navigator.userAgent && navigator.userAgent.toLowerCase().match(/applewebkit\/(\d+)/);
}

/**
 * Map %j to `JSON.stringify()`, since no Web Inspectors do that by default.
 */

exports.formatters.j = function (v) {
  try {
    return JSON.stringify(v);
  } catch (err) {
    return '[UnexpectedJSONParseError]: ' + err.message;
  }
};

/**
 * Colorize log arguments if enabled.
 *
 * @api public
 */

function formatArgs(args) {
  var useColors = this.useColors;

  args[0] = (useColors ? '%c' : '') + this.namespace + (useColors ? ' %c' : ' ') + args[0] + (useColors ? '%c ' : ' ') + '+' + exports.humanize(this.diff);

  if (!useColors) return;

  var c = 'color: ' + this.color;
  args.splice(1, 0, c, 'color: inherit');

  // the final "%c" is somewhat tricky, because there could be other
  // arguments passed either before or after the %c, so we need to
  // figure out the correct index to insert the CSS into
  var index = 0;
  var lastC = 0;
  args[0].replace(/%[a-zA-Z%]/g, function (match) {
    if ('%%' === match) return;
    index++;
    if ('%c' === match) {
      // we only are interested in the *last* %c
      // (the user may have provided their own)
      lastC = index;
    }
  });

  args.splice(lastC, 0, c);
}

/**
 * Invokes `console.log()` when available.
 * No-op when `console.log` is not a "function".
 *
 * @api public
 */

function log() {
  // this hackery is required for IE8/9, where
  // the `console.log` function doesn't have 'apply'
  return 'object' === (typeof console === 'undefined' ? 'undefined' : _typeof(console)) && console.log && Function.prototype.apply.call(console.log, console, arguments);
}

/**
 * Save `namespaces`.
 *
 * @param {String} namespaces
 * @api private
 */

function save(namespaces) {
  try {
    if (null == namespaces) {
      exports.storage.removeItem('debug');
    } else {
      exports.storage.debug = namespaces;
    }
  } catch (e) {}
}

/**
 * Load `namespaces`.
 *
 * @return {String} returns the previously persisted debug modes
 * @api private
 */

function load() {
  var r;
  try {
    r = exports.storage.debug;
  } catch (e) {}

  // If debug isn't set in LS, and we're in Electron, try to load $DEBUG
  if (!r && typeof process !== 'undefined' && 'env' in process) {
    r = process.env.DEBUG;
  }

  return r;
}

/**
 * Enable namespaces listed in `localStorage.debug` initially.
 */

exports.enable(load());

/**
 * Localstorage attempts to return the localstorage.
 *
 * This is necessary because safari throws
 * when a user disables cookies/localstorage
 * and you attempt to access it.
 *
 * @return {LocalStorage}
 * @api private
 */

function localstorage() {
  try {
    return window.localStorage;
  } catch (e) {}
}
/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__(/*! ./../../process/browser.js */ "./node_modules/process/browser.js")))

/***/ }),

/***/ "./node_modules/debug/src/debug.js":
/*!*****************************************!*\
  !*** ./node_modules/debug/src/debug.js ***!
  \*****************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


/**
 * This is the common logic for both the Node.js and web browser
 * implementations of `debug()`.
 *
 * Expose `debug()` as the module.
 */

exports = module.exports = createDebug.debug = createDebug['default'] = createDebug;
exports.coerce = coerce;
exports.disable = disable;
exports.enable = enable;
exports.enabled = enabled;
exports.humanize = __webpack_require__(/*! ms */ "./node_modules/ms/index.js");

/**
 * Active `debug` instances.
 */
exports.instances = [];

/**
 * The currently active debug mode names, and names to skip.
 */

exports.names = [];
exports.skips = [];

/**
 * Map of special "%n" handling functions, for the debug "format" argument.
 *
 * Valid key names are a single, lower or upper-case letter, i.e. "n" and "N".
 */

exports.formatters = {};

/**
 * Select a color.
 * @param {String} namespace
 * @return {Number}
 * @api private
 */

function selectColor(namespace) {
  var hash = 0,
      i;

  for (i in namespace) {
    hash = (hash << 5) - hash + namespace.charCodeAt(i);
    hash |= 0; // Convert to 32bit integer
  }

  return exports.colors[Math.abs(hash) % exports.colors.length];
}

/**
 * Create a debugger with the given `namespace`.
 *
 * @param {String} namespace
 * @return {Function}
 * @api public
 */

function createDebug(namespace) {

  var prevTime;

  function debug() {
    // disabled?
    if (!debug.enabled) return;

    var self = debug;

    // set `diff` timestamp
    var curr = +new Date();
    var ms = curr - (prevTime || curr);
    self.diff = ms;
    self.prev = prevTime;
    self.curr = curr;
    prevTime = curr;

    // turn the `arguments` into a proper Array
    var args = new Array(arguments.length);
    for (var i = 0; i < args.length; i++) {
      args[i] = arguments[i];
    }

    args[0] = exports.coerce(args[0]);

    if ('string' !== typeof args[0]) {
      // anything else let's inspect with %O
      args.unshift('%O');
    }

    // apply any `formatters` transformations
    var index = 0;
    args[0] = args[0].replace(/%([a-zA-Z%])/g, function (match, format) {
      // if we encounter an escaped % then don't increase the array index
      if (match === '%%') return match;
      index++;
      var formatter = exports.formatters[format];
      if ('function' === typeof formatter) {
        var val = args[index];
        match = formatter.call(self, val);

        // now we need to remove `args[index]` since it's inlined in the `format`
        args.splice(index, 1);
        index--;
      }
      return match;
    });

    // apply env-specific formatting (colors, etc.)
    exports.formatArgs.call(self, args);

    var logFn = debug.log || exports.log || console.log.bind(console);
    logFn.apply(self, args);
  }

  debug.namespace = namespace;
  debug.enabled = exports.enabled(namespace);
  debug.useColors = exports.useColors();
  debug.color = selectColor(namespace);
  debug.destroy = destroy;

  // env-specific initialization logic for debug instances
  if ('function' === typeof exports.init) {
    exports.init(debug);
  }

  exports.instances.push(debug);

  return debug;
}

function destroy() {
  var index = exports.instances.indexOf(this);
  if (index !== -1) {
    exports.instances.splice(index, 1);
    return true;
  } else {
    return false;
  }
}

/**
 * Enables a debug mode by namespaces. This can include modes
 * separated by a colon and wildcards.
 *
 * @param {String} namespaces
 * @api public
 */

function enable(namespaces) {
  exports.save(namespaces);

  exports.names = [];
  exports.skips = [];

  var i;
  var split = (typeof namespaces === 'string' ? namespaces : '').split(/[\s,]+/);
  var len = split.length;

  for (i = 0; i < len; i++) {
    if (!split[i]) continue; // ignore empty strings
    namespaces = split[i].replace(/\*/g, '.*?');
    if (namespaces[0] === '-') {
      exports.skips.push(new RegExp('^' + namespaces.substr(1) + '$'));
    } else {
      exports.names.push(new RegExp('^' + namespaces + '$'));
    }
  }

  for (i = 0; i < exports.instances.length; i++) {
    var instance = exports.instances[i];
    instance.enabled = exports.enabled(instance.namespace);
  }
}

/**
 * Disable debug output.
 *
 * @api public
 */

function disable() {
  exports.enable('');
}

/**
 * Returns true if the given mode name is enabled, false otherwise.
 *
 * @param {String} name
 * @return {Boolean}
 * @api public
 */

function enabled(name) {
  if (name[name.length - 1] === '*') {
    return true;
  }
  var i, len;
  for (i = 0, len = exports.skips.length; i < len; i++) {
    if (exports.skips[i].test(name)) {
      return false;
    }
  }
  for (i = 0, len = exports.names.length; i < len; i++) {
    if (exports.names[i].test(name)) {
      return true;
    }
  }
  return false;
}

/**
 * Coerce `val`.
 *
 * @param {Mixed} val
 * @return {Mixed}
 * @api private
 */

function coerce(val) {
  if (val instanceof Error) return val.stack || val.message;
  return val;
}

/***/ }),

/***/ "./node_modules/lodash.maxby/index.js":
/*!********************************************!*\
  !*** ./node_modules/lodash.maxby/index.js ***!
  \********************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
/* WEBPACK VAR INJECTION */(function(global, module) {

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

/**
 * lodash (Custom Build) <https://lodash.com/>
 * Build: `lodash modularize exports="npm" -o ./`
 * Copyright jQuery Foundation and other contributors <https://jquery.org/>
 * Released under MIT license <https://lodash.com/license>
 * Based on Underscore.js 1.8.3 <http://underscorejs.org/LICENSE>
 * Copyright Jeremy Ashkenas, DocumentCloud and Investigative Reporters & Editors
 */

/** Used as the size to enable large array optimizations. */
var LARGE_ARRAY_SIZE = 200;

/** Used as the `TypeError` message for "Functions" methods. */
var FUNC_ERROR_TEXT = 'Expected a function';

/** Used to stand-in for `undefined` hash values. */
var HASH_UNDEFINED = '__lodash_hash_undefined__';

/** Used to compose bitmasks for comparison styles. */
var UNORDERED_COMPARE_FLAG = 1,
    PARTIAL_COMPARE_FLAG = 2;

/** Used as references for various `Number` constants. */
var INFINITY = 1 / 0,
    MAX_SAFE_INTEGER = 9007199254740991;

/** `Object#toString` result references. */
var argsTag = '[object Arguments]',
    arrayTag = '[object Array]',
    boolTag = '[object Boolean]',
    dateTag = '[object Date]',
    errorTag = '[object Error]',
    funcTag = '[object Function]',
    genTag = '[object GeneratorFunction]',
    mapTag = '[object Map]',
    numberTag = '[object Number]',
    objectTag = '[object Object]',
    promiseTag = '[object Promise]',
    regexpTag = '[object RegExp]',
    setTag = '[object Set]',
    stringTag = '[object String]',
    symbolTag = '[object Symbol]',
    weakMapTag = '[object WeakMap]';

var arrayBufferTag = '[object ArrayBuffer]',
    dataViewTag = '[object DataView]',
    float32Tag = '[object Float32Array]',
    float64Tag = '[object Float64Array]',
    int8Tag = '[object Int8Array]',
    int16Tag = '[object Int16Array]',
    int32Tag = '[object Int32Array]',
    uint8Tag = '[object Uint8Array]',
    uint8ClampedTag = '[object Uint8ClampedArray]',
    uint16Tag = '[object Uint16Array]',
    uint32Tag = '[object Uint32Array]';

/** Used to match property names within property paths. */
var reIsDeepProp = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,
    reIsPlainProp = /^\w*$/,
    reLeadingDot = /^\./,
    rePropName = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g;

/**
 * Used to match `RegExp`
 * [syntax characters](http://ecma-international.org/ecma-262/7.0/#sec-patterns).
 */
var reRegExpChar = /[\\^$.*+?()[\]{}|]/g;

/** Used to match backslashes in property paths. */
var reEscapeChar = /\\(\\)?/g;

/** Used to detect host constructors (Safari). */
var reIsHostCtor = /^\[object .+?Constructor\]$/;

/** Used to detect unsigned integer values. */
var reIsUint = /^(?:0|[1-9]\d*)$/;

/** Used to identify `toStringTag` values of typed arrays. */
var typedArrayTags = {};
typedArrayTags[float32Tag] = typedArrayTags[float64Tag] = typedArrayTags[int8Tag] = typedArrayTags[int16Tag] = typedArrayTags[int32Tag] = typedArrayTags[uint8Tag] = typedArrayTags[uint8ClampedTag] = typedArrayTags[uint16Tag] = typedArrayTags[uint32Tag] = true;
typedArrayTags[argsTag] = typedArrayTags[arrayTag] = typedArrayTags[arrayBufferTag] = typedArrayTags[boolTag] = typedArrayTags[dataViewTag] = typedArrayTags[dateTag] = typedArrayTags[errorTag] = typedArrayTags[funcTag] = typedArrayTags[mapTag] = typedArrayTags[numberTag] = typedArrayTags[objectTag] = typedArrayTags[regexpTag] = typedArrayTags[setTag] = typedArrayTags[stringTag] = typedArrayTags[weakMapTag] = false;

/** Detect free variable `global` from Node.js. */
var freeGlobal = (typeof global === 'undefined' ? 'undefined' : _typeof(global)) == 'object' && global && global.Object === Object && global;

/** Detect free variable `self`. */
var freeSelf = (typeof self === 'undefined' ? 'undefined' : _typeof(self)) == 'object' && self && self.Object === Object && self;

/** Used as a reference to the global object. */
var root = freeGlobal || freeSelf || Function('return this')();

/** Detect free variable `exports`. */
var freeExports = ( false ? undefined : _typeof(exports)) == 'object' && exports && !exports.nodeType && exports;

/** Detect free variable `module`. */
var freeModule = freeExports && ( false ? undefined : _typeof(module)) == 'object' && module && !module.nodeType && module;

/** Detect the popular CommonJS extension `module.exports`. */
var moduleExports = freeModule && freeModule.exports === freeExports;

/** Detect free variable `process` from Node.js. */
var freeProcess = moduleExports && freeGlobal.process;

/** Used to access faster Node.js helpers. */
var nodeUtil = function () {
  try {
    return freeProcess && freeProcess.binding('util');
  } catch (e) {}
}();

/* Node.js helper references. */
var nodeIsTypedArray = nodeUtil && nodeUtil.isTypedArray;

/**
 * A specialized version of `_.some` for arrays without support for iteratee
 * shorthands.
 *
 * @private
 * @param {Array} [array] The array to iterate over.
 * @param {Function} predicate The function invoked per iteration.
 * @returns {boolean} Returns `true` if any element passes the predicate check,
 *  else `false`.
 */
function arraySome(array, predicate) {
  var index = -1,
      length = array ? array.length : 0;

  while (++index < length) {
    if (predicate(array[index], index, array)) {
      return true;
    }
  }
  return false;
}

/**
 * The base implementation of `_.property` without support for deep paths.
 *
 * @private
 * @param {string} key The key of the property to get.
 * @returns {Function} Returns the new accessor function.
 */
function baseProperty(key) {
  return function (object) {
    return object == null ? undefined : object[key];
  };
}

/**
 * The base implementation of `_.times` without support for iteratee shorthands
 * or max array length checks.
 *
 * @private
 * @param {number} n The number of times to invoke `iteratee`.
 * @param {Function} iteratee The function invoked per iteration.
 * @returns {Array} Returns the array of results.
 */
function baseTimes(n, iteratee) {
  var index = -1,
      result = Array(n);

  while (++index < n) {
    result[index] = iteratee(index);
  }
  return result;
}

/**
 * The base implementation of `_.unary` without support for storing metadata.
 *
 * @private
 * @param {Function} func The function to cap arguments for.
 * @returns {Function} Returns the new capped function.
 */
function baseUnary(func) {
  return function (value) {
    return func(value);
  };
}

/**
 * Gets the value at `key` of `object`.
 *
 * @private
 * @param {Object} [object] The object to query.
 * @param {string} key The key of the property to get.
 * @returns {*} Returns the property value.
 */
function getValue(object, key) {
  return object == null ? undefined : object[key];
}

/**
 * Checks if `value` is a host object in IE < 9.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a host object, else `false`.
 */
function isHostObject(value) {
  // Many host objects are `Object` objects that can coerce to strings
  // despite having improperly defined `toString` methods.
  var result = false;
  if (value != null && typeof value.toString != 'function') {
    try {
      result = !!(value + '');
    } catch (e) {}
  }
  return result;
}

/**
 * Converts `map` to its key-value pairs.
 *
 * @private
 * @param {Object} map The map to convert.
 * @returns {Array} Returns the key-value pairs.
 */
function mapToArray(map) {
  var index = -1,
      result = Array(map.size);

  map.forEach(function (value, key) {
    result[++index] = [key, value];
  });
  return result;
}

/**
 * Creates a unary function that invokes `func` with its argument transformed.
 *
 * @private
 * @param {Function} func The function to wrap.
 * @param {Function} transform The argument transform.
 * @returns {Function} Returns the new function.
 */
function overArg(func, transform) {
  return function (arg) {
    return func(transform(arg));
  };
}

/**
 * Converts `set` to an array of its values.
 *
 * @private
 * @param {Object} set The set to convert.
 * @returns {Array} Returns the values.
 */
function setToArray(set) {
  var index = -1,
      result = Array(set.size);

  set.forEach(function (value) {
    result[++index] = value;
  });
  return result;
}

/** Used for built-in method references. */
var arrayProto = Array.prototype,
    funcProto = Function.prototype,
    objectProto = Object.prototype;

/** Used to detect overreaching core-js shims. */
var coreJsData = root['__core-js_shared__'];

/** Used to detect methods masquerading as native. */
var maskSrcKey = function () {
  var uid = /[^.]+$/.exec(coreJsData && coreJsData.keys && coreJsData.keys.IE_PROTO || '');
  return uid ? 'Symbol(src)_1.' + uid : '';
}();

/** Used to resolve the decompiled source of functions. */
var funcToString = funcProto.toString;

/** Used to check objects for own properties. */
var hasOwnProperty = objectProto.hasOwnProperty;

/**
 * Used to resolve the
 * [`toStringTag`](http://ecma-international.org/ecma-262/7.0/#sec-object.prototype.tostring)
 * of values.
 */
var objectToString = objectProto.toString;

/** Used to detect if a method is native. */
var reIsNative = RegExp('^' + funcToString.call(hasOwnProperty).replace(reRegExpChar, '\\$&').replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, '$1.*?') + '$');

/** Built-in value references. */
var _Symbol = root.Symbol,
    Uint8Array = root.Uint8Array,
    propertyIsEnumerable = objectProto.propertyIsEnumerable,
    splice = arrayProto.splice;

/* Built-in method references for those with the same name as other `lodash` methods. */
var nativeKeys = overArg(Object.keys, Object);

/* Built-in method references that are verified to be native. */
var DataView = getNative(root, 'DataView'),
    Map = getNative(root, 'Map'),
    Promise = getNative(root, 'Promise'),
    Set = getNative(root, 'Set'),
    WeakMap = getNative(root, 'WeakMap'),
    nativeCreate = getNative(Object, 'create');

/** Used to detect maps, sets, and weakmaps. */
var dataViewCtorString = toSource(DataView),
    mapCtorString = toSource(Map),
    promiseCtorString = toSource(Promise),
    setCtorString = toSource(Set),
    weakMapCtorString = toSource(WeakMap);

/** Used to convert symbols to primitives and strings. */
var symbolProto = _Symbol ? _Symbol.prototype : undefined,
    symbolValueOf = symbolProto ? symbolProto.valueOf : undefined,
    symbolToString = symbolProto ? symbolProto.toString : undefined;

/**
 * Creates a hash object.
 *
 * @private
 * @constructor
 * @param {Array} [entries] The key-value pairs to cache.
 */
function Hash(entries) {
  var index = -1,
      length = entries ? entries.length : 0;

  this.clear();
  while (++index < length) {
    var entry = entries[index];
    this.set(entry[0], entry[1]);
  }
}

/**
 * Removes all key-value entries from the hash.
 *
 * @private
 * @name clear
 * @memberOf Hash
 */
function hashClear() {
  this.__data__ = nativeCreate ? nativeCreate(null) : {};
}

/**
 * Removes `key` and its value from the hash.
 *
 * @private
 * @name delete
 * @memberOf Hash
 * @param {Object} hash The hash to modify.
 * @param {string} key The key of the value to remove.
 * @returns {boolean} Returns `true` if the entry was removed, else `false`.
 */
function hashDelete(key) {
  return this.has(key) && delete this.__data__[key];
}

/**
 * Gets the hash value for `key`.
 *
 * @private
 * @name get
 * @memberOf Hash
 * @param {string} key The key of the value to get.
 * @returns {*} Returns the entry value.
 */
function hashGet(key) {
  var data = this.__data__;
  if (nativeCreate) {
    var result = data[key];
    return result === HASH_UNDEFINED ? undefined : result;
  }
  return hasOwnProperty.call(data, key) ? data[key] : undefined;
}

/**
 * Checks if a hash value for `key` exists.
 *
 * @private
 * @name has
 * @memberOf Hash
 * @param {string} key The key of the entry to check.
 * @returns {boolean} Returns `true` if an entry for `key` exists, else `false`.
 */
function hashHas(key) {
  var data = this.__data__;
  return nativeCreate ? data[key] !== undefined : hasOwnProperty.call(data, key);
}

/**
 * Sets the hash `key` to `value`.
 *
 * @private
 * @name set
 * @memberOf Hash
 * @param {string} key The key of the value to set.
 * @param {*} value The value to set.
 * @returns {Object} Returns the hash instance.
 */
function hashSet(key, value) {
  var data = this.__data__;
  data[key] = nativeCreate && value === undefined ? HASH_UNDEFINED : value;
  return this;
}

// Add methods to `Hash`.
Hash.prototype.clear = hashClear;
Hash.prototype['delete'] = hashDelete;
Hash.prototype.get = hashGet;
Hash.prototype.has = hashHas;
Hash.prototype.set = hashSet;

/**
 * Creates an list cache object.
 *
 * @private
 * @constructor
 * @param {Array} [entries] The key-value pairs to cache.
 */
function ListCache(entries) {
  var index = -1,
      length = entries ? entries.length : 0;

  this.clear();
  while (++index < length) {
    var entry = entries[index];
    this.set(entry[0], entry[1]);
  }
}

/**
 * Removes all key-value entries from the list cache.
 *
 * @private
 * @name clear
 * @memberOf ListCache
 */
function listCacheClear() {
  this.__data__ = [];
}

/**
 * Removes `key` and its value from the list cache.
 *
 * @private
 * @name delete
 * @memberOf ListCache
 * @param {string} key The key of the value to remove.
 * @returns {boolean} Returns `true` if the entry was removed, else `false`.
 */
function listCacheDelete(key) {
  var data = this.__data__,
      index = assocIndexOf(data, key);

  if (index < 0) {
    return false;
  }
  var lastIndex = data.length - 1;
  if (index == lastIndex) {
    data.pop();
  } else {
    splice.call(data, index, 1);
  }
  return true;
}

/**
 * Gets the list cache value for `key`.
 *
 * @private
 * @name get
 * @memberOf ListCache
 * @param {string} key The key of the value to get.
 * @returns {*} Returns the entry value.
 */
function listCacheGet(key) {
  var data = this.__data__,
      index = assocIndexOf(data, key);

  return index < 0 ? undefined : data[index][1];
}

/**
 * Checks if a list cache value for `key` exists.
 *
 * @private
 * @name has
 * @memberOf ListCache
 * @param {string} key The key of the entry to check.
 * @returns {boolean} Returns `true` if an entry for `key` exists, else `false`.
 */
function listCacheHas(key) {
  return assocIndexOf(this.__data__, key) > -1;
}

/**
 * Sets the list cache `key` to `value`.
 *
 * @private
 * @name set
 * @memberOf ListCache
 * @param {string} key The key of the value to set.
 * @param {*} value The value to set.
 * @returns {Object} Returns the list cache instance.
 */
function listCacheSet(key, value) {
  var data = this.__data__,
      index = assocIndexOf(data, key);

  if (index < 0) {
    data.push([key, value]);
  } else {
    data[index][1] = value;
  }
  return this;
}

// Add methods to `ListCache`.
ListCache.prototype.clear = listCacheClear;
ListCache.prototype['delete'] = listCacheDelete;
ListCache.prototype.get = listCacheGet;
ListCache.prototype.has = listCacheHas;
ListCache.prototype.set = listCacheSet;

/**
 * Creates a map cache object to store key-value pairs.
 *
 * @private
 * @constructor
 * @param {Array} [entries] The key-value pairs to cache.
 */
function MapCache(entries) {
  var index = -1,
      length = entries ? entries.length : 0;

  this.clear();
  while (++index < length) {
    var entry = entries[index];
    this.set(entry[0], entry[1]);
  }
}

/**
 * Removes all key-value entries from the map.
 *
 * @private
 * @name clear
 * @memberOf MapCache
 */
function mapCacheClear() {
  this.__data__ = {
    'hash': new Hash(),
    'map': new (Map || ListCache)(),
    'string': new Hash()
  };
}

/**
 * Removes `key` and its value from the map.
 *
 * @private
 * @name delete
 * @memberOf MapCache
 * @param {string} key The key of the value to remove.
 * @returns {boolean} Returns `true` if the entry was removed, else `false`.
 */
function mapCacheDelete(key) {
  return getMapData(this, key)['delete'](key);
}

/**
 * Gets the map value for `key`.
 *
 * @private
 * @name get
 * @memberOf MapCache
 * @param {string} key The key of the value to get.
 * @returns {*} Returns the entry value.
 */
function mapCacheGet(key) {
  return getMapData(this, key).get(key);
}

/**
 * Checks if a map value for `key` exists.
 *
 * @private
 * @name has
 * @memberOf MapCache
 * @param {string} key The key of the entry to check.
 * @returns {boolean} Returns `true` if an entry for `key` exists, else `false`.
 */
function mapCacheHas(key) {
  return getMapData(this, key).has(key);
}

/**
 * Sets the map `key` to `value`.
 *
 * @private
 * @name set
 * @memberOf MapCache
 * @param {string} key The key of the value to set.
 * @param {*} value The value to set.
 * @returns {Object} Returns the map cache instance.
 */
function mapCacheSet(key, value) {
  getMapData(this, key).set(key, value);
  return this;
}

// Add methods to `MapCache`.
MapCache.prototype.clear = mapCacheClear;
MapCache.prototype['delete'] = mapCacheDelete;
MapCache.prototype.get = mapCacheGet;
MapCache.prototype.has = mapCacheHas;
MapCache.prototype.set = mapCacheSet;

/**
 *
 * Creates an array cache object to store unique values.
 *
 * @private
 * @constructor
 * @param {Array} [values] The values to cache.
 */
function SetCache(values) {
  var index = -1,
      length = values ? values.length : 0;

  this.__data__ = new MapCache();
  while (++index < length) {
    this.add(values[index]);
  }
}

/**
 * Adds `value` to the array cache.
 *
 * @private
 * @name add
 * @memberOf SetCache
 * @alias push
 * @param {*} value The value to cache.
 * @returns {Object} Returns the cache instance.
 */
function setCacheAdd(value) {
  this.__data__.set(value, HASH_UNDEFINED);
  return this;
}

/**
 * Checks if `value` is in the array cache.
 *
 * @private
 * @name has
 * @memberOf SetCache
 * @param {*} value The value to search for.
 * @returns {number} Returns `true` if `value` is found, else `false`.
 */
function setCacheHas(value) {
  return this.__data__.has(value);
}

// Add methods to `SetCache`.
SetCache.prototype.add = SetCache.prototype.push = setCacheAdd;
SetCache.prototype.has = setCacheHas;

/**
 * Creates a stack cache object to store key-value pairs.
 *
 * @private
 * @constructor
 * @param {Array} [entries] The key-value pairs to cache.
 */
function Stack(entries) {
  this.__data__ = new ListCache(entries);
}

/**
 * Removes all key-value entries from the stack.
 *
 * @private
 * @name clear
 * @memberOf Stack
 */
function stackClear() {
  this.__data__ = new ListCache();
}

/**
 * Removes `key` and its value from the stack.
 *
 * @private
 * @name delete
 * @memberOf Stack
 * @param {string} key The key of the value to remove.
 * @returns {boolean} Returns `true` if the entry was removed, else `false`.
 */
function stackDelete(key) {
  return this.__data__['delete'](key);
}

/**
 * Gets the stack value for `key`.
 *
 * @private
 * @name get
 * @memberOf Stack
 * @param {string} key The key of the value to get.
 * @returns {*} Returns the entry value.
 */
function stackGet(key) {
  return this.__data__.get(key);
}

/**
 * Checks if a stack value for `key` exists.
 *
 * @private
 * @name has
 * @memberOf Stack
 * @param {string} key The key of the entry to check.
 * @returns {boolean} Returns `true` if an entry for `key` exists, else `false`.
 */
function stackHas(key) {
  return this.__data__.has(key);
}

/**
 * Sets the stack `key` to `value`.
 *
 * @private
 * @name set
 * @memberOf Stack
 * @param {string} key The key of the value to set.
 * @param {*} value The value to set.
 * @returns {Object} Returns the stack cache instance.
 */
function stackSet(key, value) {
  var cache = this.__data__;
  if (cache instanceof ListCache) {
    var pairs = cache.__data__;
    if (!Map || pairs.length < LARGE_ARRAY_SIZE - 1) {
      pairs.push([key, value]);
      return this;
    }
    cache = this.__data__ = new MapCache(pairs);
  }
  cache.set(key, value);
  return this;
}

// Add methods to `Stack`.
Stack.prototype.clear = stackClear;
Stack.prototype['delete'] = stackDelete;
Stack.prototype.get = stackGet;
Stack.prototype.has = stackHas;
Stack.prototype.set = stackSet;

/**
 * Creates an array of the enumerable property names of the array-like `value`.
 *
 * @private
 * @param {*} value The value to query.
 * @param {boolean} inherited Specify returning inherited property names.
 * @returns {Array} Returns the array of property names.
 */
function arrayLikeKeys(value, inherited) {
  // Safari 8.1 makes `arguments.callee` enumerable in strict mode.
  // Safari 9 makes `arguments.length` enumerable in strict mode.
  var result = isArray(value) || isArguments(value) ? baseTimes(value.length, String) : [];

  var length = result.length,
      skipIndexes = !!length;

  for (var key in value) {
    if ((inherited || hasOwnProperty.call(value, key)) && !(skipIndexes && (key == 'length' || isIndex(key, length)))) {
      result.push(key);
    }
  }
  return result;
}

/**
 * Gets the index at which the `key` is found in `array` of key-value pairs.
 *
 * @private
 * @param {Array} array The array to inspect.
 * @param {*} key The key to search for.
 * @returns {number} Returns the index of the matched value, else `-1`.
 */
function assocIndexOf(array, key) {
  var length = array.length;
  while (length--) {
    if (eq(array[length][0], key)) {
      return length;
    }
  }
  return -1;
}

/**
 * The base implementation of methods like `_.max` and `_.min` which accepts a
 * `comparator` to determine the extremum value.
 *
 * @private
 * @param {Array} array The array to iterate over.
 * @param {Function} iteratee The iteratee invoked per iteration.
 * @param {Function} comparator The comparator used to compare values.
 * @returns {*} Returns the extremum value.
 */
function baseExtremum(array, iteratee, comparator) {
  var index = -1,
      length = array.length;

  while (++index < length) {
    var value = array[index],
        current = iteratee(value);

    if (current != null && (computed === undefined ? current === current && !isSymbol(current) : comparator(current, computed))) {
      var computed = current,
          result = value;
    }
  }
  return result;
}

/**
 * The base implementation of `_.get` without support for default values.
 *
 * @private
 * @param {Object} object The object to query.
 * @param {Array|string} path The path of the property to get.
 * @returns {*} Returns the resolved value.
 */
function baseGet(object, path) {
  path = isKey(path, object) ? [path] : castPath(path);

  var index = 0,
      length = path.length;

  while (object != null && index < length) {
    object = object[toKey(path[index++])];
  }
  return index && index == length ? object : undefined;
}

/**
 * The base implementation of `getTag`.
 *
 * @private
 * @param {*} value The value to query.
 * @returns {string} Returns the `toStringTag`.
 */
function baseGetTag(value) {
  return objectToString.call(value);
}

/**
 * The base implementation of `_.gt` which doesn't coerce arguments.
 *
 * @private
 * @param {*} value The value to compare.
 * @param {*} other The other value to compare.
 * @returns {boolean} Returns `true` if `value` is greater than `other`,
 *  else `false`.
 */
function baseGt(value, other) {
  return value > other;
}

/**
 * The base implementation of `_.hasIn` without support for deep paths.
 *
 * @private
 * @param {Object} [object] The object to query.
 * @param {Array|string} key The key to check.
 * @returns {boolean} Returns `true` if `key` exists, else `false`.
 */
function baseHasIn(object, key) {
  return object != null && key in Object(object);
}

/**
 * The base implementation of `_.isEqual` which supports partial comparisons
 * and tracks traversed objects.
 *
 * @private
 * @param {*} value The value to compare.
 * @param {*} other The other value to compare.
 * @param {Function} [customizer] The function to customize comparisons.
 * @param {boolean} [bitmask] The bitmask of comparison flags.
 *  The bitmask may be composed of the following flags:
 *     1 - Unordered comparison
 *     2 - Partial comparison
 * @param {Object} [stack] Tracks traversed `value` and `other` objects.
 * @returns {boolean} Returns `true` if the values are equivalent, else `false`.
 */
function baseIsEqual(value, other, customizer, bitmask, stack) {
  if (value === other) {
    return true;
  }
  if (value == null || other == null || !isObject(value) && !isObjectLike(other)) {
    return value !== value && other !== other;
  }
  return baseIsEqualDeep(value, other, baseIsEqual, customizer, bitmask, stack);
}

/**
 * A specialized version of `baseIsEqual` for arrays and objects which performs
 * deep comparisons and tracks traversed objects enabling objects with circular
 * references to be compared.
 *
 * @private
 * @param {Object} object The object to compare.
 * @param {Object} other The other object to compare.
 * @param {Function} equalFunc The function to determine equivalents of values.
 * @param {Function} [customizer] The function to customize comparisons.
 * @param {number} [bitmask] The bitmask of comparison flags. See `baseIsEqual`
 *  for more details.
 * @param {Object} [stack] Tracks traversed `object` and `other` objects.
 * @returns {boolean} Returns `true` if the objects are equivalent, else `false`.
 */
function baseIsEqualDeep(object, other, equalFunc, customizer, bitmask, stack) {
  var objIsArr = isArray(object),
      othIsArr = isArray(other),
      objTag = arrayTag,
      othTag = arrayTag;

  if (!objIsArr) {
    objTag = getTag(object);
    objTag = objTag == argsTag ? objectTag : objTag;
  }
  if (!othIsArr) {
    othTag = getTag(other);
    othTag = othTag == argsTag ? objectTag : othTag;
  }
  var objIsObj = objTag == objectTag && !isHostObject(object),
      othIsObj = othTag == objectTag && !isHostObject(other),
      isSameTag = objTag == othTag;

  if (isSameTag && !objIsObj) {
    stack || (stack = new Stack());
    return objIsArr || isTypedArray(object) ? equalArrays(object, other, equalFunc, customizer, bitmask, stack) : equalByTag(object, other, objTag, equalFunc, customizer, bitmask, stack);
  }
  if (!(bitmask & PARTIAL_COMPARE_FLAG)) {
    var objIsWrapped = objIsObj && hasOwnProperty.call(object, '__wrapped__'),
        othIsWrapped = othIsObj && hasOwnProperty.call(other, '__wrapped__');

    if (objIsWrapped || othIsWrapped) {
      var objUnwrapped = objIsWrapped ? object.value() : object,
          othUnwrapped = othIsWrapped ? other.value() : other;

      stack || (stack = new Stack());
      return equalFunc(objUnwrapped, othUnwrapped, customizer, bitmask, stack);
    }
  }
  if (!isSameTag) {
    return false;
  }
  stack || (stack = new Stack());
  return equalObjects(object, other, equalFunc, customizer, bitmask, stack);
}

/**
 * The base implementation of `_.isMatch` without support for iteratee shorthands.
 *
 * @private
 * @param {Object} object The object to inspect.
 * @param {Object} source The object of property values to match.
 * @param {Array} matchData The property names, values, and compare flags to match.
 * @param {Function} [customizer] The function to customize comparisons.
 * @returns {boolean} Returns `true` if `object` is a match, else `false`.
 */
function baseIsMatch(object, source, matchData, customizer) {
  var index = matchData.length,
      length = index,
      noCustomizer = !customizer;

  if (object == null) {
    return !length;
  }
  object = Object(object);
  while (index--) {
    var data = matchData[index];
    if (noCustomizer && data[2] ? data[1] !== object[data[0]] : !(data[0] in object)) {
      return false;
    }
  }
  while (++index < length) {
    data = matchData[index];
    var key = data[0],
        objValue = object[key],
        srcValue = data[1];

    if (noCustomizer && data[2]) {
      if (objValue === undefined && !(key in object)) {
        return false;
      }
    } else {
      var stack = new Stack();
      if (customizer) {
        var result = customizer(objValue, srcValue, key, object, source, stack);
      }
      if (!(result === undefined ? baseIsEqual(srcValue, objValue, customizer, UNORDERED_COMPARE_FLAG | PARTIAL_COMPARE_FLAG, stack) : result)) {
        return false;
      }
    }
  }
  return true;
}

/**
 * The base implementation of `_.isNative` without bad shim checks.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a native function,
 *  else `false`.
 */
function baseIsNative(value) {
  if (!isObject(value) || isMasked(value)) {
    return false;
  }
  var pattern = isFunction(value) || isHostObject(value) ? reIsNative : reIsHostCtor;
  return pattern.test(toSource(value));
}

/**
 * The base implementation of `_.isTypedArray` without Node.js optimizations.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a typed array, else `false`.
 */
function baseIsTypedArray(value) {
  return isObjectLike(value) && isLength(value.length) && !!typedArrayTags[objectToString.call(value)];
}

/**
 * The base implementation of `_.iteratee`.
 *
 * @private
 * @param {*} [value=_.identity] The value to convert to an iteratee.
 * @returns {Function} Returns the iteratee.
 */
function baseIteratee(value) {
  // Don't store the `typeof` result in a variable to avoid a JIT bug in Safari 9.
  // See https://bugs.webkit.org/show_bug.cgi?id=156034 for more details.
  if (typeof value == 'function') {
    return value;
  }
  if (value == null) {
    return identity;
  }
  if ((typeof value === 'undefined' ? 'undefined' : _typeof(value)) == 'object') {
    return isArray(value) ? baseMatchesProperty(value[0], value[1]) : baseMatches(value);
  }
  return property(value);
}

/**
 * The base implementation of `_.keys` which doesn't treat sparse arrays as dense.
 *
 * @private
 * @param {Object} object The object to query.
 * @returns {Array} Returns the array of property names.
 */
function baseKeys(object) {
  if (!isPrototype(object)) {
    return nativeKeys(object);
  }
  var result = [];
  for (var key in Object(object)) {
    if (hasOwnProperty.call(object, key) && key != 'constructor') {
      result.push(key);
    }
  }
  return result;
}

/**
 * The base implementation of `_.matches` which doesn't clone `source`.
 *
 * @private
 * @param {Object} source The object of property values to match.
 * @returns {Function} Returns the new spec function.
 */
function baseMatches(source) {
  var matchData = getMatchData(source);
  if (matchData.length == 1 && matchData[0][2]) {
    return matchesStrictComparable(matchData[0][0], matchData[0][1]);
  }
  return function (object) {
    return object === source || baseIsMatch(object, source, matchData);
  };
}

/**
 * The base implementation of `_.matchesProperty` which doesn't clone `srcValue`.
 *
 * @private
 * @param {string} path The path of the property to get.
 * @param {*} srcValue The value to match.
 * @returns {Function} Returns the new spec function.
 */
function baseMatchesProperty(path, srcValue) {
  if (isKey(path) && isStrictComparable(srcValue)) {
    return matchesStrictComparable(toKey(path), srcValue);
  }
  return function (object) {
    var objValue = get(object, path);
    return objValue === undefined && objValue === srcValue ? hasIn(object, path) : baseIsEqual(srcValue, objValue, undefined, UNORDERED_COMPARE_FLAG | PARTIAL_COMPARE_FLAG);
  };
}

/**
 * A specialized version of `baseProperty` which supports deep paths.
 *
 * @private
 * @param {Array|string} path The path of the property to get.
 * @returns {Function} Returns the new accessor function.
 */
function basePropertyDeep(path) {
  return function (object) {
    return baseGet(object, path);
  };
}

/**
 * The base implementation of `_.toString` which doesn't convert nullish
 * values to empty strings.
 *
 * @private
 * @param {*} value The value to process.
 * @returns {string} Returns the string.
 */
function baseToString(value) {
  // Exit early for strings to avoid a performance hit in some environments.
  if (typeof value == 'string') {
    return value;
  }
  if (isSymbol(value)) {
    return symbolToString ? symbolToString.call(value) : '';
  }
  var result = value + '';
  return result == '0' && 1 / value == -INFINITY ? '-0' : result;
}

/**
 * Casts `value` to a path array if it's not one.
 *
 * @private
 * @param {*} value The value to inspect.
 * @returns {Array} Returns the cast property path array.
 */
function castPath(value) {
  return isArray(value) ? value : stringToPath(value);
}

/**
 * A specialized version of `baseIsEqualDeep` for arrays with support for
 * partial deep comparisons.
 *
 * @private
 * @param {Array} array The array to compare.
 * @param {Array} other The other array to compare.
 * @param {Function} equalFunc The function to determine equivalents of values.
 * @param {Function} customizer The function to customize comparisons.
 * @param {number} bitmask The bitmask of comparison flags. See `baseIsEqual`
 *  for more details.
 * @param {Object} stack Tracks traversed `array` and `other` objects.
 * @returns {boolean} Returns `true` if the arrays are equivalent, else `false`.
 */
function equalArrays(array, other, equalFunc, customizer, bitmask, stack) {
  var isPartial = bitmask & PARTIAL_COMPARE_FLAG,
      arrLength = array.length,
      othLength = other.length;

  if (arrLength != othLength && !(isPartial && othLength > arrLength)) {
    return false;
  }
  // Assume cyclic values are equal.
  var stacked = stack.get(array);
  if (stacked && stack.get(other)) {
    return stacked == other;
  }
  var index = -1,
      result = true,
      seen = bitmask & UNORDERED_COMPARE_FLAG ? new SetCache() : undefined;

  stack.set(array, other);
  stack.set(other, array);

  // Ignore non-index properties.
  while (++index < arrLength) {
    var arrValue = array[index],
        othValue = other[index];

    if (customizer) {
      var compared = isPartial ? customizer(othValue, arrValue, index, other, array, stack) : customizer(arrValue, othValue, index, array, other, stack);
    }
    if (compared !== undefined) {
      if (compared) {
        continue;
      }
      result = false;
      break;
    }
    // Recursively compare arrays (susceptible to call stack limits).
    if (seen) {
      if (!arraySome(other, function (othValue, othIndex) {
        if (!seen.has(othIndex) && (arrValue === othValue || equalFunc(arrValue, othValue, customizer, bitmask, stack))) {
          return seen.add(othIndex);
        }
      })) {
        result = false;
        break;
      }
    } else if (!(arrValue === othValue || equalFunc(arrValue, othValue, customizer, bitmask, stack))) {
      result = false;
      break;
    }
  }
  stack['delete'](array);
  stack['delete'](other);
  return result;
}

/**
 * A specialized version of `baseIsEqualDeep` for comparing objects of
 * the same `toStringTag`.
 *
 * **Note:** This function only supports comparing values with tags of
 * `Boolean`, `Date`, `Error`, `Number`, `RegExp`, or `String`.
 *
 * @private
 * @param {Object} object The object to compare.
 * @param {Object} other The other object to compare.
 * @param {string} tag The `toStringTag` of the objects to compare.
 * @param {Function} equalFunc The function to determine equivalents of values.
 * @param {Function} customizer The function to customize comparisons.
 * @param {number} bitmask The bitmask of comparison flags. See `baseIsEqual`
 *  for more details.
 * @param {Object} stack Tracks traversed `object` and `other` objects.
 * @returns {boolean} Returns `true` if the objects are equivalent, else `false`.
 */
function equalByTag(object, other, tag, equalFunc, customizer, bitmask, stack) {
  switch (tag) {
    case dataViewTag:
      if (object.byteLength != other.byteLength || object.byteOffset != other.byteOffset) {
        return false;
      }
      object = object.buffer;
      other = other.buffer;

    case arrayBufferTag:
      if (object.byteLength != other.byteLength || !equalFunc(new Uint8Array(object), new Uint8Array(other))) {
        return false;
      }
      return true;

    case boolTag:
    case dateTag:
    case numberTag:
      // Coerce booleans to `1` or `0` and dates to milliseconds.
      // Invalid dates are coerced to `NaN`.
      return eq(+object, +other);

    case errorTag:
      return object.name == other.name && object.message == other.message;

    case regexpTag:
    case stringTag:
      // Coerce regexes to strings and treat strings, primitives and objects,
      // as equal. See http://www.ecma-international.org/ecma-262/7.0/#sec-regexp.prototype.tostring
      // for more details.
      return object == other + '';

    case mapTag:
      var convert = mapToArray;

    case setTag:
      var isPartial = bitmask & PARTIAL_COMPARE_FLAG;
      convert || (convert = setToArray);

      if (object.size != other.size && !isPartial) {
        return false;
      }
      // Assume cyclic values are equal.
      var stacked = stack.get(object);
      if (stacked) {
        return stacked == other;
      }
      bitmask |= UNORDERED_COMPARE_FLAG;

      // Recursively compare objects (susceptible to call stack limits).
      stack.set(object, other);
      var result = equalArrays(convert(object), convert(other), equalFunc, customizer, bitmask, stack);
      stack['delete'](object);
      return result;

    case symbolTag:
      if (symbolValueOf) {
        return symbolValueOf.call(object) == symbolValueOf.call(other);
      }
  }
  return false;
}

/**
 * A specialized version of `baseIsEqualDeep` for objects with support for
 * partial deep comparisons.
 *
 * @private
 * @param {Object} object The object to compare.
 * @param {Object} other The other object to compare.
 * @param {Function} equalFunc The function to determine equivalents of values.
 * @param {Function} customizer The function to customize comparisons.
 * @param {number} bitmask The bitmask of comparison flags. See `baseIsEqual`
 *  for more details.
 * @param {Object} stack Tracks traversed `object` and `other` objects.
 * @returns {boolean} Returns `true` if the objects are equivalent, else `false`.
 */
function equalObjects(object, other, equalFunc, customizer, bitmask, stack) {
  var isPartial = bitmask & PARTIAL_COMPARE_FLAG,
      objProps = keys(object),
      objLength = objProps.length,
      othProps = keys(other),
      othLength = othProps.length;

  if (objLength != othLength && !isPartial) {
    return false;
  }
  var index = objLength;
  while (index--) {
    var key = objProps[index];
    if (!(isPartial ? key in other : hasOwnProperty.call(other, key))) {
      return false;
    }
  }
  // Assume cyclic values are equal.
  var stacked = stack.get(object);
  if (stacked && stack.get(other)) {
    return stacked == other;
  }
  var result = true;
  stack.set(object, other);
  stack.set(other, object);

  var skipCtor = isPartial;
  while (++index < objLength) {
    key = objProps[index];
    var objValue = object[key],
        othValue = other[key];

    if (customizer) {
      var compared = isPartial ? customizer(othValue, objValue, key, other, object, stack) : customizer(objValue, othValue, key, object, other, stack);
    }
    // Recursively compare objects (susceptible to call stack limits).
    if (!(compared === undefined ? objValue === othValue || equalFunc(objValue, othValue, customizer, bitmask, stack) : compared)) {
      result = false;
      break;
    }
    skipCtor || (skipCtor = key == 'constructor');
  }
  if (result && !skipCtor) {
    var objCtor = object.constructor,
        othCtor = other.constructor;

    // Non `Object` object instances with different constructors are not equal.
    if (objCtor != othCtor && 'constructor' in object && 'constructor' in other && !(typeof objCtor == 'function' && objCtor instanceof objCtor && typeof othCtor == 'function' && othCtor instanceof othCtor)) {
      result = false;
    }
  }
  stack['delete'](object);
  stack['delete'](other);
  return result;
}

/**
 * Gets the data for `map`.
 *
 * @private
 * @param {Object} map The map to query.
 * @param {string} key The reference key.
 * @returns {*} Returns the map data.
 */
function getMapData(map, key) {
  var data = map.__data__;
  return isKeyable(key) ? data[typeof key == 'string' ? 'string' : 'hash'] : data.map;
}

/**
 * Gets the property names, values, and compare flags of `object`.
 *
 * @private
 * @param {Object} object The object to query.
 * @returns {Array} Returns the match data of `object`.
 */
function getMatchData(object) {
  var result = keys(object),
      length = result.length;

  while (length--) {
    var key = result[length],
        value = object[key];

    result[length] = [key, value, isStrictComparable(value)];
  }
  return result;
}

/**
 * Gets the native function at `key` of `object`.
 *
 * @private
 * @param {Object} object The object to query.
 * @param {string} key The key of the method to get.
 * @returns {*} Returns the function if it's native, else `undefined`.
 */
function getNative(object, key) {
  var value = getValue(object, key);
  return baseIsNative(value) ? value : undefined;
}

/**
 * Gets the `toStringTag` of `value`.
 *
 * @private
 * @param {*} value The value to query.
 * @returns {string} Returns the `toStringTag`.
 */
var getTag = baseGetTag;

// Fallback for data views, maps, sets, and weak maps in IE 11,
// for data views in Edge < 14, and promises in Node.js.
if (DataView && getTag(new DataView(new ArrayBuffer(1))) != dataViewTag || Map && getTag(new Map()) != mapTag || Promise && getTag(Promise.resolve()) != promiseTag || Set && getTag(new Set()) != setTag || WeakMap && getTag(new WeakMap()) != weakMapTag) {
  getTag = function getTag(value) {
    var result = objectToString.call(value),
        Ctor = result == objectTag ? value.constructor : undefined,
        ctorString = Ctor ? toSource(Ctor) : undefined;

    if (ctorString) {
      switch (ctorString) {
        case dataViewCtorString:
          return dataViewTag;
        case mapCtorString:
          return mapTag;
        case promiseCtorString:
          return promiseTag;
        case setCtorString:
          return setTag;
        case weakMapCtorString:
          return weakMapTag;
      }
    }
    return result;
  };
}

/**
 * Checks if `path` exists on `object`.
 *
 * @private
 * @param {Object} object The object to query.
 * @param {Array|string} path The path to check.
 * @param {Function} hasFunc The function to check properties.
 * @returns {boolean} Returns `true` if `path` exists, else `false`.
 */
function hasPath(object, path, hasFunc) {
  path = isKey(path, object) ? [path] : castPath(path);

  var result,
      index = -1,
      length = path.length;

  while (++index < length) {
    var key = toKey(path[index]);
    if (!(result = object != null && hasFunc(object, key))) {
      break;
    }
    object = object[key];
  }
  if (result) {
    return result;
  }
  var length = object ? object.length : 0;
  return !!length && isLength(length) && isIndex(key, length) && (isArray(object) || isArguments(object));
}

/**
 * Checks if `value` is a valid array-like index.
 *
 * @private
 * @param {*} value The value to check.
 * @param {number} [length=MAX_SAFE_INTEGER] The upper bounds of a valid index.
 * @returns {boolean} Returns `true` if `value` is a valid index, else `false`.
 */
function isIndex(value, length) {
  length = length == null ? MAX_SAFE_INTEGER : length;
  return !!length && (typeof value == 'number' || reIsUint.test(value)) && value > -1 && value % 1 == 0 && value < length;
}

/**
 * Checks if `value` is a property name and not a property path.
 *
 * @private
 * @param {*} value The value to check.
 * @param {Object} [object] The object to query keys on.
 * @returns {boolean} Returns `true` if `value` is a property name, else `false`.
 */
function isKey(value, object) {
  if (isArray(value)) {
    return false;
  }
  var type = typeof value === 'undefined' ? 'undefined' : _typeof(value);
  if (type == 'number' || type == 'symbol' || type == 'boolean' || value == null || isSymbol(value)) {
    return true;
  }
  return reIsPlainProp.test(value) || !reIsDeepProp.test(value) || object != null && value in Object(object);
}

/**
 * Checks if `value` is suitable for use as unique object key.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is suitable, else `false`.
 */
function isKeyable(value) {
  var type = typeof value === 'undefined' ? 'undefined' : _typeof(value);
  return type == 'string' || type == 'number' || type == 'symbol' || type == 'boolean' ? value !== '__proto__' : value === null;
}

/**
 * Checks if `func` has its source masked.
 *
 * @private
 * @param {Function} func The function to check.
 * @returns {boolean} Returns `true` if `func` is masked, else `false`.
 */
function isMasked(func) {
  return !!maskSrcKey && maskSrcKey in func;
}

/**
 * Checks if `value` is likely a prototype object.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a prototype, else `false`.
 */
function isPrototype(value) {
  var Ctor = value && value.constructor,
      proto = typeof Ctor == 'function' && Ctor.prototype || objectProto;

  return value === proto;
}

/**
 * Checks if `value` is suitable for strict equality comparisons, i.e. `===`.
 *
 * @private
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` if suitable for strict
 *  equality comparisons, else `false`.
 */
function isStrictComparable(value) {
  return value === value && !isObject(value);
}

/**
 * A specialized version of `matchesProperty` for source values suitable
 * for strict equality comparisons, i.e. `===`.
 *
 * @private
 * @param {string} key The key of the property to get.
 * @param {*} srcValue The value to match.
 * @returns {Function} Returns the new spec function.
 */
function matchesStrictComparable(key, srcValue) {
  return function (object) {
    if (object == null) {
      return false;
    }
    return object[key] === srcValue && (srcValue !== undefined || key in Object(object));
  };
}

/**
 * Converts `string` to a property path array.
 *
 * @private
 * @param {string} string The string to convert.
 * @returns {Array} Returns the property path array.
 */
var stringToPath = memoize(function (string) {
  string = toString(string);

  var result = [];
  if (reLeadingDot.test(string)) {
    result.push('');
  }
  string.replace(rePropName, function (match, number, quote, string) {
    result.push(quote ? string.replace(reEscapeChar, '$1') : number || match);
  });
  return result;
});

/**
 * Converts `value` to a string key if it's not a string or symbol.
 *
 * @private
 * @param {*} value The value to inspect.
 * @returns {string|symbol} Returns the key.
 */
function toKey(value) {
  if (typeof value == 'string' || isSymbol(value)) {
    return value;
  }
  var result = value + '';
  return result == '0' && 1 / value == -INFINITY ? '-0' : result;
}

/**
 * Converts `func` to its source code.
 *
 * @private
 * @param {Function} func The function to process.
 * @returns {string} Returns the source code.
 */
function toSource(func) {
  if (func != null) {
    try {
      return funcToString.call(func);
    } catch (e) {}
    try {
      return func + '';
    } catch (e) {}
  }
  return '';
}

/**
 * Creates a function that memoizes the result of `func`. If `resolver` is
 * provided, it determines the cache key for storing the result based on the
 * arguments provided to the memoized function. By default, the first argument
 * provided to the memoized function is used as the map cache key. The `func`
 * is invoked with the `this` binding of the memoized function.
 *
 * **Note:** The cache is exposed as the `cache` property on the memoized
 * function. Its creation may be customized by replacing the `_.memoize.Cache`
 * constructor with one whose instances implement the
 * [`Map`](http://ecma-international.org/ecma-262/7.0/#sec-properties-of-the-map-prototype-object)
 * method interface of `delete`, `get`, `has`, and `set`.
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Function
 * @param {Function} func The function to have its output memoized.
 * @param {Function} [resolver] The function to resolve the cache key.
 * @returns {Function} Returns the new memoized function.
 * @example
 *
 * var object = { 'a': 1, 'b': 2 };
 * var other = { 'c': 3, 'd': 4 };
 *
 * var values = _.memoize(_.values);
 * values(object);
 * // => [1, 2]
 *
 * values(other);
 * // => [3, 4]
 *
 * object.a = 2;
 * values(object);
 * // => [1, 2]
 *
 * // Modify the result cache.
 * values.cache.set(object, ['a', 'b']);
 * values(object);
 * // => ['a', 'b']
 *
 * // Replace `_.memoize.Cache`.
 * _.memoize.Cache = WeakMap;
 */
function memoize(func, resolver) {
  if (typeof func != 'function' || resolver && typeof resolver != 'function') {
    throw new TypeError(FUNC_ERROR_TEXT);
  }
  var memoized = function memoized() {
    var args = arguments,
        key = resolver ? resolver.apply(this, args) : args[0],
        cache = memoized.cache;

    if (cache.has(key)) {
      return cache.get(key);
    }
    var result = func.apply(this, args);
    memoized.cache = cache.set(key, result);
    return result;
  };
  memoized.cache = new (memoize.Cache || MapCache)();
  return memoized;
}

// Assign cache to `_.memoize`.
memoize.Cache = MapCache;

/**
 * Performs a
 * [`SameValueZero`](http://ecma-international.org/ecma-262/7.0/#sec-samevaluezero)
 * comparison between two values to determine if they are equivalent.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to compare.
 * @param {*} other The other value to compare.
 * @returns {boolean} Returns `true` if the values are equivalent, else `false`.
 * @example
 *
 * var object = { 'a': 1 };
 * var other = { 'a': 1 };
 *
 * _.eq(object, object);
 * // => true
 *
 * _.eq(object, other);
 * // => false
 *
 * _.eq('a', 'a');
 * // => true
 *
 * _.eq('a', Object('a'));
 * // => false
 *
 * _.eq(NaN, NaN);
 * // => true
 */
function eq(value, other) {
  return value === other || value !== value && other !== other;
}

/**
 * Checks if `value` is likely an `arguments` object.
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is an `arguments` object,
 *  else `false`.
 * @example
 *
 * _.isArguments(function() { return arguments; }());
 * // => true
 *
 * _.isArguments([1, 2, 3]);
 * // => false
 */
function isArguments(value) {
  // Safari 8.1 makes `arguments.callee` enumerable in strict mode.
  return isArrayLikeObject(value) && hasOwnProperty.call(value, 'callee') && (!propertyIsEnumerable.call(value, 'callee') || objectToString.call(value) == argsTag);
}

/**
 * Checks if `value` is classified as an `Array` object.
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is an array, else `false`.
 * @example
 *
 * _.isArray([1, 2, 3]);
 * // => true
 *
 * _.isArray(document.body.children);
 * // => false
 *
 * _.isArray('abc');
 * // => false
 *
 * _.isArray(_.noop);
 * // => false
 */
var isArray = Array.isArray;

/**
 * Checks if `value` is array-like. A value is considered array-like if it's
 * not a function and has a `value.length` that's an integer greater than or
 * equal to `0` and less than or equal to `Number.MAX_SAFE_INTEGER`.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is array-like, else `false`.
 * @example
 *
 * _.isArrayLike([1, 2, 3]);
 * // => true
 *
 * _.isArrayLike(document.body.children);
 * // => true
 *
 * _.isArrayLike('abc');
 * // => true
 *
 * _.isArrayLike(_.noop);
 * // => false
 */
function isArrayLike(value) {
  return value != null && isLength(value.length) && !isFunction(value);
}

/**
 * This method is like `_.isArrayLike` except that it also checks if `value`
 * is an object.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is an array-like object,
 *  else `false`.
 * @example
 *
 * _.isArrayLikeObject([1, 2, 3]);
 * // => true
 *
 * _.isArrayLikeObject(document.body.children);
 * // => true
 *
 * _.isArrayLikeObject('abc');
 * // => false
 *
 * _.isArrayLikeObject(_.noop);
 * // => false
 */
function isArrayLikeObject(value) {
  return isObjectLike(value) && isArrayLike(value);
}

/**
 * Checks if `value` is classified as a `Function` object.
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a function, else `false`.
 * @example
 *
 * _.isFunction(_);
 * // => true
 *
 * _.isFunction(/abc/);
 * // => false
 */
function isFunction(value) {
  // The use of `Object#toString` avoids issues with the `typeof` operator
  // in Safari 8-9 which returns 'object' for typed array and other constructors.
  var tag = isObject(value) ? objectToString.call(value) : '';
  return tag == funcTag || tag == genTag;
}

/**
 * Checks if `value` is a valid array-like length.
 *
 * **Note:** This method is loosely based on
 * [`ToLength`](http://ecma-international.org/ecma-262/7.0/#sec-tolength).
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a valid length, else `false`.
 * @example
 *
 * _.isLength(3);
 * // => true
 *
 * _.isLength(Number.MIN_VALUE);
 * // => false
 *
 * _.isLength(Infinity);
 * // => false
 *
 * _.isLength('3');
 * // => false
 */
function isLength(value) {
  return typeof value == 'number' && value > -1 && value % 1 == 0 && value <= MAX_SAFE_INTEGER;
}

/**
 * Checks if `value` is the
 * [language type](http://www.ecma-international.org/ecma-262/7.0/#sec-ecmascript-language-types)
 * of `Object`. (e.g. arrays, functions, objects, regexes, `new Number(0)`, and `new String('')`)
 *
 * @static
 * @memberOf _
 * @since 0.1.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is an object, else `false`.
 * @example
 *
 * _.isObject({});
 * // => true
 *
 * _.isObject([1, 2, 3]);
 * // => true
 *
 * _.isObject(_.noop);
 * // => true
 *
 * _.isObject(null);
 * // => false
 */
function isObject(value) {
  var type = typeof value === 'undefined' ? 'undefined' : _typeof(value);
  return !!value && (type == 'object' || type == 'function');
}

/**
 * Checks if `value` is object-like. A value is object-like if it's not `null`
 * and has a `typeof` result of "object".
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is object-like, else `false`.
 * @example
 *
 * _.isObjectLike({});
 * // => true
 *
 * _.isObjectLike([1, 2, 3]);
 * // => true
 *
 * _.isObjectLike(_.noop);
 * // => false
 *
 * _.isObjectLike(null);
 * // => false
 */
function isObjectLike(value) {
  return !!value && (typeof value === 'undefined' ? 'undefined' : _typeof(value)) == 'object';
}

/**
 * Checks if `value` is classified as a `Symbol` primitive or object.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a symbol, else `false`.
 * @example
 *
 * _.isSymbol(Symbol.iterator);
 * // => true
 *
 * _.isSymbol('abc');
 * // => false
 */
function isSymbol(value) {
  return (typeof value === 'undefined' ? 'undefined' : _typeof(value)) == 'symbol' || isObjectLike(value) && objectToString.call(value) == symbolTag;
}

/**
 * Checks if `value` is classified as a typed array.
 *
 * @static
 * @memberOf _
 * @since 3.0.0
 * @category Lang
 * @param {*} value The value to check.
 * @returns {boolean} Returns `true` if `value` is a typed array, else `false`.
 * @example
 *
 * _.isTypedArray(new Uint8Array);
 * // => true
 *
 * _.isTypedArray([]);
 * // => false
 */
var isTypedArray = nodeIsTypedArray ? baseUnary(nodeIsTypedArray) : baseIsTypedArray;

/**
 * Converts `value` to a string. An empty string is returned for `null`
 * and `undefined` values. The sign of `-0` is preserved.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Lang
 * @param {*} value The value to process.
 * @returns {string} Returns the string.
 * @example
 *
 * _.toString(null);
 * // => ''
 *
 * _.toString(-0);
 * // => '-0'
 *
 * _.toString([1, 2, 3]);
 * // => '1,2,3'
 */
function toString(value) {
  return value == null ? '' : baseToString(value);
}

/**
 * Gets the value at `path` of `object`. If the resolved value is
 * `undefined`, the `defaultValue` is returned in its place.
 *
 * @static
 * @memberOf _
 * @since 3.7.0
 * @category Object
 * @param {Object} object The object to query.
 * @param {Array|string} path The path of the property to get.
 * @param {*} [defaultValue] The value returned for `undefined` resolved values.
 * @returns {*} Returns the resolved value.
 * @example
 *
 * var object = { 'a': [{ 'b': { 'c': 3 } }] };
 *
 * _.get(object, 'a[0].b.c');
 * // => 3
 *
 * _.get(object, ['a', '0', 'b', 'c']);
 * // => 3
 *
 * _.get(object, 'a.b.c', 'default');
 * // => 'default'
 */
function get(object, path, defaultValue) {
  var result = object == null ? undefined : baseGet(object, path);
  return result === undefined ? defaultValue : result;
}

/**
 * Checks if `path` is a direct or inherited property of `object`.
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Object
 * @param {Object} object The object to query.
 * @param {Array|string} path The path to check.
 * @returns {boolean} Returns `true` if `path` exists, else `false`.
 * @example
 *
 * var object = _.create({ 'a': _.create({ 'b': 2 }) });
 *
 * _.hasIn(object, 'a');
 * // => true
 *
 * _.hasIn(object, 'a.b');
 * // => true
 *
 * _.hasIn(object, ['a', 'b']);
 * // => true
 *
 * _.hasIn(object, 'b');
 * // => false
 */
function hasIn(object, path) {
  return object != null && hasPath(object, path, baseHasIn);
}

/**
 * Creates an array of the own enumerable property names of `object`.
 *
 * **Note:** Non-object values are coerced to objects. See the
 * [ES spec](http://ecma-international.org/ecma-262/7.0/#sec-object.keys)
 * for more details.
 *
 * @static
 * @since 0.1.0
 * @memberOf _
 * @category Object
 * @param {Object} object The object to query.
 * @returns {Array} Returns the array of property names.
 * @example
 *
 * function Foo() {
 *   this.a = 1;
 *   this.b = 2;
 * }
 *
 * Foo.prototype.c = 3;
 *
 * _.keys(new Foo);
 * // => ['a', 'b'] (iteration order is not guaranteed)
 *
 * _.keys('hi');
 * // => ['0', '1']
 */
function keys(object) {
  return isArrayLike(object) ? arrayLikeKeys(object) : baseKeys(object);
}

/**
 * This method returns the first argument it receives.
 *
 * @static
 * @since 0.1.0
 * @memberOf _
 * @category Util
 * @param {*} value Any value.
 * @returns {*} Returns `value`.
 * @example
 *
 * var object = { 'a': 1 };
 *
 * console.log(_.identity(object) === object);
 * // => true
 */
function identity(value) {
  return value;
}

/**
 * Creates a function that returns the value at `path` of a given object.
 *
 * @static
 * @memberOf _
 * @since 2.4.0
 * @category Util
 * @param {Array|string} path The path of the property to get.
 * @returns {Function} Returns the new accessor function.
 * @example
 *
 * var objects = [
 *   { 'a': { 'b': 2 } },
 *   { 'a': { 'b': 1 } }
 * ];
 *
 * _.map(objects, _.property('a.b'));
 * // => [2, 1]
 *
 * _.map(_.sortBy(objects, _.property(['a', 'b'])), 'a.b');
 * // => [1, 2]
 */
function property(path) {
  return isKey(path) ? baseProperty(toKey(path)) : basePropertyDeep(path);
}

/**
 * This method is like `_.max` except that it accepts `iteratee` which is
 * invoked for each element in `array` to generate the criterion by which
 * the value is ranked. The iteratee is invoked with one argument: (value).
 *
 * @static
 * @memberOf _
 * @since 4.0.0
 * @category Math
 * @param {Array} array The array to iterate over.
 * @param {Function} [iteratee=_.identity] The iteratee invoked per element.
 * @returns {*} Returns the maximum value.
 * @example
 *
 * var objects = [{ 'n': 1 }, { 'n': 2 }];
 *
 * _.maxBy(objects, function(o) { return o.n; });
 * // => { 'n': 2 }
 *
 * // The `_.property` iteratee shorthand.
 * _.maxBy(objects, 'n');
 * // => { 'n': 2 }
 */
function maxBy(array, iteratee) {
  return array && array.length ? baseExtremum(array, baseIteratee(iteratee, 2), baseGt) : undefined;
}

module.exports = maxBy;
/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__(/*! ./../webpack/buildin/global.js */ "./node_modules/webpack/buildin/global.js"), __webpack_require__(/*! ./../webpack/buildin/module.js */ "./node_modules/webpack/buildin/module.js")(module)))

/***/ }),

/***/ "./node_modules/ms/index.js":
/*!**********************************!*\
  !*** ./node_modules/ms/index.js ***!
  \**********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

/**
 * Helpers.
 */

var s = 1000;
var m = s * 60;
var h = m * 60;
var d = h * 24;
var y = d * 365.25;

/**
 * Parse or format the given `val`.
 *
 * Options:
 *
 *  - `long` verbose formatting [false]
 *
 * @param {String|Number} val
 * @param {Object} [options]
 * @throws {Error} throw an error if val is not a non-empty string or a number
 * @return {String|Number}
 * @api public
 */

module.exports = function (val, options) {
  options = options || {};
  var type = typeof val === 'undefined' ? 'undefined' : _typeof(val);
  if (type === 'string' && val.length > 0) {
    return parse(val);
  } else if (type === 'number' && isNaN(val) === false) {
    return options.long ? fmtLong(val) : fmtShort(val);
  }
  throw new Error('val is not a non-empty string or a valid number. val=' + JSON.stringify(val));
};

/**
 * Parse the given `str` and return milliseconds.
 *
 * @param {String} str
 * @return {Number}
 * @api private
 */

function parse(str) {
  str = String(str);
  if (str.length > 100) {
    return;
  }
  var match = /^((?:\d+)?\.?\d+) *(milliseconds?|msecs?|ms|seconds?|secs?|s|minutes?|mins?|m|hours?|hrs?|h|days?|d|years?|yrs?|y)?$/i.exec(str);
  if (!match) {
    return;
  }
  var n = parseFloat(match[1]);
  var type = (match[2] || 'ms').toLowerCase();
  switch (type) {
    case 'years':
    case 'year':
    case 'yrs':
    case 'yr':
    case 'y':
      return n * y;
    case 'days':
    case 'day':
    case 'd':
      return n * d;
    case 'hours':
    case 'hour':
    case 'hrs':
    case 'hr':
    case 'h':
      return n * h;
    case 'minutes':
    case 'minute':
    case 'mins':
    case 'min':
    case 'm':
      return n * m;
    case 'seconds':
    case 'second':
    case 'secs':
    case 'sec':
    case 's':
      return n * s;
    case 'milliseconds':
    case 'millisecond':
    case 'msecs':
    case 'msec':
    case 'ms':
      return n;
    default:
      return undefined;
  }
}

/**
 * Short format for `ms`.
 *
 * @param {Number} ms
 * @return {String}
 * @api private
 */

function fmtShort(ms) {
  if (ms >= d) {
    return Math.round(ms / d) + 'd';
  }
  if (ms >= h) {
    return Math.round(ms / h) + 'h';
  }
  if (ms >= m) {
    return Math.round(ms / m) + 'm';
  }
  if (ms >= s) {
    return Math.round(ms / s) + 's';
  }
  return ms + 'ms';
}

/**
 * Long format for `ms`.
 *
 * @param {Number} ms
 * @return {String}
 * @api private
 */

function fmtLong(ms) {
  return plural(ms, d, 'day') || plural(ms, h, 'hour') || plural(ms, m, 'minute') || plural(ms, s, 'second') || ms + ' ms';
}

/**
 * Pluralization helper.
 */

function plural(ms, n, name) {
  if (ms < n) {
    return;
  }
  if (ms < n * 1.5) {
    return Math.floor(ms / n) + ' ' + name;
  }
  return Math.ceil(ms / n) + ' ' + name + 's';
}

/***/ }),

/***/ "./node_modules/process/browser.js":
/*!*****************************************!*\
  !*** ./node_modules/process/browser.js ***!
  \*****************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


// shim for using process in browser
var process = module.exports = {};

// cached from whatever global is present so that test runners that stub it
// don't break things.  But we need to wrap it in a try catch in case it is
// wrapped in strict mode code which doesn't define any globals.  It's inside a
// function because try/catches deoptimize in certain engines.

var cachedSetTimeout;
var cachedClearTimeout;

function defaultSetTimout() {
    throw new Error('setTimeout has not been defined');
}
function defaultClearTimeout() {
    throw new Error('clearTimeout has not been defined');
}
(function () {
    try {
        if (typeof setTimeout === 'function') {
            cachedSetTimeout = setTimeout;
        } else {
            cachedSetTimeout = defaultSetTimout;
        }
    } catch (e) {
        cachedSetTimeout = defaultSetTimout;
    }
    try {
        if (typeof clearTimeout === 'function') {
            cachedClearTimeout = clearTimeout;
        } else {
            cachedClearTimeout = defaultClearTimeout;
        }
    } catch (e) {
        cachedClearTimeout = defaultClearTimeout;
    }
})();
function runTimeout(fun) {
    if (cachedSetTimeout === setTimeout) {
        //normal enviroments in sane situations
        return setTimeout(fun, 0);
    }
    // if setTimeout wasn't available but was latter defined
    if ((cachedSetTimeout === defaultSetTimout || !cachedSetTimeout) && setTimeout) {
        cachedSetTimeout = setTimeout;
        return setTimeout(fun, 0);
    }
    try {
        // when when somebody has screwed with setTimeout but no I.E. maddness
        return cachedSetTimeout(fun, 0);
    } catch (e) {
        try {
            // When we are in I.E. but the script has been evaled so I.E. doesn't trust the global object when called normally
            return cachedSetTimeout.call(null, fun, 0);
        } catch (e) {
            // same as above but when it's a version of I.E. that must have the global object for 'this', hopfully our context correct otherwise it will throw a global error
            return cachedSetTimeout.call(this, fun, 0);
        }
    }
}
function runClearTimeout(marker) {
    if (cachedClearTimeout === clearTimeout) {
        //normal enviroments in sane situations
        return clearTimeout(marker);
    }
    // if clearTimeout wasn't available but was latter defined
    if ((cachedClearTimeout === defaultClearTimeout || !cachedClearTimeout) && clearTimeout) {
        cachedClearTimeout = clearTimeout;
        return clearTimeout(marker);
    }
    try {
        // when when somebody has screwed with setTimeout but no I.E. maddness
        return cachedClearTimeout(marker);
    } catch (e) {
        try {
            // When we are in I.E. but the script has been evaled so I.E. doesn't  trust the global object when called normally
            return cachedClearTimeout.call(null, marker);
        } catch (e) {
            // same as above but when it's a version of I.E. that must have the global object for 'this', hopfully our context correct otherwise it will throw a global error.
            // Some versions of I.E. have different rules for clearTimeout vs setTimeout
            return cachedClearTimeout.call(this, marker);
        }
    }
}
var queue = [];
var draining = false;
var currentQueue;
var queueIndex = -1;

function cleanUpNextTick() {
    if (!draining || !currentQueue) {
        return;
    }
    draining = false;
    if (currentQueue.length) {
        queue = currentQueue.concat(queue);
    } else {
        queueIndex = -1;
    }
    if (queue.length) {
        drainQueue();
    }
}

function drainQueue() {
    if (draining) {
        return;
    }
    var timeout = runTimeout(cleanUpNextTick);
    draining = true;

    var len = queue.length;
    while (len) {
        currentQueue = queue;
        queue = [];
        while (++queueIndex < len) {
            if (currentQueue) {
                currentQueue[queueIndex].run();
            }
        }
        queueIndex = -1;
        len = queue.length;
    }
    currentQueue = null;
    draining = false;
    runClearTimeout(timeout);
}

process.nextTick = function (fun) {
    var args = new Array(arguments.length - 1);
    if (arguments.length > 1) {
        for (var i = 1; i < arguments.length; i++) {
            args[i - 1] = arguments[i];
        }
    }
    queue.push(new Item(fun, args));
    if (queue.length === 1 && !draining) {
        runTimeout(drainQueue);
    }
};

// v8 likes predictible objects
function Item(fun, array) {
    this.fun = fun;
    this.array = array;
}
Item.prototype.run = function () {
    this.fun.apply(null, this.array);
};
process.title = 'browser';
process.browser = true;
process.env = {};
process.argv = [];
process.version = ''; // empty string to avoid regexp issues
process.versions = {};

function noop() {}

process.on = noop;
process.addListener = noop;
process.once = noop;
process.off = noop;
process.removeListener = noop;
process.removeAllListeners = noop;
process.emit = noop;
process.prependListener = noop;
process.prependOnceListener = noop;

process.listeners = function (name) {
    return [];
};

process.binding = function (name) {
    throw new Error('process.binding is not supported');
};

process.cwd = function () {
    return '/';
};
process.chdir = function (dir) {
    throw new Error('process.chdir is not supported');
};
process.umask = function () {
    return 0;
};

/***/ }),

/***/ "./node_modules/webpack/buildin/global.js":
/*!***********************************!*\
  !*** (webpack)/buildin/global.js ***!
  \***********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

var g;

// This works in non-strict mode
g = function () {
	return this;
}();

try {
	// This works if eval is allowed (see CSP)
	g = g || Function("return this")() || (1, eval)("this");
} catch (e) {
	// This works if the window reference is available
	if ((typeof window === "undefined" ? "undefined" : _typeof(window)) === "object") g = window;
}

// g can still be undefined, but nothing to do about it...
// We return undefined, instead of nothing here, so it's
// easier to handle this case. if(!global) { ...}

module.exports = g;

/***/ }),

/***/ "./node_modules/webpack/buildin/module.js":
/*!***********************************!*\
  !*** (webpack)/buildin/module.js ***!
  \***********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


module.exports = function (module) {
	if (!module.webpackPolyfill) {
		module.deprecate = function () {};
		module.paths = [];
		// module.parent = undefined by default
		if (!module.children) module.children = [];
		Object.defineProperty(module, "loaded", {
			enumerable: true,
			get: function get() {
				return module.l;
			}
		});
		Object.defineProperty(module, "id", {
			enumerable: true,
			get: function get() {
				return module.i;
			}
		});
		module.webpackPolyfill = 1;
	}
	return module;
};

/***/ }),

/***/ "./node_modules/whatwg-fetch/fetch.js":
/*!********************************************!*\
  !*** ./node_modules/whatwg-fetch/fetch.js ***!
  \********************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


(function (self) {
  'use strict';

  if (self.fetch) {
    return;
  }

  var support = {
    searchParams: 'URLSearchParams' in self,
    iterable: 'Symbol' in self && 'iterator' in Symbol,
    blob: 'FileReader' in self && 'Blob' in self && function () {
      try {
        new Blob();
        return true;
      } catch (e) {
        return false;
      }
    }(),
    formData: 'FormData' in self,
    arrayBuffer: 'ArrayBuffer' in self
  };

  if (support.arrayBuffer) {
    var viewClasses = ['[object Int8Array]', '[object Uint8Array]', '[object Uint8ClampedArray]', '[object Int16Array]', '[object Uint16Array]', '[object Int32Array]', '[object Uint32Array]', '[object Float32Array]', '[object Float64Array]'];

    var isDataView = function isDataView(obj) {
      return obj && DataView.prototype.isPrototypeOf(obj);
    };

    var isArrayBufferView = ArrayBuffer.isView || function (obj) {
      return obj && viewClasses.indexOf(Object.prototype.toString.call(obj)) > -1;
    };
  }

  function normalizeName(name) {
    if (typeof name !== 'string') {
      name = String(name);
    }
    if (/[^a-z0-9\-#$%&'*+.\^_`|~]/i.test(name)) {
      throw new TypeError('Invalid character in header field name');
    }
    return name.toLowerCase();
  }

  function normalizeValue(value) {
    if (typeof value !== 'string') {
      value = String(value);
    }
    return value;
  }

  // Build a destructive iterator for the value list
  function iteratorFor(items) {
    var iterator = {
      next: function next() {
        var value = items.shift();
        return { done: value === undefined, value: value };
      }
    };

    if (support.iterable) {
      iterator[Symbol.iterator] = function () {
        return iterator;
      };
    }

    return iterator;
  }

  function Headers(headers) {
    this.map = {};

    if (headers instanceof Headers) {
      headers.forEach(function (value, name) {
        this.append(name, value);
      }, this);
    } else if (Array.isArray(headers)) {
      headers.forEach(function (header) {
        this.append(header[0], header[1]);
      }, this);
    } else if (headers) {
      Object.getOwnPropertyNames(headers).forEach(function (name) {
        this.append(name, headers[name]);
      }, this);
    }
  }

  Headers.prototype.append = function (name, value) {
    name = normalizeName(name);
    value = normalizeValue(value);
    var oldValue = this.map[name];
    this.map[name] = oldValue ? oldValue + ',' + value : value;
  };

  Headers.prototype['delete'] = function (name) {
    delete this.map[normalizeName(name)];
  };

  Headers.prototype.get = function (name) {
    name = normalizeName(name);
    return this.has(name) ? this.map[name] : null;
  };

  Headers.prototype.has = function (name) {
    return this.map.hasOwnProperty(normalizeName(name));
  };

  Headers.prototype.set = function (name, value) {
    this.map[normalizeName(name)] = normalizeValue(value);
  };

  Headers.prototype.forEach = function (callback, thisArg) {
    for (var name in this.map) {
      if (this.map.hasOwnProperty(name)) {
        callback.call(thisArg, this.map[name], name, this);
      }
    }
  };

  Headers.prototype.keys = function () {
    var items = [];
    this.forEach(function (value, name) {
      items.push(name);
    });
    return iteratorFor(items);
  };

  Headers.prototype.values = function () {
    var items = [];
    this.forEach(function (value) {
      items.push(value);
    });
    return iteratorFor(items);
  };

  Headers.prototype.entries = function () {
    var items = [];
    this.forEach(function (value, name) {
      items.push([name, value]);
    });
    return iteratorFor(items);
  };

  if (support.iterable) {
    Headers.prototype[Symbol.iterator] = Headers.prototype.entries;
  }

  function consumed(body) {
    if (body.bodyUsed) {
      return Promise.reject(new TypeError('Already read'));
    }
    body.bodyUsed = true;
  }

  function fileReaderReady(reader) {
    return new Promise(function (resolve, reject) {
      reader.onload = function () {
        resolve(reader.result);
      };
      reader.onerror = function () {
        reject(reader.error);
      };
    });
  }

  function readBlobAsArrayBuffer(blob) {
    var reader = new FileReader();
    var promise = fileReaderReady(reader);
    reader.readAsArrayBuffer(blob);
    return promise;
  }

  function readBlobAsText(blob) {
    var reader = new FileReader();
    var promise = fileReaderReady(reader);
    reader.readAsText(blob);
    return promise;
  }

  function readArrayBufferAsText(buf) {
    var view = new Uint8Array(buf);
    var chars = new Array(view.length);

    for (var i = 0; i < view.length; i++) {
      chars[i] = String.fromCharCode(view[i]);
    }
    return chars.join('');
  }

  function bufferClone(buf) {
    if (buf.slice) {
      return buf.slice(0);
    } else {
      var view = new Uint8Array(buf.byteLength);
      view.set(new Uint8Array(buf));
      return view.buffer;
    }
  }

  function Body() {
    this.bodyUsed = false;

    this._initBody = function (body) {
      this._bodyInit = body;
      if (!body) {
        this._bodyText = '';
      } else if (typeof body === 'string') {
        this._bodyText = body;
      } else if (support.blob && Blob.prototype.isPrototypeOf(body)) {
        this._bodyBlob = body;
      } else if (support.formData && FormData.prototype.isPrototypeOf(body)) {
        this._bodyFormData = body;
      } else if (support.searchParams && URLSearchParams.prototype.isPrototypeOf(body)) {
        this._bodyText = body.toString();
      } else if (support.arrayBuffer && support.blob && isDataView(body)) {
        this._bodyArrayBuffer = bufferClone(body.buffer);
        // IE 10-11 can't handle a DataView body.
        this._bodyInit = new Blob([this._bodyArrayBuffer]);
      } else if (support.arrayBuffer && (ArrayBuffer.prototype.isPrototypeOf(body) || isArrayBufferView(body))) {
        this._bodyArrayBuffer = bufferClone(body);
      } else {
        throw new Error('unsupported BodyInit type');
      }

      if (!this.headers.get('content-type')) {
        if (typeof body === 'string') {
          this.headers.set('content-type', 'text/plain;charset=UTF-8');
        } else if (this._bodyBlob && this._bodyBlob.type) {
          this.headers.set('content-type', this._bodyBlob.type);
        } else if (support.searchParams && URLSearchParams.prototype.isPrototypeOf(body)) {
          this.headers.set('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
        }
      }
    };

    if (support.blob) {
      this.blob = function () {
        var rejected = consumed(this);
        if (rejected) {
          return rejected;
        }

        if (this._bodyBlob) {
          return Promise.resolve(this._bodyBlob);
        } else if (this._bodyArrayBuffer) {
          return Promise.resolve(new Blob([this._bodyArrayBuffer]));
        } else if (this._bodyFormData) {
          throw new Error('could not read FormData body as blob');
        } else {
          return Promise.resolve(new Blob([this._bodyText]));
        }
      };

      this.arrayBuffer = function () {
        if (this._bodyArrayBuffer) {
          return consumed(this) || Promise.resolve(this._bodyArrayBuffer);
        } else {
          return this.blob().then(readBlobAsArrayBuffer);
        }
      };
    }

    this.text = function () {
      var rejected = consumed(this);
      if (rejected) {
        return rejected;
      }

      if (this._bodyBlob) {
        return readBlobAsText(this._bodyBlob);
      } else if (this._bodyArrayBuffer) {
        return Promise.resolve(readArrayBufferAsText(this._bodyArrayBuffer));
      } else if (this._bodyFormData) {
        throw new Error('could not read FormData body as text');
      } else {
        return Promise.resolve(this._bodyText);
      }
    };

    if (support.formData) {
      this.formData = function () {
        return this.text().then(decode);
      };
    }

    this.json = function () {
      return this.text().then(JSON.parse);
    };

    return this;
  }

  // HTTP methods whose capitalization should be normalized
  var methods = ['DELETE', 'GET', 'HEAD', 'OPTIONS', 'POST', 'PUT'];

  function normalizeMethod(method) {
    var upcased = method.toUpperCase();
    return methods.indexOf(upcased) > -1 ? upcased : method;
  }

  function Request(input, options) {
    options = options || {};
    var body = options.body;

    if (input instanceof Request) {
      if (input.bodyUsed) {
        throw new TypeError('Already read');
      }
      this.url = input.url;
      this.credentials = input.credentials;
      if (!options.headers) {
        this.headers = new Headers(input.headers);
      }
      this.method = input.method;
      this.mode = input.mode;
      if (!body && input._bodyInit != null) {
        body = input._bodyInit;
        input.bodyUsed = true;
      }
    } else {
      this.url = String(input);
    }

    this.credentials = options.credentials || this.credentials || 'omit';
    if (options.headers || !this.headers) {
      this.headers = new Headers(options.headers);
    }
    this.method = normalizeMethod(options.method || this.method || 'GET');
    this.mode = options.mode || this.mode || null;
    this.referrer = null;

    if ((this.method === 'GET' || this.method === 'HEAD') && body) {
      throw new TypeError('Body not allowed for GET or HEAD requests');
    }
    this._initBody(body);
  }

  Request.prototype.clone = function () {
    return new Request(this, { body: this._bodyInit });
  };

  function decode(body) {
    var form = new FormData();
    body.trim().split('&').forEach(function (bytes) {
      if (bytes) {
        var split = bytes.split('=');
        var name = split.shift().replace(/\+/g, ' ');
        var value = split.join('=').replace(/\+/g, ' ');
        form.append(decodeURIComponent(name), decodeURIComponent(value));
      }
    });
    return form;
  }

  function parseHeaders(rawHeaders) {
    var headers = new Headers();
    // Replace instances of \r\n and \n followed by at least one space or horizontal tab with a space
    // https://tools.ietf.org/html/rfc7230#section-3.2
    var preProcessedHeaders = rawHeaders.replace(/\r?\n[\t ]+/g, ' ');
    preProcessedHeaders.split(/\r?\n/).forEach(function (line) {
      var parts = line.split(':');
      var key = parts.shift().trim();
      if (key) {
        var value = parts.join(':').trim();
        headers.append(key, value);
      }
    });
    return headers;
  }

  Body.call(Request.prototype);

  function Response(bodyInit, options) {
    if (!options) {
      options = {};
    }

    this.type = 'default';
    this.status = options.status === undefined ? 200 : options.status;
    this.ok = this.status >= 200 && this.status < 300;
    this.statusText = 'statusText' in options ? options.statusText : 'OK';
    this.headers = new Headers(options.headers);
    this.url = options.url || '';
    this._initBody(bodyInit);
  }

  Body.call(Response.prototype);

  Response.prototype.clone = function () {
    return new Response(this._bodyInit, {
      status: this.status,
      statusText: this.statusText,
      headers: new Headers(this.headers),
      url: this.url
    });
  };

  Response.error = function () {
    var response = new Response(null, { status: 0, statusText: '' });
    response.type = 'error';
    return response;
  };

  var redirectStatuses = [301, 302, 303, 307, 308];

  Response.redirect = function (url, status) {
    if (redirectStatuses.indexOf(status) === -1) {
      throw new RangeError('Invalid status code');
    }

    return new Response(null, { status: status, headers: { location: url } });
  };

  self.Headers = Headers;
  self.Request = Request;
  self.Response = Response;

  self.fetch = function (input, init) {
    return new Promise(function (resolve, reject) {
      var request = new Request(input, init);
      var xhr = new XMLHttpRequest();

      xhr.onload = function () {
        var options = {
          status: xhr.status,
          statusText: xhr.statusText,
          headers: parseHeaders(xhr.getAllResponseHeaders() || '')
        };
        options.url = 'responseURL' in xhr ? xhr.responseURL : options.headers.get('X-Request-URL');
        var body = 'response' in xhr ? xhr.response : xhr.responseText;
        resolve(new Response(body, options));
      };

      xhr.onerror = function () {
        reject(new TypeError('Network request failed'));
      };

      xhr.ontimeout = function () {
        reject(new TypeError('Network request failed'));
      };

      xhr.open(request.method, request.url, true);

      if (request.credentials === 'include') {
        xhr.withCredentials = true;
      } else if (request.credentials === 'omit') {
        xhr.withCredentials = false;
      }

      if ('responseType' in xhr && support.blob) {
        xhr.responseType = 'blob';
      }

      request.headers.forEach(function (value, name) {
        xhr.setRequestHeader(name, value);
      });

      xhr.send(typeof request._bodyInit === 'undefined' ? null : request._bodyInit);
    });
  };
  self.fetch.polyfill = true;
})(typeof self !== 'undefined' ? self : undefined);

/***/ }),

/***/ "./source/js/composite-image.js":
/*!**************************************!*\
  !*** ./source/js/composite-image.js ***!
  \**************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _tileCoverageMap = __webpack_require__(/*! ./tile-coverage-map */ "./source/js/tile-coverage-map.js");

var _tileCoverageMap2 = _interopRequireDefault(_tileCoverageMap);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/**
 * @class CompositeImage
 * @private
 *
 * Utility class to composite tiles into a complete image
 * and track the rendered state of an image as new tiles
 * load.
 */

/**
 * @param levels {Array.<Array.<Tile>>}
 * @constructor
 */
var CompositeImage = function () {
    function CompositeImage(levels) {
        _classCallCheck(this, CompositeImage);

        this._levels = levels; // Assume levels sorted high-res first
        var urlsToTiles = this._urlsToTiles = {};

        levels.forEach(function (level) {
            level.tiles.forEach(function (tile) {
                urlsToTiles[tile.url] = {
                    zoomLevel: level.zoomLevel,
                    row: tile.row,
                    col: tile.col
                };
            });
        });

        this.clear();
    }

    _createClass(CompositeImage, [{
        key: "clear",
        value: function clear() {
            var loadedByLevel = this._loadedByLevel = {};

            this._levels.forEach(function (level) {
                loadedByLevel[level.zoomLevel] = new _tileCoverageMap2.default(level.rows, level.cols);
            });
        }
    }, {
        key: "getTiles",
        value: function getTiles(baseZoomLevel) {
            var _this = this;

            var toRenderByLevel = [];
            var highestZoomLevel = this._levels[0].zoomLevel;
            var covered = new _tileCoverageMap2.default(this._levels[0].rows, this._levels[0].cols);

            var bestLevelIndex = void 0;

            // Default to the lowest zoom level
            if (baseZoomLevel === null) {
                bestLevelIndex = 0;
            } else {
                var ceilLevel = Math.ceil(baseZoomLevel);
                bestLevelIndex = findIndex(this._levels, function (level) {
                    return level.zoomLevel <= ceilLevel;
                });
                // bestLevelIndex = this._levels.findIndex((level) => level.zoomLevel <= ceilLevel);
            }

            // The best level, followed by higher-res levels in ascending order of resolution,
            // followed by lower-res levels in descending order of resolution
            var levelsByPreference = this._levels.slice(0, bestLevelIndex + 1).reverse().concat(this._levels.slice(bestLevelIndex + 1));

            levelsByPreference.forEach(function (level) {
                var loaded = _this._loadedByLevel[level.zoomLevel];

                var additionalTiles = level.tiles.filter(function (tile) {
                    return loaded.isLoaded(tile.row, tile.col);
                });

                // Filter out entirely covered tiles

                // FIXME: Is it better to draw all of a partially covered tile,
                // with some of it ultimately covered, or to pick out the region
                // which needs to be drawn?
                // See https://github.com/DDMAL/diva.js/issues/358
                var scaleRatio = Math.pow(2, highestZoomLevel - level.zoomLevel);

                additionalTiles = additionalTiles.filter(function (tile) {
                    var isNeeded = false;

                    var highResRow = tile.row * scaleRatio;
                    var highResCol = tile.col * scaleRatio;

                    for (var i = 0; i < scaleRatio; i++) {
                        for (var j = 0; j < scaleRatio; j++) {
                            if (!covered.isLoaded(highResRow + i, highResCol + j)) {
                                isNeeded = true;
                                covered.set(highResRow + i, highResCol + j, true);
                            }
                        }
                    }

                    return isNeeded;
                });

                toRenderByLevel.push(additionalTiles);
            }, this);

            // Less-preferred tiles should come first
            toRenderByLevel.reverse();

            var tiles = [];

            toRenderByLevel.forEach(function (byLevel) {
                tiles.push.apply(tiles, byLevel);
            });

            return tiles;
        }

        /**
         * Update the composite image to take into account all the URLs
         * loaded in an image cache.
         *
         * @param cache {ImageCache}
         */

    }, {
        key: "updateFromCache",
        value: function updateFromCache(cache) {
            var _this2 = this;

            this.clear();

            this._levels.forEach(function (level) {
                var loaded = _this2._loadedByLevel[level.zoomLevel];

                level.tiles.forEach(function (tile) {
                    if (cache.has(tile.url)) loaded.set(tile.row, tile.col, true);
                });
            }, this);
        }
    }, {
        key: "updateWithLoadedUrls",
        value: function updateWithLoadedUrls(urls) {
            var _this3 = this;

            urls.forEach(function (url) {
                var entry = _this3._urlsToTiles[url];
                _this3._loadedByLevel[entry.zoomLevel].set(entry.row, entry.col, true);
            }, this);
        }
    }]);

    return CompositeImage;
}();

// function fill (count, value)
// {
//     const arr = new Array(count);
//
//     for (let i=0; i < count; i++)
//         arr[i] = value;
//
//     return arr;
// }

exports.default = CompositeImage;
function findIndex(array, predicate) {
    var length = array.length;
    for (var i = 0; i < length; i++) {
        if (predicate(array[i], i)) return i;
    }

    return -1;
}

/***/ }),

/***/ "./source/js/diva-global.js":
/*!**********************************!*\
  !*** ./source/js/diva-global.js ***!
  \**********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

var _events = __webpack_require__(/*! ./utils/events */ "./source/js/utils/events.js");

// import PluginRegistry from './plugin-registry';

var diva = {
  Events: _events.Events

  // registerPlugin: function (plugin)
  // {
  //     PluginRegistry.register(plugin);
  // },

  /**
   * Create a new Diva instance at the given element
   *
   * @param element {Element}
   * @param options {Object}
   * @returns {Diva}
   */
  // create: function (element, options)
  // {
  //     if (diva.find(element))
  //         throw new Error('Diva is already initialized on ' + reprElem(element));
  //
  //     const $elem = $(element);
  //     $elem.diva(options);
  //
  //     return $elem.data('diva');
  // },

  /**
   * Return the Diva instance attached to the
   * element, if any.
   *
   * @param element
   * @returns {Diva|null}
   */
  // find: function (element)
  // {
  //     return $(element).data('diva') || null;
  // }
};

exports.default = diva;

// function reprElem(elem)
// {
//     const id = elem.id ? '#' + elem.id : elem.id;
//     const classes = elem.className ? '.' + elem.className.split(/\s+/g).join('.') : '';
//
//     return (id ? id : elem.tagName.toLowerCase()) + classes;
// }

/***/ }),

/***/ "./source/js/diva.js":
/*!***************************!*\
  !*** ./source/js/diva.js ***!
  \***************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

__webpack_require__(/*! ./utils/vanilla.kinetic */ "./source/js/utils/vanilla.kinetic.js");

__webpack_require__(/*! ./utils/dragscroll */ "./source/js/utils/dragscroll.js");

var _elt = __webpack_require__(/*! ./utils/elt */ "./source/js/utils/elt.js");

var _exceptions = __webpack_require__(/*! ./exceptions */ "./source/js/exceptions.js");

var _divaGlobal = __webpack_require__(/*! ./diva-global */ "./source/js/diva-global.js");

var _divaGlobal2 = _interopRequireDefault(_divaGlobal);

var _viewerCore = __webpack_require__(/*! ./viewer-core */ "./source/js/viewer-core.js");

var _viewerCore2 = _interopRequireDefault(_viewerCore);

var _imageManifest = __webpack_require__(/*! ./image-manifest */ "./source/js/image-manifest.js");

var _imageManifest2 = _interopRequireDefault(_imageManifest);

var _toolbar = __webpack_require__(/*! ./toolbar */ "./source/js/toolbar.js");

var _toolbar2 = _interopRequireDefault(_toolbar);

var _hashParams = __webpack_require__(/*! ./utils/hash-params */ "./source/js/utils/hash-params.js");

var _hashParams2 = _interopRequireDefault(_hashParams);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/**
 * The top-level class for Diva objects. This is instantiated by passing in an HTML element
 * ID or HTML Element node and an object containing a list of options, of which the 'objectData'
 * option is required and which must point to a IIIF Presentation API Manifest:
 *
 * var diva = new Diva('element-id', {
 *     objectData: "http://example.com/iiif-manifest.json"
 * });
 *
 * This class also serves as the entry point for the Events system, in which applications can subscribe
 * to notifications sent from Diva instances:
 *
 * Diva.Events.subscribe('VisiblePageDidChange', function () { console.log("Visible Page Changed"); });
 *
 *
 *
 **/
var Diva = function () {
    function Diva(element, options) {
        _classCallCheck(this, Diva);

        /*
         * If a string is passed in, convert that to an element.
         * */
        if (!(element instanceof HTMLElement)) {
            this.element = document.getElementById(element);

            if (this.element === null) {
                throw new _exceptions.DivaParentElementNotFoundException();
            }
        }

        if (!options.objectData) {
            throw new _exceptions.ObjectDataNotSuppliedException('You must supply either a URL or a literal object to the `objectData` key.');
        }

        this.options = Object.assign({
            adaptivePadding: 0.05, // The ratio of padding to the page dimension
            arrowScrollAmount: 40, // The amount (in pixels) to scroll by when using arrow keys
            blockMobileMove: false, // Prevent moving or scrolling the page on mobile devices
            objectData: '', // A IIIF Manifest or a JSON file generated by process.py that provides the object dimension data, or a URL pointing to such data - *REQUIRED*
            enableAutoTitle: true, // Shows the title within a div of id diva-title
            enableFilename: true, // Uses filenames and not page numbers for links (i=bm_001.tif, not p=1)
            enableFullscreen: true, // Enable or disable fullscreen icon (mode still available)
            enableGotoPage: true, // A "go to page" jump box
            enableGotoSuggestions: true, // Controls whether suggestions are shown under the input field when the user is typing in the 'go to page' form
            enableGridIcon: true, // A grid view of all the pages
            enableGridControls: 'buttons', // Specify control of pages per grid row in Grid view. Possible values: 'buttons' (+/-), 'slider'. Any other value disables the controls.
            enableImageTitles: true, // Adds "Page {n}" title to page images if true
            enableKeyScroll: true, // Captures scrolling using the arrow and page up/down keys regardless of page focus. When off, defers to default browser scrolling behavior.
            enableLinkIcon: true, // Controls the visibility of the link icon
            enableNonPagedVisibilityIcon: true, // Controls the visibility of the icon to toggle the visibility of non-paged pages. (Automatically hidden if no 'non-paged' pages).
            enableSpaceScroll: false, // Scrolling down by pressing the space key
            enableToolbar: true, // Enables the toolbar. Note that disabling this means you have to handle all controls yourself.
            enableZoomControls: 'buttons', // Specify controls for zooming in and out. Possible values: 'buttons' (+/-), 'slider'. Any other value disables the controls.
            fillParentHeight: true, // Use a flexbox layout to allow Diva to fill its parent's height
            fixedPadding: 10, // Fallback if adaptive padding is set to 0
            fixedHeightGrid: true, // So each page in grid view has the same height (only widths differ)
            goDirectlyTo: 0, // Default initial page to show (0-indexed)
            hashParamSuffix: null, // Used when there are multiple document viewers on a page
            iipServerURL: '', // The URL to the IIPImage installation, including the `?FIF=` - *REQUIRED*, unless using IIIF
            inFullscreen: false, // Set to true to load fullscreen mode initially
            inBookLayout: false, // Set to true to view the document with facing pages in document mode
            inGrid: false, // Set to true to load grid view initially
            imageDir: '', // Image directory, either absolute path or relative to IIP's FILESYSTEM_PREFIX - *REQUIRED*, unless using IIIF
            maxPagesPerRow: 8, // Maximum number of pages per row in grid view
            maxZoomLevel: -1, // Optional; defaults to the max zoom returned in the JSON response
            minPagesPerRow: 2, // Minimum pages per row in grid view. Recommended default.
            minZoomLevel: 0, // Defaults to 0 (the minimum zoom)
            onGotoSubmit: null, // When set to a function that takes a string and returns a page index, this will override the default behaviour of the 'go to page' form submission
            pageAliases: {}, // An object mapping specific page indices to aliases (has priority over 'pageAliasFunction'
            pageAliasFunction: function pageAliasFunction() {
                return false;
            }, // A function mapping page indices to an alias. If false is returned, default page number is displayed
            pageLoadTimeout: 200, // Number of milliseconds to wait before loading pages
            pagesPerRow: 5, // The default number of pages per row in grid view
            showNonPagedPages: false, // Whether pages tagged as 'non-paged' (in IIIF manifests only) should be visible after initial load
            throbberTimeout: 100, // Number of milliseconds to wait before showing throbber
            tileHeight: 256, // The height of each tile, in pixels; usually 256
            tileWidth: 256, // The width of each tile, in pixels; usually 256
            toolbarParentObject: null, // The toolbar parent object.
            verticallyOriented: true, // Determines vertical vs. horizontal orientation
            viewportMargin: 200, // Pretend tiles +/- 200px away from viewport are in
            zoomLevel: 2 // The initial zoom level (used to store the current zoom level)
        }, options);

        // In order to fill the height, use a wrapper div displayed using a flexbox layout
        var wrapperElement = (0, _elt.elt)('div', {
            class: 'diva-wrapper' + (this.options.fillParentHeight ? " diva-wrapper-flexbox" : "")
        });

        this.element.appendChild(wrapperElement);

        this.options.toolbarParentObject = this.options.toolbarParentObject || wrapperElement;

        var viewerCore = new _viewerCore2.default(wrapperElement, this.options, this);

        this.viewerState = viewerCore.getInternalState();
        this.settings = viewerCore.getSettings();
        this.toolbar = new _toolbar2.default(this);

        wrapperElement.id = this.settings.ID + 'wrapper';

        this.divaState = {
            viewerCore: viewerCore,
            toolbar: this.settings.enableToolbar ? this.toolbar : null
        };

        this.toolbar.render();
        this.hashState = this._getHashParamState();

        this._loadOrFetchObjectData();
    }

    /**
     * @private
     **/


    _createClass(Diva, [{
        key: '_loadOrFetchObjectData',
        value: function _loadOrFetchObjectData() {
            var _this = this;

            if (_typeof(this.settings.objectData) === 'object') {
                var self = this;
                // Defer execution until initialization has completed
                setTimeout(function () {
                    self._loadObjectData(self.settings.objectData, self.hashState);
                }, 0);
            } else {
                var pendingManifestRequest = fetch(this.settings.objectData, {
                    headers: {
                        "Accept": "application/json"
                    }
                }).then(function (response) {
                    if (!response.ok) {
                        _this._ajaxError(response);

                        var error = new Error(response.statusText);
                        error.response = response;
                        throw error;
                    }
                    return response.json();
                }).then(function (data) {
                    _this._loadObjectData(data, _this.hashState);
                });

                // Store the pending request so that it can be cancelled in the event that Diva needs to be destroyed
                this.divaState.viewerCore.setPendingManifestRequest(pendingManifestRequest);
            }
        }

        /**
         * @private
         **/

    }, {
        key: '_showError',
        value: function _showError(message) {
            this.divaState.viewerCore.showError(message);
        }

        /**
         * @private
         * */

    }, {
        key: '_ajaxError',
        value: function _ajaxError(response) {
            // Show a basic error message within the document viewer pane
            var errorMessage = ['Invalid objectData setting. Error code: ' + response.status + ' ' + response.statusText];

            // Detect and handle CORS errors
            var dataHasAbsolutePath = this.settings.objectData.lastIndexOf('http', 0) === 0;

            if (dataHasAbsolutePath) {
                var jsonHost = this.settings.objectData.replace(/https?:\/\//i, "").split(/[/?#]/)[0];

                if (window.location.hostname !== jsonHost) {
                    errorMessage.push((0, _elt.elt)('p', 'Attempted to access cross-origin data without CORS.'), (0, _elt.elt)('p', 'You may need to update your server configuration to support CORS. For help, see the ', (0, _elt.elt)('a', {
                        href: 'https://github.com/DDMAL/diva.js/wiki/Installation#a-note-about-cross-site-requests',
                        target: '_blank'
                    }, 'cross-site request documentation.')));
                }
            }

            this._showError(errorMessage);
        }

        /**
         * @private
         **/

    }, {
        key: '_loadObjectData',
        value: function _loadObjectData(responseData, hashState) {
            var manifest = void 0;

            // TODO improve IIIF detection method
            if (!responseData.hasOwnProperty('@context') && (responseData['@context'].indexOf('iiif') === -1 || responseData['@context'].indexOf('shared-canvas') === -1)) {
                throw new _exceptions.NotAnIIIFManifestException('This does not appear to be a IIIF Manifest.');
            }

            // trigger ManifestDidLoad event
            // FIXME: Why is this triggered before the manifest is parsed? See https://github.com/DDMAL/diva.js/issues/357
            _divaGlobal2.default.Events.publish('ManifestDidLoad', [responseData], this);

            manifest = _imageManifest2.default.fromIIIF(responseData);
            var loadOptions = hashState ? this._getLoadOptionsForState(hashState, manifest) : {};

            this.divaState.viewerCore.setManifest(manifest, loadOptions);
        }

        /**
         * Parse the hash parameters into the format used by getState and setState
         *
         * @private
         **/

    }, {
        key: '_getHashParamState',
        value: function _getHashParamState() {
            var _this2 = this;

            var state = {};

            ['f', 'v', 'z', 'n', 'i', 'p', 'y', 'x'].forEach(function (param) {
                var value = _hashParams2.default.get(param + _this2.settings.hashParamSuffix);

                // `false` is returned if the value is missing
                if (value !== false) state[param] = value;
            });

            // Do some awkward special-casing, since this format is kind of weird.

            // For inFullscreen (f), true and false strings should be interpreted
            // as booleans.
            if (state.f === 'true') state.f = true;else if (state.f === 'false') state.f = false;

            // Convert numerical values to integers, if provided
            ['z', 'n', 'p', 'x', 'y'].forEach(function (param) {
                if (param in state) state[param] = parseInt(state[param], 10);
            });

            return state;
        }

        /**
         * @private
         **/

    }, {
        key: '_getLoadOptionsForState',
        value: function _getLoadOptionsForState(state, manifest) {
            manifest = manifest || this.settings.manifest;

            var options = 'v' in state ? this._getViewState(state.v) : {};

            if ('f' in state) options.inFullscreen = state.f;

            if ('z' in state) options.zoomLevel = state.z;

            if ('n' in state) options.pagesPerRow = state.n;

            // Only change specify the page if state.i or state.p is valid
            var pageIndex = this._getPageIndexForManifest(manifest, state.i);

            if (!(pageIndex >= 0 && pageIndex < manifest.pages.length)) {
                pageIndex = state.p - 1;

                // Possibly NaN
                if (!(pageIndex >= 0 && pageIndex < manifest.pages.length)) pageIndex = null;
            }

            if (pageIndex !== null) {
                var horizontalOffset = parseInt(state.x, 10);
                var verticalOffset = parseInt(state.y, 10);

                options.goDirectlyTo = pageIndex;
                options.horizontalOffset = horizontalOffset;
                options.verticalOffset = verticalOffset;
            }

            return options;
        }

        /**
         * @private
         * */

    }, {
        key: '_getViewState',
        value: function _getViewState(view) {
            switch (view) {
                case 'd':
                    return {
                        inGrid: false,
                        inBookLayout: false
                    };

                case 'b':
                    return {
                        inGrid: false,
                        inBookLayout: true
                    };

                case 'g':
                    return {
                        inGrid: true,
                        inBookLayout: false
                    };

                default:
                    return null;
            }
        }

        /**
         * @private
         * */

    }, {
        key: '_getPageIndexForManifest',
        value: function _getPageIndexForManifest(manifest, filename) {
            var i = void 0;
            var np = manifest.pages.length;

            for (i = 0; i < np; i++) {
                if (manifest.pages[i].f === filename) {
                    return i;
                }
            }

            return -1;
        }

        /**
         * @private
         * */

    }, {
        key: '_getState',
        value: function _getState() {
            var view = void 0;

            if (this.settings.inGrid) {
                view = 'g';
            } else if (this.settings.inBookLayout) {
                view = 'b';
            } else {
                view = 'd';
            }

            var layout = this.divaState.viewerCore.getCurrentLayout();
            var pageOffset = layout.getPageToViewportCenterOffset(this.settings.currentPageIndex, this.viewerState.viewport);

            return {
                'f': this.settings.inFullscreen,
                'v': view,
                'z': this.settings.zoomLevel,
                'n': this.settings.pagesPerRow,
                'i': this.settings.enableFilename ? this.settings.manifest.pages[this.settings.currentPageIndex].f : false,
                'p': this.settings.enableFilename ? false : this.settings.currentPageIndex + 1,
                'y': pageOffset ? pageOffset.y : false,
                'x': pageOffset ? pageOffset.x : false
            };
        }

        /**
         * @private
         **/

    }, {
        key: '_getURLHash',
        value: function _getURLHash() {
            var hashParams = this._getState();
            var hashStringBuilder = [];
            var param = void 0;

            for (param in hashParams) {
                if (hashParams[param] !== false) hashStringBuilder.push(param + this.settings.hashParamSuffix + '=' + encodeURIComponent(hashParams[param]));
            }

            return hashStringBuilder.join('&');
        }

        /**
         * Returns the page index associated with the given filename; must called after setting settings.manifest
         *
         * @private
         **/

    }, {
        key: '_getPageIndex',
        value: function _getPageIndex(filename) {
            return this._getPageIndexForManifest(this.settings.manifest, filename);
        }

        /**
         * @private
         * */

    }, {
        key: '_checkLoaded',
        value: function _checkLoaded() {
            if (!this.viewerState.loaded) {
                console.warn("The viewer is not completely initialized. This is likely because it is still downloading data. To fix this, only call this function if the isReady() method returns true.");
                return false;
            }
            return true;
        }

        /**
         * Called when the fullscreen icon is clicked
         *
         * @private
         **/

    }, {
        key: '_toggleFullscreen',
        value: function _toggleFullscreen() {
            this._reloadViewer({
                inFullscreen: !this.settings.inFullscreen
            });
        }

        /**
         * Toggles between orientations
         *
         * @private
         * */

    }, {
        key: '_togglePageLayoutOrientation',
        value: function _togglePageLayoutOrientation() {
            var verticallyOriented = !this.settings.verticallyOriented;

            //if in grid, switch out of grid
            this._reloadViewer({
                inGrid: false,
                verticallyOriented: verticallyOriented,
                goDirectlyTo: this.settings.currentPageIndex,
                verticalOffset: this.divaState.viewerCore.getYOffset(),
                horizontalOffset: this.divaState.viewerCore.getXOffset()
            });

            return verticallyOriented;
        }

        /**
         * Called when the change view icon is clicked
         *
         * @private
         **/

    }, {
        key: '_changeView',
        value: function _changeView(destinationView) {
            switch (destinationView) {
                case 'document':
                    return this._reloadViewer({
                        inGrid: false,
                        inBookLayout: false
                    });

                case 'book':
                    return this._reloadViewer({
                        inGrid: false,
                        inBookLayout: true
                    });

                case 'grid':
                    return this._reloadViewer({
                        inGrid: true
                    });

                default:
                    return false;
            }
        }

        /**
         * @private
         *
         * @param {Number} pageIndex - 0-based page index.
         * @param {Number} xAnchor - x coordinate to jump to on resulting page.
         * @param {Number} yAnchor - y coordinate to jump to on resulting page.
         * @returns {Boolean} - Whether the jump was successful.
         **/

    }, {
        key: '_gotoPageByIndex',
        value: function _gotoPageByIndex(pageIndex, xAnchor, yAnchor) {
            var pidx = parseInt(pageIndex, 10);

            if (this._isPageIndexValid(pidx)) {
                var xOffset = this.divaState.viewerCore.getXOffset(pidx, xAnchor);
                var yOffset = this.divaState.viewerCore.getYOffset(pidx, yAnchor);

                this.viewerState.renderer.goto(pidx, yOffset, xOffset);
                return true;
            }

            return false;
        }

        /**
         * Check if a page index is valid
         *
         * @private
         * @param {Number} pageIndex - Numeric (0-based) page index
         * @return {Boolean} whether the page index is valid or not.
         */

    }, {
        key: '_isPageIndexValid',
        value: function _isPageIndexValid(pageIndex) {
            return this.settings.manifest.isPageValid(pageIndex, this.settings.showNonPagedPages);
        }

        /**
         * Given a pageX and pageY value, returns either the page visible at that (x,y)
         * position or -1 if no page is.
         *
         * @private
         */

    }, {
        key: '_getPageIndexForPageXYValues',
        value: function _getPageIndexForPageXYValues(pageX, pageY) {
            //get the four edges of the outer element
            var outerOffset = this.viewerState.outerElement.getBoundingClientRect();
            var outerTop = outerOffset.top;
            var outerLeft = outerOffset.left;
            var outerBottom = outerOffset.bottom;
            var outerRight = outerOffset.right;

            //if the clicked position was outside the diva-outer object, it was not on a visible portion of a page
            if (pageX < outerLeft || pageX > outerRight) return -1;

            if (pageY < outerTop || pageY > outerBottom) return -1;

            //navigate through all diva page objects
            var pages = document.getElementsByClassName('diva-page');
            var curPageIdx = pages.length;
            while (curPageIdx--) {
                //get the offset for each page
                var curPage = pages[curPageIdx];
                var curOffset = curPage.getBoundingClientRect();

                //if this point is outside the horizontal boundaries of the page, continue
                if (pageX < curOffset.left || pageX > curOffset.right) continue;

                //same with vertical boundaries
                if (pageY < curOffset.top || pageY > curOffset.bottom) continue;

                //if we made it through the above two, we found the page we're looking for
                return curPage.getAttribute('data-index');
            }

            //if we made it through that entire while loop, we didn't click on a page
            return -1;
        }

        /**
         * @private
         **/

    }, {
        key: '_reloadViewer',
        value: function _reloadViewer(newOptions) {
            return this.divaState.viewerCore.reload(newOptions);
        }

        /**
         * @private
         */

    }, {
        key: '_getCurrentURL',
        value: function _getCurrentURL() {
            return location.protocol + '//' + location.host + location.pathname + location.search + '#' + this._getURLHash();
        }

        /**
         * ===============================================
         *                PUBLIC FUNCTIONS
         * ===============================================
         **/

        /**
         *  Activate this instance of diva via the active Diva controller.
         *
         *  @public
         */

    }, {
        key: 'activate',
        value: function activate() {
            this.viewerState.isActiveDiva = true;
        }

        /**
         * Change the object (objectData) parameter currently being rendered by Diva.
         *
         * @public
         * @params {object} objectData - An IIIF Manifest object OR a URL to a IIIF manifest.
         */

    }, {
        key: 'changeObject',
        value: function changeObject(objectData) {
            this.viewerState.loaded = false;
            this.divaState.viewerCore.clear();

            if (this.viewerState.renderer) this.viewerState.renderer.destroy();

            this.viewerState.options.objectData = objectData;

            this._loadOrFetchObjectData();
        }

        /**
         * Change views. Takes 'document', 'book', or 'grid' to specify which view to switch into
         *
         * @public
         * @params {string} destinationView - the destination view to change to.
         */

    }, {
        key: 'changeView',
        value: function changeView(destinationView) {
            this._changeView(destinationView);
        }

        /**
         * Close all popups on the toolbar.
         *
         * @public
         **/

    }, {
        key: 'closePopups',
        value: function closePopups() {
            this.divaState.toolbar.closePopups();
        }

        /**
         *  Deactivate this diva instance through the active Diva controller.
         *
         *  @public
         **/

    }, {
        key: 'deactivate',
        value: function deactivate() {
            this.viewerState.isActiveDiva = false;
        }

        /**
         * Destroys this instance, tells plugins to do the same
         *
         * @public
         **/

    }, {
        key: 'destroy',
        value: function destroy() {
            this.divaState.viewerCore.destroy();
        }

        /**
         * Disables document dragging, scrolling (by keyboard if set), and zooming by double-clicking
         *
         * @public
         **/

    }, {
        key: 'disableScrollable',
        value: function disableScrollable() {
            this.divaState.viewerCore.disableScrollable();
        }

        /**
         * Re-enables document dragging, scrolling (by keyboard if set), and zooming by double-clicking
         *
         * @public
         **/

    }, {
        key: 'enableScrollable',
        value: function enableScrollable() {
            this.divaState.viewerCore.enableScrollable();
        }

        /**
         * Enter fullscreen mode if currently not in fullscreen mode. If currently in fullscreen
         * mode this will have no effect.
         *
         * This function will work even if enableFullscreen is set to false in the options.
         *
         * @public
         * @returns {boolean} - Whether the switch to fullscreen was successful or not.
         **/

    }, {
        key: 'enterFullscreenMode',
        value: function enterFullscreenMode() {
            if (!this.settings.inFullscreen) {
                this._toggleFullscreen();
                return true;
            }

            return false;
        }

        /**
         * Enter grid view if currently not in grid view. If currently in grid view mode
         * this will have no effect.
         *
         * @public
         * @returns {boolean} - Whether the switch to grid view was successful or not.
         **/

    }, {
        key: 'enterGridView',
        value: function enterGridView() {
            if (!this.settings.inGrid) {
                this._changeView('grid');
                return true;
            }

            return false;
        }

        /**
         * Return the current URL for the viewer, including the hash parameters reflecting
         * the current state of the viewer.
         *
         * @public
         * @returns {string} - The URL for the current view state.
         * */

    }, {
        key: 'getCurrentURL',
        value: function getCurrentURL() {
            return this._getCurrentURL();
        }

        /**
         * Returns the title of the document, based on the label in the IIIF manifest.
         *
         * @public
         * @returns {string} - The current title of the object from the label key in the IIIF Manifest.
         **/

    }, {
        key: 'getItemTitle',
        value: function getItemTitle() {
            return this.settings.manifest.itemTitle;
        }

        /**
         * Get the canvas identifier for the currently visible page.
         *
         * @public
         * @returns {string} - The URI of the currently visible canvas.
         **/

    }, {
        key: 'getCurrentCanvas',
        value: function getCurrentCanvas() {
            return this.settings.manifest.pages[this.settings.currentPageIndex].canvas;
        }

        /**
         * Returns the dimensions of the current page at the current zoom level. Also works in
         * grid view.
         *
         * @public
         * @returns {object} - An object containing the current page dimensions at the current zoom level.
         **/

    }, {
        key: 'getCurrentPageDimensionsAtCurrentZoomLevel',
        value: function getCurrentPageDimensionsAtCurrentZoomLevel() {
            return this.getPageDimensionsAtCurrentZoomLevel(this.settings.currentPageIndex);
        }

        /**
         * Returns the current filename (deprecated). Returns the URI for current page.
         *
         * @public
         * @deprecated
         * @returns {string} - The URI for the current page image.
         **/

    }, {
        key: 'getCurrentPageFilename',
        value: function getCurrentPageFilename() {
            console.warn('This method will be deprecated in the next version of Diva. Please use getCurrentPageURI instead.');
            return this.settings.manifest.pages[this.settings.currentPageIndex].f;
        }

        /**
         * Returns the current URI for the visible page.
         *
         * @public
         * @returns {string} - The URI for the current page image.
         **/

    }, {
        key: 'getCurrentPageURI',
        value: function getCurrentPageURI() {
            return this.settings.manifest.pages[this.settings.currentPageIndex].f;
        }

        /**
         * Returns the 0-based index for the current page.
         *
         * @public
         * @returns {number} - The 0-based index for the currently visible page.
         **/

    }, {
        key: 'getCurrentPageIndex',
        value: function getCurrentPageIndex() {
            return this.settings.currentPageIndex;
        }

        /**
         * Shortcut to getPageOffset for current page.
         *
         * @public
         * @returns {} -
         * */

    }, {
        key: 'getCurrentPageOffset',
        value: function getCurrentPageOffset() {
            return this.getPageOffset(this.settings.currentPageIndex);
        }

        /**
         * Returns an array of all filenames in the document. Deprecated.
         *
         * @public
         * @deprecated
         * @returns {Array} - An array of all the URIs in the document.
         * */

    }, {
        key: 'getFilenames',
        value: function getFilenames() {
            console.warn('This will be removed in the next version of Diva. Use getAllPageURIs instead.');

            return this.settings.manifest.pages.map(function (pg) {
                return pg.f;
            });
        }

        /**
         * Returns an array of all page image URIs in the document.
         *
         * @public
         * @returns {Array} - An array of all the URIs in the document.
         * */

    }, {
        key: 'getAllPageURIs',
        value: function getAllPageURIs() {
            return this.settings.manifest.pages.map(function (pg) {
                return pg.f;
            });
        }

        /**
         * Get the number of grid pages per row.
         *
         * @public
         * @returns {number} - The number of grid pages per row.
         **/

    }, {
        key: 'getGridPagesPerRow',
        value: function getGridPagesPerRow() {
            // TODO(wabain): Add test case
            return this.settings.pagesPerRow;
        }

        /**
         * Get the instance ID number.
         *
         * @public
         * @returns {number} - The instance ID.
         * */
        //

    }, {
        key: 'getInstanceId',
        value: function getInstanceId() {
            return this.settings.ID;
        }

        /**
         * Get the instance selector for this instance. This is the selector for the parent
         * div.
         *
         * @public
         * @returns {string} - The viewport selector.
         * */

    }, {
        key: 'getInstanceSelector',
        value: function getInstanceSelector() {
            console.log(this);
            return this.divaState.viewerCore.selector;
        }

        /**
         * Gets the maximum zoom level for the entire document.
         *
         * @public
         * @returns {number} - The maximum zoom level for the document
         * */

    }, {
        key: 'getMaxZoomLevel',
        value: function getMaxZoomLevel() {
            return this.settings.maxZoomLevel;
        }

        /**
         * Gets the max zoom level for a given page.
         *
         * @public
         * @param {number} pageIdx - The 0-based index number for the page.
         * @returns {number} - The maximum zoom level for that page.
         * */

    }, {
        key: 'getMaxZoomLevelForPage',
        value: function getMaxZoomLevelForPage(pageIdx) {
            if (!this._checkLoaded()) return false;

            return this.settings.manifest.pages[pageIdx].m;
        }

        /**
         * Gets the minimum zoom level for the entire document.
         *
         * @public
         * @returns {number} - The minimum zoom level for the document
         * */

    }, {
        key: 'getMinZoomLevel',
        value: function getMinZoomLevel() {
            return this.settings.minZoomLevel;
        }

        /**
         * Gets the number of pages in the document.
         *
         * @public
         * @returns {number} - The number of pages in the document.
         * */

    }, {
        key: 'getNumberOfPages',
        value: function getNumberOfPages() {
            if (!this._checkLoaded()) return false;

            return this.settings.numPages;
        }

        /**
         * If a canvas has multiple images defined, returns the non-primary image.
         *
         * @public
         * @params {number} pageIndex - The page index for which to return the other images.
         * @returns {object} An object containing the other images.
         **/

    }, {
        key: 'getOtherImages',
        value: function getOtherImages(pageIndex) {
            return this.settings.manifest.pages[pageIndex].otherImages;
        }

        /**
         * Get page dimensions in the current view and zoom level
         *
         * @public
         * @params {number} pageIndex - A valid 0-based page index
         * @returns {object} - An object containing the dimensions of the page
         * */

    }, {
        key: 'getPageDimensions',
        value: function getPageDimensions(pageIndex) {
            if (!this._checkLoaded()) return null;

            return this.divaState.viewerCore.getCurrentLayout().getPageDimensions(pageIndex);
        }

        /**
         * Get page dimensions at a given zoom level
         *
         * @public
         * @params {number} pageIdx - A valid 0-based page index
         * @params {number} zoomLevel - A candidate zoom level.
         * @returns {object} - An object containing the dimensions of the page at the given zoom level.
         **/

    }, {
        key: 'getPageDimensionsAtZoomLevel',
        value: function getPageDimensionsAtZoomLevel(pageIdx, zoomLevel) {
            if (!this._checkLoaded()) return false;

            if (zoomLevel > this.settings.maxZoomLevel) zoomLevel = this.settings.maxZoomLevel;

            var pg = this.settings.manifest.pages[parseInt(pageIdx, 10)];
            var pgAtZoom = pg.d[parseInt(zoomLevel, 10)];

            return {
                width: pgAtZoom.w,
                height: pgAtZoom.h
            };
        }

        /**
         * Returns the dimensions of a given page at the current zoom level.
         * Also works in Grid view
         *
         * @public
         * @param {number} pageIndex - The 0-based page index
         * @returns {object} - An object containing the page dimensions at the current zoom level.
         * */

    }, {
        key: 'getPageDimensionsAtCurrentZoomLevel',
        value: function getPageDimensionsAtCurrentZoomLevel(pageIndex) {
            var pidx = parseInt(pageIndex, 10);

            if (!this._isPageIndexValid(pidx)) throw new Error('Invalid Page Index');

            return this.divaState.viewerCore.getCurrentLayout().getPageDimensions(pidx);
        }

        /**
         * Returns a URL for the image of the page at the given index. The
         * optional size parameter supports setting the image width or height
         * (default is full-sized).
         *
         * @public
         * @params {number} pageIndex - 0-based page index
         * @params {?object} size - an object containing width and height information
         * @returns {string} - The IIIF URL for a given page at an optional size
         */

    }, {
        key: 'getPageImageURL',
        value: function getPageImageURL(pageIndex, size) {
            return this.settings.manifest.getPageImageURL(pageIndex, size);
        }

        /**
         * Given a set of co-ordinates (e.g., from a mouse click), return the 0-based page index
         * for which it matches.
         *
         * @public
         * @params {number} pageX - The x co-ordinate
         * @params {number} pageY - The y co-ordinate
         * @returns {number} - The page index matching the co-ordinates.
         * */

    }, {
        key: 'getPageIndexForPageXYValues',
        value: function getPageIndexForPageXYValues(pageX, pageY) {
            return this._getPageIndexForPageXYValues(pageX, pageY);
        }

        /**
         * Returns distance between the northwest corners of diva-inner and page index.
         *
         * @public
         * @params {number} pageIndex - The 0-based page index
         * @params {?options} options - A set of options to pass in.
         * @returns {object} - The offset between the upper left corner and the page.
         *
         * */

    }, {
        key: 'getPageOffset',
        value: function getPageOffset(pageIndex, options) {
            var region = this.divaState.viewerCore.getPageRegion(pageIndex, options);

            return {
                top: region.top,
                left: region.left
            };
        }

        /**
         * Get the instance settings.
         *
         * @public
         * @returns {object} - The current instance settings.
         * */

    }, {
        key: 'getSettings',
        value: function getSettings() {
            return this.settings;
        }

        /**
         * Get an object representing the complete state of the viewer.
         *
         * @public
         * @returns {object} - The current instance state.
         * */

    }, {
        key: 'getState',
        value: function getState() {
            return this._getState();
        }

        /**
         * Get the current zoom level.
         *
         * @public
         * @returns {number} - The current zoom level.
         * */

    }, {
        key: 'getZoomLevel',
        value: function getZoomLevel() {
            return this.settings.zoomLevel;
        }

        /**
         *  Go to a particular page (with indexing starting at 0).
         *  The (xAnchor) side of the page will be anchored to the (xAnchor) side of the diva-outer element
         *
         *  @public
         *  @params {number} pageIndex - 0-based page index.
         *  @params {?string} xAnchor - may either be "left", "right", or default "center"
         *  @params {?string} yAnchor - may either be "top", "bottom", or default "center"; same process as xAnchor.
         *  @returns {boolean} - True if the page index is valid; false if it is not.
         * */

    }, {
        key: 'gotoPageByIndex',
        value: function gotoPageByIndex(pageIndex, xAnchor, yAnchor) {
            this._gotoPageByIndex(pageIndex, xAnchor, yAnchor);
        }

        /**
         * Given a canvas label, attempt to go to that page. If no label was found.
         * the label will be attempted to match against the page index.
         *
         * @public
         * @params {string} label - The label to search on.
         * @params {?string} xAnchor - may either be "left", "right", or default "center"
         * @params {?string} yAnchor - may either be "top", "bottom", or default "center"
         * @returns {boolean} - True if the page index is valid; false if it is not.
         * */

    }, {
        key: 'gotoPageByLabel',
        value: function gotoPageByLabel(label, xAnchor, yAnchor) {
            var pages = this.settings.manifest.pages;
            var llc = label.toLowerCase();

            for (var i = 0, len = pages.length; i < len; i++) {
                if (pages[i].l.toLowerCase().indexOf(llc) > -1) return this._gotoPageByIndex(i, xAnchor, yAnchor);
            }

            var pageIndex = parseInt(label, 10) - 1;
            return this._gotoPageByIndex(pageIndex, xAnchor, yAnchor);
        }

        /**
         * Jump to a page based on its filename. Deprecated. Use gotoPageByURI instead.
         *
         * @public
         * @params {string} filename - The filename of the image to jump to.
         * @params {?string} xAnchor - may either be "left", "right", or default "center"
         * @params {?string} yAnchor - may either be "top", "bottom", or default "center"
         * @returns {boolean} true if successful and false if the filename is not found.
        */

    }, {
        key: 'gotoPageByName',
        value: function gotoPageByName(filename, xAnchor, yAnchor) {
            console.warn('This method will be removed in the next version of Diva.js. Use gotoPageByURI instead.');
            var pageIndex = this._getPageIndex(filename);
            return this._gotoPageByIndex(pageIndex, xAnchor, yAnchor);
        }

        /**
         * Jump to a page based on its URI.
         *
         * @public
         * @params {string} uri - The URI of the image to jump to.
         * @params {?string} xAnchor - may either be "left", "right", or default "center"
         * @params {?string} yAnchor - may either be "top", "bottom", or default "center"
         * @returns {boolean} true if successful and false if the URI is not found.
         */

    }, {
        key: 'gotoPageByURI',
        value: function gotoPageByURI(uri, xAnchor, yAnchor) {
            var pageIndex = this._getPageIndex(uri);
            return this._gotoPageByIndex(pageIndex, xAnchor, yAnchor);
        }

        /**
         * Whether the page has other images to display.
         *
         * @public
         * @params {number} pageIndex - The 0-based page index
         * @returns {boolean} Whether the page has other images to display.
         **/

    }, {
        key: 'hasOtherImages',
        value: function hasOtherImages(pageIndex) {
            return this.settings.manifest.pages[pageIndex].otherImages === true;
        }

        /**
         * Hides the pages that are marked "non-paged" in the IIIF manifest.
         *
         * @public
         **/

    }, {
        key: 'hideNonPagedPages',
        value: function hideNonPagedPages() {
            this._reloadViewer({ showNonPagedPages: false });
        }

        /**
         * Is the viewer currently in full-screen mode?
         *
         * @public
         * @returns {boolean} - Whether the viewer is in fullscreen mode.
         **/

    }, {
        key: 'isInFullscreen',
        value: function isInFullscreen() {
            return this.settings.inFullscreen;
        }

        /**
         * Check if a page index is within the range of the document
         *
         * @public
         * @returns {boolean} - Whether the page index is valid.
         **/

    }, {
        key: 'isPageIndexValid',
        value: function isPageIndexValid(pageIndex) {
            return this._isPageIndexValid(pageIndex);
        }

        /**
         * Determines if a page is currently in the viewport
         *
         * @public
         * @params {number} pageIndex - The 0-based page index
         * @returns {boolean} - Whether the page is currently in the viewport.
         **/

    }, {
        key: 'isPageInViewport',
        value: function isPageInViewport(pageIndex) {
            return this.viewerState.renderer.isPageVisible(pageIndex);
        }

        /**
         * Whether the Diva viewer has been fully initialized.
         *
         * @public
         * @returns {boolean} - True if the viewer is initialized; false otherwise.
         **/

    }, {
        key: 'isReady',
        value: function isReady() {
            return this.viewerState.loaded;
        }

        /**
         * Check if something (e.g. a highlight box on a particular page) is visible
         *
         * @public
         * @params {number} pageIndex - The 0-based page index
         * @params {number} leftOffset - The distance of the region from the left of the viewport
         * @params {number} topOffset - The distance of the region from the top of the viewport
         * @params {number} width - The width of the region
         * @params {number} height - The height of the region
         * @returns {boolean} - Whether the region is in the viewport.
         **/

    }, {
        key: 'isRegionInViewport',
        value: function isRegionInViewport(pageIndex, leftOffset, topOffset, width, height) {
            var layout = this.divaState.viewerCore.getCurrentLayout();

            if (!layout) return false;

            var offset = layout.getPageOffset(pageIndex);

            var top = offset.top + topOffset;
            var left = offset.left + leftOffset;

            return this.viewerState.viewport.intersectsRegion({
                top: top,
                bottom: top + height,
                left: left,
                right: left + width
            });
        }

        /**
         * Whether the page layout is vertically or horizontally oriented.
         *
         * @public
         * @returns {boolean} - True if vertical; false if horizontal.
         **/

    }, {
        key: 'isVerticallyOriented',
        value: function isVerticallyOriented() {
            return this.settings.verticallyOriented;
        }

        /**
         * Leave fullscreen mode if currently in fullscreen mode.
         *
         * @public
         * @returns {boolean} - true if in fullscreen mode intitially, false otherwise
         **/

    }, {
        key: 'leaveFullscreenMode',
        value: function leaveFullscreenMode() {
            if (this.settings.inFullscreen) {
                this.toggleFullscreen();
                return true;
            }

            return false;
        }

        /**
         * Leave grid view if currently in grid view.
         *
         * @public
         * @returns {boolean} - true if in grid view initially, false otherwise
         **/

    }, {
        key: 'leaveGridView',
        value: function leaveGridView() {
            if (this.settings.inGrid) {
                this._reloadViewer({ inGrid: false });
                return true;
            }

            return false;
        }

        /**
         * Set the number of grid pages per row.
         *
         * @public
         * @params {number} pagesPerRow - The number of pages per row
         * @returns {boolean} - True if the operation was successful.
         **/

    }, {
        key: 'setGridPagesPerRow',
        value: function setGridPagesPerRow(pagesPerRow) {
            // TODO(wabain): Add test case
            if (!this.divaState.viewerCore.isValidOption('pagesPerRow', pagesPerRow)) return false;

            return this._reloadViewer({
                inGrid: true,
                pagesPerRow: pagesPerRow
            });
        }

        /**
         * Align this diva instance with a state object (as returned by getState)
         *
         * @public
         * @params {object} state - A Diva state object.
         * @returns {boolean} - True if the operation was successful.
         **/

    }, {
        key: 'setState',
        value: function setState(state) {
            this._reloadViewer(this._getLoadOptionsForState(state));
        }

        /**
         * Show non-paged pages.
         *
         * @public
         * @returns {boolean} - True if the operation was successful.
         **/

    }, {
        key: 'showNonPagedPages',
        value: function showNonPagedPages() {
            this._reloadViewer({ showNonPagedPages: true });
        }

        /**
         * Sets the zoom level.
         *
         * @public
         * @returns {boolean} - True if the operation was successful.
         **/

    }, {
        key: 'setZoomLevel',
        value: function setZoomLevel(zoomLevel) {
            if (this.settings.inGrid) {
                this._reloadViewer({
                    inGrid: false
                });
            }

            return this.divaState.viewerCore.zoom(zoomLevel);
        }

        /**
         * Toggle fullscreen mode.
         *
         * @public
         * @returns {boolean} - True if the operation was successful.
         **/

    }, {
        key: 'toggleFullscreenMode',
        value: function toggleFullscreenMode() {
            this._toggleFullscreen();
        }

        /**
         * Show/Hide non-paged pages
         *
         * @public
         * @returns {boolean} - True if the operation was successful.
         **/

    }, {
        key: 'toggleNonPagedPagesVisibility',
        value: function toggleNonPagedPagesVisibility() {
            this._reloadViewer({
                showNonPagedPages: !this.settings.showNonPagedPages
            });
        }

        //Changes between horizontal layout and vertical layout. Returns true if document is now vertically oriented, false otherwise.

    }, {
        key: 'toggleOrientation',
        value: function toggleOrientation() {
            return this._togglePageLayoutOrientation();
        }

        /**
         * Translates a measurement from the zoom level on the largest size
         * to one on the current zoom level.
         *
         * For example, a point 1000 on an image that is on zoom level 2 of 5
         * translates to a position of 111.111... (1000 / (5 - 2)^2).
         *
         * Works for a single pixel co-ordinate or a dimension (e.g., translates a box
         * that is 1000 pixels wide on the original to one that is 111.111 pixels wide
         * on the current zoom level).
         *
         * @public
         * @params {number} position - A point on the max zoom level
         * @returns {number} - The same point on the current zoom level.
        */

    }, {
        key: 'translateFromMaxZoomLevel',
        value: function translateFromMaxZoomLevel(position) {
            var zoomDifference = this.settings.maxZoomLevel - this.settings.zoomLevel;
            return position / Math.pow(2, zoomDifference);
        }

        /**
         * Translates a measurement from the current zoom level to the position on the
         * largest zoom level.
         *
         * Works for a single pixel co-ordinate or a dimension (e.g., translates a box
         * that is 111.111 pixels wide on the current image to one that is 1000 pixels wide
         * on the current zoom level).
         *
         * @public
         * @params {number} position - A point on the current zoom level
         * @returns {number} - The same point on the max zoom level.
        */

    }, {
        key: 'translateToMaxZoomLevel',
        value: function translateToMaxZoomLevel(position) {
            var zoomDifference = this.settings.maxZoomLevel - this.settings.zoomLevel;

            // if there is no difference, it's a box on the max zoom level and
            // we can just return the position.
            if (zoomDifference === 0) return position;

            return position * Math.pow(2, zoomDifference);
        }

        /**
         * Zoom in.
         *
         * @public
         * @returns {boolean} - false if it's at the maximum zoom
         **/

    }, {
        key: 'zoomIn',
        value: function zoomIn() {
            return this.setZoomLevel(this.settings.zoomLevel + 1);
        }

        /**
         * Zoom out.
         * @returns {boolean} - false if it's at the minimum zoom
         **/

    }, {
        key: 'zoomOut',
        value: function zoomOut() {
            return this.setZoomLevel(this.settings.zoomLevel - 1);
        }
    }]);

    return Diva;
}();

exports.default = Diva;

/**
 * Make `Diva` available in the global context.
 * */

(function (global) {
    global.Diva = global.Diva || Diva;
    global.Diva.Events = _divaGlobal2.default.Events;
})(window);

/***/ }),

/***/ "./source/js/document-handler.js":
/*!***************************************!*\
  !*** ./source/js/document-handler.js ***!
  \***************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _lodash = __webpack_require__(/*! lodash.maxby */ "./node_modules/lodash.maxby/index.js");

var _lodash2 = _interopRequireDefault(_lodash);

var _pageToolsOverlay = __webpack_require__(/*! ./page-tools-overlay */ "./source/js/page-tools-overlay.js");

var _pageToolsOverlay2 = _interopRequireDefault(_pageToolsOverlay);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var DocumentHandler = function () {
    function DocumentHandler(viewerCore) {
        _classCallCheck(this, DocumentHandler);

        this._viewerCore = viewerCore;
        this._viewerState = viewerCore.getInternalState();
        this._overlays = [];

        if (this._viewerCore.getPageTools().length) {
            var numPages = viewerCore.getSettings().numPages;

            for (var i = 0; i < numPages; i++) {
                var overlay = new _pageToolsOverlay2.default(i, viewerCore);
                this._overlays.push(overlay);
                this._viewerCore.addPageOverlay(overlay);
            }
        }
    }

    // USER EVENTS


    _createClass(DocumentHandler, [{
        key: 'onDoubleClick',
        value: function onDoubleClick(event, coords) {
            var settings = this._viewerCore.getSettings();
            var newZoomLevel = event.ctrlKey ? settings.zoomLevel - 1 : settings.zoomLevel + 1;

            var position = this._viewerCore.getPagePositionAtViewportOffset(coords);
            this._viewerCore.zoom(newZoomLevel, position);
        }
    }, {
        key: 'onPinch',
        value: function onPinch(event, coords, startDistance, endDistance) {
            // FIXME: Do this check in a way which is less spaghetti code-y
            var viewerState = this._viewerCore.getInternalState();
            var settings = this._viewerCore.getSettings();

            var newZoomLevel = Math.log(Math.pow(2, settings.zoomLevel) * endDistance / (startDistance * Math.log(2))) / Math.log(2);
            newZoomLevel = Math.max(settings.minZoomLevel, newZoomLevel);
            newZoomLevel = Math.min(settings.maxZoomLevel, newZoomLevel);

            if (newZoomLevel === settings.zoomLevel) {
                return;
            }

            var position = this._viewerCore.getPagePositionAtViewportOffset(coords);

            var layout = this._viewerCore.getCurrentLayout();
            var centerOffset = layout.getPageToViewportCenterOffset(position.anchorPage, viewerState.viewport);
            var scaleRatio = 1 / Math.pow(2, settings.zoomLevel - newZoomLevel);

            this._viewerCore.reload({
                zoomLevel: newZoomLevel,
                goDirectlyTo: position.anchorPage,
                horizontalOffset: centerOffset.x - position.offset.left + position.offset.left * scaleRatio,
                verticalOffset: centerOffset.y - position.offset.top + position.offset.top * scaleRatio
            });
        }

        // VIEW EVENTS

    }, {
        key: 'onViewWillLoad',
        value: function onViewWillLoad() {
            this._viewerCore.publish('DocumentWillLoad', this._viewerCore.getSettings());
        }
    }, {
        key: 'onViewDidLoad',
        value: function onViewDidLoad() {
            // TODO: Should only be necessary to handle changes on view update, not
            // initial load
            this._handleZoomLevelChange();

            var currentPageIndex = this._viewerCore.getSettings().currentPageIndex;
            var fileName = this._viewerCore.getPageName(currentPageIndex);
            this._viewerCore.publish("DocumentDidLoad", currentPageIndex, fileName);
        }
    }, {
        key: 'onViewDidUpdate',
        value: function onViewDidUpdate(renderedPages, targetPage) {
            var currentPage = targetPage !== null ? targetPage : getCentermostPage(renderedPages, this._viewerCore.getCurrentLayout(), this._viewerCore.getViewport());

            // Don't change the current page if there is no page in the viewport
            // FIXME: Would be better to fall back to the page closest to the viewport
            if (currentPage !== null) {
                this._viewerCore.setCurrentPage(currentPage);
            }

            if (targetPage !== null) {
                this._viewerCore.publish("ViewerDidJump", targetPage);
            }

            this._handleZoomLevelChange();
        }
    }, {
        key: '_handleZoomLevelChange',
        value: function _handleZoomLevelChange() {
            var viewerState = this._viewerState;
            var zoomLevel = viewerState.options.zoomLevel;

            // If this is not the initial load, trigger the zoom events
            if (viewerState.oldZoomLevel !== zoomLevel && viewerState.oldZoomLevel >= 0) {
                if (viewerState.oldZoomLevel < zoomLevel) {
                    this._viewerCore.publish("ViewerDidZoomIn", zoomLevel);
                } else {
                    this._viewerCore.publish("ViewerDidZoomOut", zoomLevel);
                }

                this._viewerCore.publish("ViewerDidZoom", zoomLevel);
            }

            viewerState.oldZoomLevel = zoomLevel;
        }
    }, {
        key: 'destroy',
        value: function destroy() {
            var _this = this;

            this._overlays.forEach(function (overlay) {
                _this._viewerCore.removePageOverlay(overlay);
            }, this);
        }
    }]);

    return DocumentHandler;
}();

exports.default = DocumentHandler;


function getCentermostPage(renderedPages, layout, viewport) {
    var centerY = viewport.top + viewport.height / 2;
    var centerX = viewport.left + viewport.width / 2;

    // Find the minimum distance from the viewport center to a page.
    // Compute minus the squared distance from viewport center to the page's border.
    // http://gamedev.stackexchange.com/questions/44483/how-do-i-calculate-distance-between-a-point-and-an-axis-aligned-rectangle
    var centerPage = (0, _lodash2.default)(renderedPages, function (pageIndex) {
        var dims = layout.getPageDimensions(pageIndex);
        var imageOffset = layout.getPageOffset(pageIndex, { excludePadding: false });

        var midX = imageOffset.left + dims.height / 2;
        var midY = imageOffset.top + dims.width / 2;

        var dx = Math.max(Math.abs(centerX - midX) - dims.width / 2, 0);
        var dy = Math.max(Math.abs(centerY - midY) - dims.height / 2, 0);

        return -(dx * dx + dy * dy);
    });

    return centerPage != null ? centerPage : null;
}

/***/ }),

/***/ "./source/js/document-layout.js":
/*!**************************************!*\
  !*** ./source/js/document-layout.js ***!
  \**************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/**
 * Translate page layouts, as generated by page-layouts, into an
 * object which computes layout information for the document as
 * a whole.
 */
var DocumentLayout = function () {
    function DocumentLayout(config, zoomLevel) {
        _classCallCheck(this, DocumentLayout);

        var computedLayout = getComputedLayout(config, zoomLevel);

        this.dimensions = computedLayout.dimensions;
        this.pageGroups = computedLayout.pageGroups;
        this._pageLookup = getPageLookup(computedLayout.pageGroups);
    }

    /**
     * @typedef {Object} PageInfo
     * @property {number} index
     * @property {{index, dimensions, pages, region, padding}} group
     * @property {{height: number, width: number}} dimensions
     * @property {{top: number, left: number}} groupOffset
     */

    /**
     * @param pageIndex
     * @returns {PageInfo|null}
     */


    _createClass(DocumentLayout, [{
        key: 'getPageInfo',
        value: function getPageInfo(pageIndex) {
            return this._pageLookup[pageIndex] || null;
        }

        /**
         * Get the dimensions of a page
         *
         * @param pageIndex
         * @returns {{height: number, width: number}}
         */

    }, {
        key: 'getPageDimensions',
        value: function getPageDimensions(pageIndex) {
            if (!this._pageLookup || !this._pageLookup[pageIndex]) return null;

            var region = getPageRegionFromPageInfo(this._pageLookup[pageIndex]);

            return {
                height: region.bottom - region.top,
                width: region.right - region.left
            };
        }

        // TODO(wabain): Get rid of this; it's a subset of the page region, so
        // give that instead
        /**
         * Get the top-left coordinates of a page, including*** padding
         *
         * @param pageIndex
         * @param options
         * @returns {{top: number, left: number} | null}
         */

    }, {
        key: 'getPageOffset',
        value: function getPageOffset(pageIndex, options) {
            var region = this.getPageRegion(pageIndex, options);

            if (!region) return null;

            return {
                top: region.top,
                left: region.left
            };
        }
    }, {
        key: 'getPageRegion',
        value: function getPageRegion(pageIndex, options) {
            var pageInfo = this._pageLookup[pageIndex];

            if (!pageInfo) return null;

            var region = getPageRegionFromPageInfo(pageInfo);

            if (options && options.excludePadding) {
                // FIXME?
                var padding = pageInfo.group.padding;

                return {
                    top: region.top + padding.top,
                    left: region.left + padding.left,
                    bottom: region.bottom,
                    right: region.right
                };
            }

            return region;
        }

        /**
         * Get the distance from the top-right of the page to the center of the
         * specified viewport region
         *
         * @param pageIndex
         * @param viewport {{top: number, left: number, bottom: number, right: number}}
         * @returns {{x: number, y: number}}
         */

    }, {
        key: 'getPageToViewportCenterOffset',
        value: function getPageToViewportCenterOffset(pageIndex, viewport) {
            var scrollLeft = viewport.left;
            var elementWidth = viewport.right - viewport.left;

            var offset = this.getPageOffset(pageIndex);

            var x = scrollLeft - offset.left + parseInt(elementWidth / 2, 10);

            var scrollTop = viewport.top;
            var elementHeight = viewport.bottom - viewport.top;

            var y = scrollTop - offset.top + parseInt(elementHeight / 2, 10);

            return {
                x: x,
                y: y
            };
        }
    }]);

    return DocumentLayout;
}();

exports.default = DocumentLayout;


function getPageRegionFromPageInfo(page) {
    var top = page.groupOffset.top + page.group.region.top;
    var bottom = top + page.dimensions.height;
    var left = page.groupOffset.left + page.group.region.left;
    var right = left + page.dimensions.width;

    return {
        top: top,
        bottom: bottom,
        left: left,
        right: right
    };
}

function getPageLookup(pageGroups) {
    var pageLookup = {};

    pageGroups.forEach(function (group) {
        group.pages.forEach(function (page) {
            pageLookup[page.index] = {
                index: page.index,
                group: group,
                dimensions: page.dimensions,
                groupOffset: page.groupOffset
            };
        });
    });

    return pageLookup;
}

function getComputedLayout(config, zoomLevel) {
    var scaledLayouts = zoomLevel === null ? config.pageLayouts : getScaledPageLayouts(config, zoomLevel);

    var documentSecondaryExtent = getExtentAlongSecondaryAxis(config, scaledLayouts);

    // The current position in the document along the primary axis
    var primaryDocPosition = config.verticallyOriented ? config.padding.document.top : config.padding.document.left;

    var pageGroups = [];

    // TODO: Use bottom, right as well
    var pagePadding = {
        top: config.padding.page.top,
        left: config.padding.page.left
    };

    scaledLayouts.forEach(function (layout, index) {
        var top = void 0,
            left = void 0;

        if (config.verticallyOriented) {
            top = primaryDocPosition;
            left = (documentSecondaryExtent - layout.dimensions.width) / 2;
        } else {
            top = (documentSecondaryExtent - layout.dimensions.height) / 2;
            left = primaryDocPosition;
        }

        var region = {
            top: top,
            bottom: top + pagePadding.top + layout.dimensions.height,
            left: left,
            right: left + pagePadding.left + layout.dimensions.width
        };

        pageGroups.push({
            index: index,
            dimensions: layout.dimensions,
            pages: layout.pages,
            region: region,
            padding: pagePadding
        });

        primaryDocPosition = config.verticallyOriented ? region.bottom : region.right;
    });

    var height = void 0,
        width = void 0;

    if (config.verticallyOriented) {
        height = primaryDocPosition + pagePadding.top;
        width = documentSecondaryExtent;
    } else {
        height = documentSecondaryExtent;
        width = primaryDocPosition + pagePadding.left;
    }

    return {
        dimensions: {
            height: height,
            width: width
        },
        pageGroups: pageGroups
    };
}

function getScaledPageLayouts(config, zoomLevel) {
    var scaleRatio = Math.pow(2, zoomLevel - config.maxZoomLevel);

    return config.pageLayouts.map(function (group) {
        return {
            dimensions: scaleDimensions(group.dimensions, scaleRatio),

            pages: group.pages.map(function (page) {
                return {
                    index: page.index,

                    groupOffset: {
                        top: Math.floor(page.groupOffset.top * scaleRatio),
                        left: Math.floor(page.groupOffset.left * scaleRatio)
                    },

                    dimensions: scaleDimensions(page.dimensions, scaleRatio)
                };
            })
        };
    });
}

function scaleDimensions(dimensions, scaleRatio) {
    return {
        height: Math.floor(dimensions.height * scaleRatio),
        width: Math.floor(dimensions.width * scaleRatio)
    };
}

function getExtentAlongSecondaryAxis(config, scaledLayouts) {
    // Get the extent of the document along the secondary axis
    var secondaryDim = void 0,
        secondaryPadding = void 0;
    var docPadding = config.padding.document;

    if (config.verticallyOriented) {
        secondaryDim = 'width';
        secondaryPadding = docPadding.left + docPadding.right;
    } else {
        secondaryDim = 'height';
        secondaryPadding = docPadding.top + docPadding.bottom;
    }

    return secondaryPadding + scaledLayouts.reduce(function (maxDim, layout) {
        return Math.max(layout.dimensions[secondaryDim], maxDim);
    }, 0);
}

/***/ }),

/***/ "./source/js/exceptions.js":
/*!*********************************!*\
  !*** ./source/js/exceptions.js ***!
  \*********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.DivaParentElementNotFoundException = DivaParentElementNotFoundException;
exports.NotAnIIIFManifestException = NotAnIIIFManifestException;
exports.ObjectDataNotSuppliedException = ObjectDataNotSuppliedException;
function DivaParentElementNotFoundException(message) {
    this.name = "DivaParentElementNotFoundException";
    this.message = message;
    this.stack = new Error().stack;
}

DivaParentElementNotFoundException.prototype = new Error();

function NotAnIIIFManifestException(message) {
    this.name = "NotAnIIIFManifestException";
    this.message = message;
    this.stack = new Error().stack;
}

NotAnIIIFManifestException.prototype = new Error();

function ObjectDataNotSuppliedException(message) {
    this.name = "ObjectDataNotSuppliedException";
    this.message = message;
    this.stack = new Error().stack;
}

ObjectDataNotSuppliedException.prototype = new Error();

/***/ }),

/***/ "./source/js/gesture-events.js":
/*!*************************************!*\
  !*** ./source/js/gesture-events.js ***!
  \*************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = {
    onDoubleClick: onDoubleClick,
    onPinch: onPinch,
    onDoubleTap: onDoubleTap
};


var DOUBLE_CLICK_TIMEOUT = 500;
var DOUBLE_TAP_DISTANCE_THRESHOLD = 50;
var DOUBLE_TAP_TIMEOUT = 250;

function onDoubleClick(elem, callback) {
    elem.addEventListener('dblclick', function (event) {
        if (!event.ctrlKey) {
            callback(event, getRelativeOffset(event.currentTarget, event));
        }
    });

    // Handle the control key for macs (in conjunction with double-clicking)
    // FIXME: Does a click get handled with ctrl pressed on non-Macs?
    var tracker = createDoubleEventTracker(DOUBLE_CLICK_TIMEOUT);

    elem.addEventListener('contextmenu', function (event) {
        event.preventDefault();

        if (event.ctrlKey) {
            if (tracker.isTriggered()) {
                tracker.reset();
                callback(event, getRelativeOffset(event.currentTarget, event));
            } else {
                tracker.trigger();
            }
        }
    });
}

function onPinch(elem, callback) {
    var startDistance = 0;

    elem.addEventListener('touchstart', function (event) {
        // Prevent mouse event from firing
        event.preventDefault();

        if (event.originalEvent.touches.length === 2) {
            startDistance = distance(event.originalEvent.touches[0].clientX, event.originalEvent.touches[0].clientY, event.originalEvent.touches[1].clientX, event.originalEvent.touches[1].clientY);
        }
    });

    elem.addEventListener('touchmove', function (event) {
        // Prevent mouse event from firing
        event.preventDefault();

        if (event.originalEvent.touches.length === 2) {
            var touches = event.originalEvent.touches;

            var moveDistance = distance(touches[0].clientX, touches[0].clientY, touches[1].clientX, touches[1].clientY);

            var zoomDelta = moveDistance - startDistance;

            if (Math.abs(zoomDelta) > 0) {
                var touchCenter = {
                    pageX: (touches[0].clientX + touches[1].clientX) / 2,
                    pageY: (touches[0].clientY + touches[1].clientY) / 2
                };

                callback(event, getRelativeOffset(event.currentTarget, touchCenter), startDistance, moveDistance);
            }
        }
    });
}

function onDoubleTap(elem, callback) {
    var tracker = createDoubleEventTracker(DOUBLE_TAP_TIMEOUT);
    var firstTap = null;

    elem.addEventListener('touchend', function (event) {
        // Prevent mouse event from firing
        event.preventDefault();

        if (tracker.isTriggered()) {
            tracker.reset();

            // Doubletap has occurred
            var secondTap = {
                pageX: event.originalEvent.changedTouches[0].clientX,
                pageY: event.originalEvent.changedTouches[0].clientY
            };

            // If first tap is close to second tap (prevents interference with scale event)
            var tapDistance = distance(firstTap.pageX, firstTap.pageY, secondTap.pageX, secondTap.pageY);

            // TODO: Could give something higher-level than secondTap to callback
            if (tapDistance < DOUBLE_TAP_DISTANCE_THRESHOLD) callback(event, getRelativeOffset(event.currentTarget, secondTap));

            firstTap = null;
        } else {
            firstTap = {
                pageX: event.originalEvent.changedTouches[0].clientX,
                pageY: event.originalEvent.changedTouches[0].clientY
            };

            tracker.trigger();
        }
    });
}

// Pythagorean theorem to get the distance between two points (used for
// calculating finger distance for double-tap and pinch-zoom)
function distance(x1, y1, x2, y2) {
    return Math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
}

// Utility to keep track of whether an event has been triggered twice
// during a a given duration
function createDoubleEventTracker(timeoutDuration) {
    var triggered = false;
    var timeoutId = null;

    return {
        trigger: function trigger() {
            triggered = true;
            resetTimeout();
            timeoutId = setTimeout(function () {
                triggered = false;
                timeoutId = null;
            }, timeoutDuration);
        },
        isTriggered: function isTriggered() {
            return triggered;
        },
        reset: function reset() {
            triggered = false;
            resetTimeout();
        }
    };

    function resetTimeout() {
        if (timeoutId !== null) {
            clearTimeout(timeoutId);
            timeoutId = null;
        }
    }
}

function getRelativeOffset(elem, pageCoords) {
    var bounds = elem.getBoundingClientRect();

    return {
        left: pageCoords.pageX - bounds.left,
        top: pageCoords.pageY - bounds.top
    };
}

/***/ }),

/***/ "./source/js/grid-handler.js":
/*!***********************************!*\
  !*** ./source/js/grid-handler.js ***!
  \***********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _lodash = __webpack_require__(/*! lodash.maxby */ "./node_modules/lodash.maxby/index.js");

var _lodash2 = _interopRequireDefault(_lodash);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var GridHandler = function () {
    function GridHandler(viewerCore) {
        _classCallCheck(this, GridHandler);

        this._viewerCore = viewerCore;
    }

    // USER EVENTS


    _createClass(GridHandler, [{
        key: 'onDoubleClick',
        value: function onDoubleClick(event, coords) {
            var position = this._viewerCore.getPagePositionAtViewportOffset(coords);

            var layout = this._viewerCore.getCurrentLayout();
            var viewport = this._viewerCore.getViewport();
            var pageToViewportCenterOffset = layout.getPageToViewportCenterOffset(position.anchorPage, viewport);

            this._viewerCore.reload({
                inGrid: false,
                goDirectlyTo: position.anchorPage,
                horizontalOffset: pageToViewportCenterOffset.x + position.offset.left,
                verticalOffset: pageToViewportCenterOffset.y + position.offset.top
            });
        }
    }, {
        key: 'onPinch',
        value: function onPinch() {
            this._viewerCore.reload({ inGrid: false });
        }

        // VIEW EVENTS

    }, {
        key: 'onViewWillLoad',
        value: function onViewWillLoad() {
            // FIXME(wabain): Should something happen here?
            /* No-op */
        }
    }, {
        key: 'onViewDidLoad',
        value: function onViewDidLoad() {
            // FIXME(wabain): Should something happen here?
            /* No-op */
        }
    }, {
        key: 'onViewDidUpdate',
        value: function onViewDidUpdate(renderedPages, targetPage) {
            // return early if there are no rendered pages in view.
            if (renderedPages.length === 0) return;

            if (targetPage !== null) {
                this._viewerCore.setCurrentPage(targetPage);
                return;
            }

            // Select the current page from the first row if it is fully visible, or from
            // the second row if it is fully visible, or from the centermost row otherwise.
            // If the current page is in that group then don't change it. Otherwise, set
            // the current page to the group's first page.

            var layout = this._viewerCore.getCurrentLayout();
            var groups = [];

            renderedPages.forEach(function (pageIndex) {
                var group = layout.getPageInfo(pageIndex).group;
                if (groups.length === 0 || group !== groups[groups.length - 1]) {
                    groups.push(group);
                }
            });

            var viewport = this._viewerCore.getViewport();
            var chosenGroup = void 0;

            if (groups.length === 1 || groups[0].region.top >= viewport.top) {
                chosenGroup = groups[0];
            } else if (groups[1].region.bottom <= viewport.bottom) {
                chosenGroup = groups[1];
            } else {
                chosenGroup = getCentermostGroup(groups, viewport);
            }

            var currentPage = this._viewerCore.getSettings().currentPageIndex;

            var hasCurrentPage = chosenGroup.pages.some(function (page) {
                return page.index === currentPage;
            });

            if (!hasCurrentPage) {
                this._viewerCore.setCurrentPage(chosenGroup.pages[0].index);
            }
        }
    }, {
        key: 'destroy',
        value: function destroy() {
            // No-op
        }
    }]);

    return GridHandler;
}();

exports.default = GridHandler;


function getCentermostGroup(groups, viewport) {
    var viewportMiddle = viewport.top + viewport.height / 2;

    return (0, _lodash2.default)(groups, function (group) {
        var groupMiddle = group.region.top + group.dimensions.height / 2;
        return -Math.abs(viewportMiddle - groupMiddle);
    });
}

/***/ }),

/***/ "./source/js/iiif-source-adapter.js":
/*!******************************************!*\
  !*** ./source/js/iiif-source-adapter.js ***!
  \******************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var IIIFSourceAdapter = function () {
    function IIIFSourceAdapter() {
        _classCallCheck(this, IIIFSourceAdapter);
    }

    _createClass(IIIFSourceAdapter, [{
        key: 'getPageImageURL',
        value: function getPageImageURL(manifest, pageIndex, size) {
            var dimens = void 0;

            if (!size || size.width == null && size.height == null) {
                dimens = 'full';
            } else {
                dimens = (size.width == null ? '' : size.width) + ',' + (size.height == null ? '' : size.height);
            }

            var page = manifest.pages[pageIndex];
            var quality = page.api > 1.1 ? 'default' : 'native';

            return encodeURI(page.url + 'full/' + dimens + '/0/' + quality + '.jpg');
        }
    }, {
        key: 'getTileImageURL',
        value: function getTileImageURL(manifest, pageIndex, params) {
            var page = manifest.pages[pageIndex];

            var height = void 0,
                width = void 0;

            if (params.row === params.rowCount - 1) {
                height = page.d[params.zoomLevel].h - (params.rowCount - 1) * params.tileDimensions.height;
            } else {
                height = params.tileDimensions.height;
            }

            if (params.col === params.colCount - 1) {
                width = page.d[params.zoomLevel].w - (params.colCount - 1) * params.tileDimensions.width;
            } else {
                width = params.tileDimensions.width;
            }

            var zoomDifference = Math.pow(2, manifest.maxZoom - params.zoomLevel);

            var x = params.col * params.tileDimensions.width * zoomDifference;
            var y = params.row * params.tileDimensions.height * zoomDifference;

            if (page.hasOwnProperty('xoffset')) {
                x += page.xoffset;
                y += page.yoffset;
            }

            var region = [x, y, width * zoomDifference, height * zoomDifference].join(',');

            var quality = page.api > 1.1 ? 'default' : 'native';

            return encodeURI(page.url + region + '/' + width + ',' + height + '/0/' + quality + '.jpg');
        }
    }]);

    return IIIFSourceAdapter;
}();

exports.default = IIIFSourceAdapter;

/***/ }),

/***/ "./source/js/image-cache.js":
/*!**********************************!*\
  !*** ./source/js/image-cache.js ***!
  \**********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var debug = __webpack_require__(/*! debug */ "./node_modules/debug/src/browser.js")('diva:ImageCache');

/* FIXME(wabain): The caching strategy here is completely
 * arbitrary and the implementation isn't especially efficient.
 */
var DEFAULT_MAX_KEYS = 100;

var ImageCache = function () {
    function ImageCache(options) {
        _classCallCheck(this, ImageCache);

        options = options || { maxKeys: DEFAULT_MAX_KEYS };
        this.maxKeys = options.maxKeys || DEFAULT_MAX_KEYS;

        this._held = {};
        this._urls = {};
        this._lru = [];
    }

    _createClass(ImageCache, [{
        key: 'get',
        value: function get(url) {
            var record = this._urls[url];
            return record ? record.img : null;
        }
    }, {
        key: 'has',
        value: function has(url) {
            return !!this._urls[url];
        }
    }, {
        key: 'put',
        value: function put(url, img) {
            var record = this._urls[url];
            if (record) {
                // FIXME: Does this make sense for this use case?
                record.img = img;
                this._promote(record);
            } else {
                record = {
                    img: img,
                    url: url
                };

                this._urls[url] = record;
                this._tryEvict(1);
                this._lru.unshift(record);
            }
        }
    }, {
        key: '_promote',
        value: function _promote(record) {
            var index = this._lru.indexOf(record);
            this._lru.splice(index, 1);
            this._lru.unshift(record);
        }
    }, {
        key: '_tryEvict',
        value: function _tryEvict(extraCapacity) {
            var allowedEntryCount = this.maxKeys - extraCapacity;

            if (this._lru.length <= allowedEntryCount) return;

            var evictionIndex = this._lru.length - 1;

            for (;;) {
                var target = this._lru[evictionIndex];

                if (!this._held[target.url]) {
                    debug('Evicting image %s', target.url);
                    this._lru.splice(evictionIndex, 1);
                    delete this._urls[target.url];

                    if (this._lru.length <= allowedEntryCount) break;
                }

                if (evictionIndex === 0) {
                    /* istanbul ignore next */
                    debug.enabled && debug('Cache overfull by %s (all entries are being held)', this._lru.length - allowedEntryCount);

                    break;
                }

                evictionIndex--;
            }
        }
    }, {
        key: 'acquire',
        value: function acquire(url) {
            this._held[url] = (this._held[url] || 0) + 1;
            this._promote(this._urls[url]);
        }
    }, {
        key: 'release',
        value: function release(url) {
            var count = this._held[url];

            if (count > 1) this._held[url]--;else delete this._held[url];

            this._tryEvict(0);
        }
    }]);

    return ImageCache;
}();

exports.default = ImageCache;

/***/ }),

/***/ "./source/js/image-manifest.js":
/*!*************************************!*\
  !*** ./source/js/image-manifest.js ***!
  \*************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _parseIiifManifest = __webpack_require__(/*! ./parse-iiif-manifest */ "./source/js/parse-iiif-manifest.js");

var _parseIiifManifest2 = _interopRequireDefault(_parseIiifManifest);

var _iiifSourceAdapter = __webpack_require__(/*! ./iiif-source-adapter */ "./source/js/iiif-source-adapter.js");

var _iiifSourceAdapter2 = _interopRequireDefault(_iiifSourceAdapter);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var ImageManifest = function () {
    function ImageManifest(data, urlAdapter) {
        _classCallCheck(this, ImageManifest);

        // Save all the data we need
        this.pages = data.pgs;
        this.maxZoom = data.max_zoom;
        this.maxRatio = data.dims.max_ratio;
        this.minRatio = data.dims.min_ratio;
        this.itemTitle = data.item_title;

        // Only given for IIIF manifests
        this.paged = !!data.paged;

        // These are arrays, the index corresponding to the zoom level
        this._maxWidths = data.dims.max_w;
        this._maxHeights = data.dims.max_h;
        this._averageWidths = data.dims.a_wid;
        this._averageHeights = data.dims.a_hei;
        this._totalHeights = data.dims.t_hei;
        this._totalWidths = data.dims.t_wid;

        this._urlAdapter = urlAdapter;
    }

    _createClass(ImageManifest, [{
        key: 'isPageValid',
        value: function isPageValid(pageIndex, showNonPagedPages) {
            if (!showNonPagedPages && this.paged && !this.pages[pageIndex].paged) {
                return false;
            }

            return pageIndex >= 0 && pageIndex < this.pages.length;
        }
    }, {
        key: 'getMaxPageDimensions',
        value: function getMaxPageDimensions(pageIndex) {
            var maxDims = this.pages[pageIndex].d[this.maxZoom];

            return {
                height: maxDims.h,
                width: maxDims.w
            };
        }
    }, {
        key: 'getPageDimensionsAtZoomLevel',
        value: function getPageDimensionsAtZoomLevel(pageIndex, zoomLevel) {
            var maxDims = this.pages[pageIndex].d[this.maxZoom];

            var scaleRatio = getScaleRatio(this.maxZoom, zoomLevel);

            return {
                height: maxDims.h * scaleRatio,
                width: maxDims.w * scaleRatio
            };
        }

        /**
         * Returns a URL for the image of the given page. The optional size
         * parameter supports setting the image width or height (default is
         * full-sized).
         */

    }, {
        key: 'getPageImageURL',
        value: function getPageImageURL(pageIndex, size) {
            return this._urlAdapter.getPageImageURL(this, pageIndex, size);
        }

        /**
         * Return an array of tile objects for the specified page and integer zoom level
         */

    }, {
        key: 'getPageImageTiles',
        value: function getPageImageTiles(pageIndex, zoomLevel, tileDimensions) {
            var page = this.pages[pageIndex];

            if (!isFinite(zoomLevel) || zoomLevel % 1 !== 0) {
                throw new TypeError('Zoom level must be an integer: ' + zoomLevel);
            }

            var rows = Math.ceil(page.d[zoomLevel].h / tileDimensions.height);
            var cols = Math.ceil(page.d[zoomLevel].w / tileDimensions.width);

            var tiles = [];

            var row = void 0,
                col = void 0,
                url = void 0;

            for (row = 0; row < rows; row++) {
                for (col = 0; col < cols; col++) {
                    url = this._urlAdapter.getTileImageURL(this, pageIndex, {
                        row: row,
                        col: col,
                        rowCount: rows,
                        colCount: cols,
                        zoomLevel: zoomLevel,
                        tileDimensions: tileDimensions
                    });

                    // FIXME: Dimensions should account for partial tiles (e.g. the
                    // last row and column in a tiled image)
                    tiles.push({
                        row: row,
                        col: col,
                        zoomLevel: zoomLevel,
                        dimensions: {
                            height: tileDimensions.height,
                            width: tileDimensions.width
                        },
                        offset: {
                            top: row * tileDimensions.height,
                            left: col * tileDimensions.width
                        },
                        url: url
                    });
                }
            }

            return {
                zoomLevel: zoomLevel,
                rows: rows,
                cols: cols,
                tiles: tiles
            };
        }
    }], [{
        key: 'fromIIIF',
        value: function fromIIIF(iiifManifest) {
            var data = (0, _parseIiifManifest2.default)(iiifManifest);
            return new ImageManifest(data, new _iiifSourceAdapter2.default());
        }
    }]);

    return ImageManifest;
}();

exports.default = ImageManifest;


ImageManifest.prototype.getMaxWidth = zoomedPropertyGetter('_maxWidths');
ImageManifest.prototype.getMaxHeight = zoomedPropertyGetter('_maxHeights');
ImageManifest.prototype.getAverageWidth = zoomedPropertyGetter('_averageWidths');
ImageManifest.prototype.getAverageHeight = zoomedPropertyGetter('_averageHeights');
ImageManifest.prototype.getTotalWidth = zoomedPropertyGetter('_totalWidths');
ImageManifest.prototype.getTotalHeight = zoomedPropertyGetter('_totalHeights');

function zoomedPropertyGetter(privateName) {
    return function (zoomLevel) {
        return this[privateName][zoomLevel];
    };
}

function getScaleRatio(sourceZoomLevel, targetZoomLevel) {
    return 1 / Math.pow(2, sourceZoomLevel - targetZoomLevel);
}

/***/ }),

/***/ "./source/js/image-request-handler.js":
/*!********************************************!*\
  !*** ./source/js/image-request-handler.js ***!
  \********************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var debug = __webpack_require__(/*! debug */ "./node_modules/debug/src/browser.js")('diva:ImageRequestHandler');
/**
 * Handler for the request for an image tile
 *
 * @param url
 * @param callback
 * @constructor
 */

var ImageRequestHandler = function () {
    function ImageRequestHandler(options) {
        var _this = this;

        _classCallCheck(this, ImageRequestHandler);

        this._url = options.url;
        this._callback = options.load;
        this._errorCallback = options.error;
        this.timeoutTime = options.timeoutTime || 0;
        this._aborted = this._complete = false;

        //Use a timeout to allow the requests to be debounced (as they are in renderer)
        this.timeout = setTimeout(function () {
            // Initiate the request
            _this._image = new Image();
            _this._image.crossOrigin = "anonymous";
            _this._image.onload = _this._handleLoad.bind(_this);
            _this._image.onerror = _this._handleError.bind(_this);
            _this._image.src = options.url;

            debug('Requesting image %s', options.url);
        }, this.timeoutTime);
    }

    _createClass(ImageRequestHandler, [{
        key: 'abort',
        value: function abort() {
            debug('Aborting request to %s', this._url);

            clearTimeout(this.timeout);

            // FIXME
            // People on the Internet say that doing this {{should/should not}} abort the request. I believe
            // it corresponds to what the WHATWG HTML spec says should happen when the UA
            // updates the image data if selected source is null.
            //
            // Sources:
            //
            // https://html.spec.whatwg.org/multipage/embedded-content.html#the-img-element
            // http://stackoverflow.com/questions/7390888/does-changing-the-src-attribute-of-an-image-stop-the-image-from-downloading
            if (this._image) {
                this._image.onload = this._image.onerror = null;

                this._image.src = '';
            }

            this._aborted = true;
        }
    }, {
        key: '_handleLoad',
        value: function _handleLoad() {
            if (this._aborted) {
                console.error('ImageRequestHandler invoked on cancelled request for ' + this._url);
                return;
            }

            if (this._complete) {
                console.error('ImageRequestHandler invoked on completed request for ' + this._url);
                return;
            }

            this._complete = true;

            debug('Received image %s', this._url);
            this._callback(this._image);
        }
    }, {
        key: '_handleError',
        value: function _handleError() {
            debug('Failed to load image %s', this._url);
            this._errorCallback(this._image);
        }
    }]);

    return ImageRequestHandler;
}();

exports.default = ImageRequestHandler;

/***/ }),

/***/ "./source/js/interpolate-animation.js":
/*!********************************************!*\
  !*** ./source/js/interpolate-animation.js ***!
  \********************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});
// TODO: requestAnimationFrame fallback

exports.default = {
    animate: animate,
    easing: {
        linear: linearEasing,
        cubic: inOutCubicEasing
    }
};


var now = void 0;

if (typeof performance !== 'undefined' && performance.now) {
    now = function now() {
        return performance.now();
    };
} else {
    now = function now() {
        return Date.now();
    };
}

function animate(options) {
    var durationMs = options.duration;
    var parameters = options.parameters;
    var onUpdate = options.onUpdate;
    var onEnd = options.onEnd;

    // Setup
    // Times are in milliseconds from a basically arbitrary start
    var start = now();
    var end = start + durationMs;

    var tweenFns = {};
    var values = {};
    var paramKeys = Object.keys(parameters);

    paramKeys.forEach(function (key) {
        var config = parameters[key];
        tweenFns[key] = interpolate(config.from, config.to, config.easing || inOutCubicEasing);
    });

    // Run it!
    var requestId = requestAnimationFrame(update);

    return {
        cancel: function cancel() {
            if (requestId !== null) {
                cancelAnimationFrame(requestId);
                handleAnimationCompletion({
                    interrupted: true
                });
            }
        }
    };

    function update() {
        var current = now();
        var elapsed = Math.min((current - start) / durationMs, 1);

        updateValues(elapsed);
        onUpdate(values);

        if (current < end) {
            requestId = requestAnimationFrame(update);
        } else {
            handleAnimationCompletion({
                interrupted: false
            });
        }
    }

    function updateValues(elapsed) {
        paramKeys.forEach(function (key) {
            values[key] = tweenFns[key](elapsed);
        });
    }

    function handleAnimationCompletion(info) {
        requestId = null;

        if (onEnd) onEnd(info);
    }
}

function interpolate(start, end, easing) {
    return function (elapsed) {
        return start + (end - start) * easing(elapsed);
    };
}

/**
 * Easing functions. inOutCubicEasing is the default, but
 * others are given for convenience.
 *
 **/
function linearEasing(e) {
    return e;
}

function inOutCubicEasing(t) {
    return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
}

/***/ }),

/***/ "./source/js/page-layouts/book-layout.js":
/*!***********************************************!*\
  !*** ./source/js/page-layouts/book-layout.js ***!
  \***********************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = getBookLayoutGroups;

var _pageDimensions = __webpack_require__(/*! ./page-dimensions */ "./source/js/page-layouts/page-dimensions.js");

var _pageDimensions2 = _interopRequireDefault(_pageDimensions);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function getBookLayoutGroups(viewerConfig) {
    var groupings = getGroupings(viewerConfig);

    return groupings.map(function (grouping) {
        return getGroupLayoutsFromPageGrouping(viewerConfig, grouping);
    });
}

function getGroupings(viewerConfig) {
    var manifest = viewerConfig.manifest;

    var pagesByGroup = [];
    var leftPage = null;
    var nonPagedPages = []; // Pages to display below the current group

    var _addNonPagedPages = function _addNonPagedPages() {
        for (var i = 0, nlen = nonPagedPages.length; i < nlen; i++) {
            pagesByGroup.push([nonPagedPages[i]]);
        }
        nonPagedPages = [];
    };

    manifest.pages.forEach(function (page, index) {
        var pageRecord = {
            index: index,
            dimensions: (0, _pageDimensions2.default)(index, manifest),
            paged: !manifest.paged || page.paged
        };

        // Only display non-paged pages if specified in the settings
        if (!viewerConfig.showNonPagedPages && !pageRecord.paged) return;

        if (!pageRecord.paged) {
            nonPagedPages.push(pageRecord);
        } else if (index === 0 || page.facingPages) {
            // The first page is placed on its own
            pagesByGroup.push([pageRecord]);
            _addNonPagedPages();
        } else if (leftPage === null) {
            leftPage = pageRecord;
        } else {
            pagesByGroup.push([leftPage, pageRecord]);
            leftPage = null;
            _addNonPagedPages();
        }
    });

    // Flush a final left page
    if (leftPage !== null) {
        pagesByGroup.push([leftPage]);
        _addNonPagedPages();
    }

    return pagesByGroup;
}

function getGroupLayoutsFromPageGrouping(viewerConfig, grouping) {
    var verticallyOriented = viewerConfig.verticallyOriented;

    if (grouping.length === 2) return getFacingPageGroup(grouping[0], grouping[1], verticallyOriented);

    var page = grouping[0];
    var pageDims = page.dimensions;

    // The first page is placed on its own to the right in vertical orientation.
    // NB that this needs to be the page with index 0; if the first page is excluded
    // from the layout then this special case shouldn't apply.
    // If the page is tagged as 'non-paged', center it horizontally
    var leftOffset = void 0;
    if (page.paged) leftOffset = page.index === 0 && verticallyOriented ? pageDims.width : 0;else leftOffset = verticallyOriented ? pageDims.width / 2 : 0;

    var shouldBeHorizontallyAdjusted = verticallyOriented && !viewerConfig.manifest.pages[page.index].facingPages;

    // We need to left-align the page in vertical orientation, so we double
    // the group width
    return {
        dimensions: {
            height: pageDims.height,
            width: shouldBeHorizontallyAdjusted ? pageDims.width * 2 : pageDims.width
        },
        pages: [{
            index: page.index,
            groupOffset: {
                top: 0,
                left: leftOffset
            },
            dimensions: pageDims
        }]
    };
}

function getFacingPageGroup(leftPage, rightPage, verticallyOriented) {
    var leftDims = leftPage.dimensions;
    var rightDims = rightPage.dimensions;

    var height = Math.max(leftDims.height, rightDims.height);

    var width = void 0,
        firstLeftOffset = void 0,
        secondLeftOffset = void 0;

    if (verticallyOriented) {
        var midWidth = Math.max(leftDims.width, rightDims.width);

        width = midWidth * 2;

        firstLeftOffset = midWidth - leftDims.width;
        secondLeftOffset = midWidth;
    } else {
        width = leftDims.width + rightDims.width;
        firstLeftOffset = 0;
        secondLeftOffset = leftDims.width;
    }

    return {
        dimensions: {
            height: height,
            width: width
        },
        pages: [{
            index: leftPage.index,
            dimensions: leftDims,
            groupOffset: {
                top: 0,
                left: firstLeftOffset
            }
        }, {
            index: rightPage.index,
            dimensions: rightDims,
            groupOffset: {
                top: 0,
                left: secondLeftOffset
            }
        }]
    };
}

/***/ }),

/***/ "./source/js/page-layouts/grid-layout.js":
/*!***********************************************!*\
  !*** ./source/js/page-layouts/grid-layout.js ***!
  \***********************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = getGridLayoutGroups;
function getGridLayoutGroups(viewerConfig) {
    var viewportWidth = viewerConfig.viewport.width;
    var manifest = viewerConfig.manifest;
    var pagesPerRow = viewerConfig.pagesPerRow;
    var fixedHeightGrid = viewerConfig.fixedHeightGrid;
    var fixedPadding = viewerConfig.fixedPadding;
    var showNonPagedPages = viewerConfig.showNonPagedPages;

    var horizontalPadding = fixedPadding * (pagesPerRow + 1);
    var pageWidth = (viewportWidth - horizontalPadding) / pagesPerRow;
    var gridPageWidth = pageWidth;

    // Calculate the row height depending on whether we want to fix the width or the height
    var rowHeight = fixedHeightGrid ? fixedPadding + manifest.minRatio * pageWidth : fixedPadding + manifest.maxRatio * pageWidth;

    var groups = [];
    var currentPages = [];

    var getGridPageDimensions = function getGridPageDimensions(pageData) {
        // Calculate the width, height and horizontal placement of this page
        // Get dimensions at max zoom level, although any level should be fine
        var pageDimenData = pageData.d[pageData.d.length - 1];
        var heightToWidthRatio = pageDimenData.h / pageDimenData.w;

        var pageWidth = void 0,
            pageHeight = void 0;

        if (fixedHeightGrid) {
            pageWidth = (rowHeight - fixedPadding) / heightToWidthRatio;
            pageHeight = rowHeight - fixedPadding;
        } else {
            pageWidth = gridPageWidth;
            pageHeight = pageWidth * heightToWidthRatio;
        }

        return {
            width: Math.round(pageWidth),
            height: Math.round(pageHeight)
        };
    };

    var rowDimensions = {
        height: rowHeight,
        width: viewportWidth
    };

    manifest.pages.forEach(function (page, pageIndex) {
        if (!showNonPagedPages && manifest.paged && !page.paged) return;

        // Calculate the width, height and horizontal placement of this page
        var pageDimens = getGridPageDimensions(page);
        var leftOffset = Math.floor(currentPages.length * (fixedPadding + gridPageWidth) + fixedPadding);

        // Center the page if the height is fixed (otherwise, there is no horizontal padding)
        if (fixedHeightGrid) {
            leftOffset += (gridPageWidth - pageDimens.width) / 2;
        }

        // TODO: Precompute page dimensions everywhere
        currentPages.push({
            index: pageIndex,
            dimensions: pageDimens,
            groupOffset: {
                top: 0,
                left: leftOffset
            }
        });

        if (currentPages.length === pagesPerRow) {
            groups.push({
                dimensions: rowDimensions,
                pages: currentPages
            });

            currentPages = [];
        }
    });

    if (currentPages.length > 0) {
        groups.push({
            dimensions: rowDimensions,
            pages: currentPages
        });
    }

    return groups;
}

/***/ }),

/***/ "./source/js/page-layouts/index.js":
/*!*****************************************!*\
  !*** ./source/js/page-layouts/index.js ***!
  \*****************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = getPageLayouts;

var _bookLayout = __webpack_require__(/*! ./book-layout */ "./source/js/page-layouts/book-layout.js");

var _bookLayout2 = _interopRequireDefault(_bookLayout);

var _singlesLayout = __webpack_require__(/*! ./singles-layout */ "./source/js/page-layouts/singles-layout.js");

var _singlesLayout2 = _interopRequireDefault(_singlesLayout);

var _gridLayout = __webpack_require__(/*! ./grid-layout */ "./source/js/page-layouts/grid-layout.js");

var _gridLayout2 = _interopRequireDefault(_gridLayout);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

/** Get the relative positioning of pages for the current view */
function getPageLayouts(settings) {
    if (settings.inGrid) {
        return (0, _gridLayout2.default)(pluck(settings, ['manifest', 'viewport', 'pagesPerRow', 'fixedHeightGrid', 'fixedPadding', 'showNonPagedPages']));
    } else {
        var config = pluck(settings, ['manifest', 'verticallyOriented', 'showNonPagedPages']);

        if (settings.inBookLayout) return (0, _bookLayout2.default)(config);else return (0, _singlesLayout2.default)(config);
    }
}

function pluck(obj, keys) {
    var out = {};
    keys.forEach(function (key) {
        out[key] = obj[key];
    });
    return out;
}

/***/ }),

/***/ "./source/js/page-layouts/page-dimensions.js":
/*!***************************************************!*\
  !*** ./source/js/page-layouts/page-dimensions.js ***!
  \***************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = getPageDimensions;
function getPageDimensions(pageIndex, manifest) {
    var dims = manifest.getMaxPageDimensions(pageIndex);

    return {
        width: Math.floor(dims.width),
        height: Math.floor(dims.height)
    };
}

/***/ }),

/***/ "./source/js/page-layouts/singles-layout.js":
/*!**************************************************!*\
  !*** ./source/js/page-layouts/singles-layout.js ***!
  \**************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = getSinglesLayoutGroups;

var _pageDimensions = __webpack_require__(/*! ./page-dimensions */ "./source/js/page-layouts/page-dimensions.js");

var _pageDimensions2 = _interopRequireDefault(_pageDimensions);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function getSinglesLayoutGroups(viewerConfig) {
    var manifest = viewerConfig.manifest;

    // Render each page alone in a group
    var pages = [];
    manifest.pages.forEach(function (page, index) {
        if (!viewerConfig.showNonPagedPages && manifest.paged && !page.paged) return;

        var pageDims = (0, _pageDimensions2.default)(index, manifest);

        pages.push({
            dimensions: pageDims,
            pages: [{
                index: index,
                groupOffset: { top: 0, left: 0 },
                dimensions: pageDims
            }]
        });
    });

    return pages;
}

/***/ }),

/***/ "./source/js/page-overlay-manager.js":
/*!*******************************************!*\
  !*** ./source/js/page-overlay-manager.js ***!
  \*******************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/**
 * Manages a collection of page overlays, which implement a low-level
 * API for synchronizing HTML pages to the canvas. Each overlay needs
 * to implement the following protocol:
 *
 *   mount(): Called when a page is first rendered
 *   refresh(): Called when a page is moved
 *   unmount(): Called when a previously rendered page has stopped being rendered
 *
 * @class
 */

var PageOverlayManager = function () {
    function PageOverlayManager() {
        _classCallCheck(this, PageOverlayManager);

        this._pages = {};
        this._renderedPages = [];
        this._renderedPageMap = {};
    }

    _createClass(PageOverlayManager, [{
        key: "addOverlay",
        value: function addOverlay(overlay) {
            var overlaysByPage = this._pages[overlay.page] || (this._pages[overlay.page] = []);

            overlaysByPage.push(overlay);

            if (this._renderedPageMap[overlay.page]) overlay.mount();
        }
    }, {
        key: "removeOverlay",
        value: function removeOverlay(overlay) {
            var page = overlay.page;
            var overlaysByPage = this._pages[page];

            if (!overlaysByPage) return;

            var overlayIndex = overlaysByPage.indexOf(overlay);

            if (overlayIndex === -1) return;

            if (this._renderedPageMap[page]) overlaysByPage[overlayIndex].unmount();

            overlaysByPage.splice(overlayIndex, 1);

            if (overlaysByPage.length === 0) delete this._pages[page];
        }
    }, {
        key: "updateOverlays",
        value: function updateOverlays(renderedPages) {
            var _this = this;

            var previouslyRendered = this._renderedPages;
            var newRenderedMap = {};

            renderedPages.map(function (pageIndex) {
                newRenderedMap[pageIndex] = true;

                if (!_this._renderedPageMap[pageIndex]) {
                    _this._renderedPageMap[pageIndex] = true;

                    _this._invokeOnOverlays(pageIndex, function (overlay) {
                        overlay.mount();
                    });
                }
            });

            previouslyRendered.map(function (pageIndex) {
                if (newRenderedMap[pageIndex]) {
                    _this._invokeOnOverlays(pageIndex, function (overlay) {
                        overlay.refresh();
                    });
                } else {
                    delete _this._renderedPageMap[pageIndex];
                    _this._invokeOnOverlays(pageIndex, function (overlay) {
                        overlay.unmount();
                    });
                }
            });

            this._renderedPages = renderedPages;
        }
    }, {
        key: "_invokeOnOverlays",
        value: function _invokeOnOverlays(pageIndex, func) {
            var overlays = this._pages[pageIndex];
            if (overlays) overlays.map(function (o) {
                return func(o);
            });
        }
    }]);

    return PageOverlayManager;
}();

exports.default = PageOverlayManager;

/***/ }),

/***/ "./source/js/page-tools-overlay.js":
/*!*****************************************!*\
  !*** ./source/js/page-tools-overlay.js ***!
  \*****************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _elt = __webpack_require__(/*! ./utils/elt */ "./source/js/utils/elt.js");

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/**
*
*
**/
var PageToolsOverlay = function () {
    function PageToolsOverlay(pageIndex, viewerCore) {
        _classCallCheck(this, PageToolsOverlay);

        this.page = pageIndex;

        this._viewerCore = viewerCore;

        this._innerElement = this._viewerCore.getSettings().innerElement;
        this._pageToolsElem = null;
        //
        // this._buttons = null;
    }

    _createClass(PageToolsOverlay, [{
        key: 'mount',
        value: function mount() {
            if (this._pageToolsElem === null) {
                this._buttons = this._initializePageToolButtons();

                this._pageToolsElem = (0, _elt.elt)('div', { class: 'diva-page-tools-wrapper' }, (0, _elt.elt)('div', { class: 'diva-page-tools' }, this._buttons));
            }

            this.refresh();
            this._innerElement.appendChild(this._pageToolsElem);
        }
    }, {
        key: '_initializePageToolButtons',
        value: function _initializePageToolButtons() {
            // Callback parameters
            var settings = this._viewerCore.getSettings();
            var publicInstance = this._viewerCore.getPublicInstance();
            var pageIndex = this.page;

            return this._viewerCore.getPageTools().map(function (plugin) {
                // !!! The node needs to be cloned otherwise it is detached from
                //  one and reattached to the other.
                var button = plugin.pageToolsIcon.cloneNode(true);

                // ensure the plugin instance is handed as the first argument to call;
                // this will set the context (i.e., `this`) of the handleClick call to the plugin instance
                // itself.
                button.addEventListener('click', function (event) {
                    plugin.handleClick.call(plugin, event, settings, publicInstance, pageIndex);
                }, false);

                button.addEventListener('touchend', function (event) {
                    // Prevent firing of emulated mouse events
                    event.preventDefault();

                    plugin.handleClick.call(plugin, event, settings, publicInstance, pageIndex);
                }, false);

                return button;
            });
        }
    }, {
        key: 'unmount',
        value: function unmount() {
            this._innerElement.removeChild(this._pageToolsElem);
        }
    }, {
        key: 'refresh',
        value: function refresh() {
            var pos = this._viewerCore.getPageRegion(this.page, {
                excludePadding: true,
                incorporateViewport: true
            });

            this._pageToolsElem.style.top = pos.top + 'px';
            this._pageToolsElem.style.left = pos.left + 'px';
        }
    }]);

    return PageToolsOverlay;
}();

exports.default = PageToolsOverlay;

/***/ }),

/***/ "./source/js/parse-iiif-manifest.js":
/*!******************************************!*\
  !*** ./source/js/parse-iiif-manifest.js ***!
  \******************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = parseIIIFManifest;
var getMaxZoomLevel = function getMaxZoomLevel(width, height) {
    var largestDimension = Math.max(width, height);
    return Math.ceil(Math.log((largestDimension + 1) / (256 + 1)) / Math.log(2));
};

var incorporateZoom = function incorporateZoom(imageDimension, zoomDifference) {
    return imageDimension / Math.pow(2, zoomDifference);
};

var getOtherImageData = function getOtherImageData(otherImages, lowestMaxZoom) {
    return otherImages.map(function (itm) {
        var w = itm.width;
        var h = itm.height;
        var info = parseImageInfo(itm);
        var url = info.url.slice(-1) !== '/' ? info.url + '/' : info.url; // append trailing slash to url if it's not there.

        var dims = new Array(lowestMaxZoom + 1);
        for (var j = 0; j < lowestMaxZoom + 1; j++) {
            dims[j] = {
                h: Math.floor(incorporateZoom(h, lowestMaxZoom - j)),
                w: Math.floor(incorporateZoom(w, lowestMaxZoom - j))
            };
        }

        return {
            f: info.url,
            url: url,
            il: itm.label || "",
            d: dims
        };
    });
};

/**
 * Parses an IIIF Presentation API Manifest and converts it into a Diva.js-format object
 * (See https://github.com/DDMAL/diva.js/wiki/Development-notes#data-received-through-ajax-request)
 *
 * @param {Object} manifest - an object that represents a valid IIIF manifest
 * @returns {Object} divaServiceBlock - the data needed by Diva to show a view of a single document
 */
function parseIIIFManifest(manifest) {
    var sequence = manifest.sequences[0];
    var canvases = sequence.canvases;
    var numCanvases = canvases.length;

    var pages = new Array(canvases.length);

    var thisCanvas = void 0,
        thisResource = void 0,
        thisImage = void 0,
        otherImages = void 0,
        context = void 0,
        url = void 0,
        info = void 0,
        imageAPIVersion = void 0,
        width = void 0,
        height = void 0,
        maxZoom = void 0,
        canvas = void 0,
        label = void 0,
        imageLabel = void 0,
        zoomDimensions = void 0,
        widthAtCurrentZoomLevel = void 0,
        heightAtCurrentZoomLevel = void 0;

    var lowestMaxZoom = 100;
    var maxRatio = 0;
    var minRatio = 100;

    // quickly determine the lowest possible max zoom level (i.e., the upper bound for images) across all canvases.
    // while we're here, compute the global ratios as well.
    for (var z = 0; z < numCanvases; z++) {
        var c = canvases[z];
        var w = c.width;
        var h = c.height;
        var mz = getMaxZoomLevel(w, h);
        var ratio = h / w;
        maxRatio = Math.max(ratio, maxRatio);
        minRatio = Math.min(ratio, minRatio);

        lowestMaxZoom = Math.min(lowestMaxZoom, mz);
    }

    /*
        These arrays need to be pre-initialized since we will do arithmetic and value checking on them
    */
    var totalWidths = new Array(lowestMaxZoom + 1).fill(0);
    var totalHeights = new Array(lowestMaxZoom + 1).fill(0);
    var maxWidths = new Array(lowestMaxZoom + 1).fill(0);
    var maxHeights = new Array(lowestMaxZoom + 1).fill(0);

    for (var i = 0; i < numCanvases; i++) {
        thisCanvas = canvases[i];
        canvas = thisCanvas['@id'];
        label = thisCanvas.label;
        thisResource = thisCanvas.images[0].resource;

        /*
         * If a canvas has multiple images it will be encoded
         * with a resource type of "oa:Choice". The primary image will be available
         * on the 'default' key, with other images available under 'item.'
         * */
        if (thisResource['@type'] === "oa:Choice") {
            thisImage = thisResource.default;
        } else {
            thisImage = thisResource;
        }

        // Prioritize the canvas height / width first, since images may not have h/w
        width = thisCanvas.width || thisImage.width;
        height = thisCanvas.height || thisImage.height;
        if (width <= 0 || height <= 0) {
            console.warn('Invalid width or height for canvas ' + label + '. Skipping');
            continue;
        }

        maxZoom = getMaxZoomLevel(width, height);

        if (thisResource.item) {
            otherImages = getOtherImageData(thisResource.item, lowestMaxZoom);
        } else {
            otherImages = [];
        }

        imageLabel = thisImage.label || null;

        info = parseImageInfo(thisImage);
        url = info.url.slice(-1) !== '/' ? info.url + '/' : info.url; // append trailing slash to url if it's not there.

        context = thisImage.service['@context'];

        if (context === 'http://iiif.io/api/image/2/context.json') {
            imageAPIVersion = 2;
        } else if (context === 'http://library.stanford.edu/iiif/image-api/1.1/context.json') {
            imageAPIVersion = 1.1;
        } else {
            imageAPIVersion = 1.0;
        }

        zoomDimensions = new Array(lowestMaxZoom + 1);

        for (var k = 0; k < lowestMaxZoom + 1; k++) {
            widthAtCurrentZoomLevel = Math.floor(incorporateZoom(width, lowestMaxZoom - k));
            heightAtCurrentZoomLevel = Math.floor(incorporateZoom(height, lowestMaxZoom - k));
            zoomDimensions[k] = {
                h: heightAtCurrentZoomLevel,
                w: widthAtCurrentZoomLevel
            };

            totalWidths[k] += widthAtCurrentZoomLevel;
            totalHeights[k] += heightAtCurrentZoomLevel;
            maxWidths[k] = Math.max(widthAtCurrentZoomLevel, maxWidths[k]);
            maxHeights[k] = Math.max(heightAtCurrentZoomLevel, maxHeights[k]);
        }

        pages[i] = {
            d: zoomDimensions,
            m: maxZoom,
            l: label, // canvas label ('page 1, page 2', etc.)
            il: imageLabel, // default image label ('primary image', 'UV light', etc.)
            f: info.url,
            url: url,
            api: imageAPIVersion,
            paged: thisCanvas.viewingHint !== 'non-paged',
            facingPages: thisCanvas.viewingHint === 'facing-pages',
            canvas: canvas,
            otherImages: otherImages,
            xoffset: info.x || null,
            yoffset: info.y || null
        };
    }

    var averageWidths = new Array(lowestMaxZoom + 1);
    var averageHeights = new Array(lowestMaxZoom + 1);

    for (var a = 0; a < lowestMaxZoom + 1; a++) {
        averageWidths[a] = totalWidths[a] / numCanvases;
        averageHeights[a] = totalHeights[a] / numCanvases;
    }

    var dims = {
        a_wid: averageWidths,
        a_hei: averageHeights,
        max_w: maxWidths,
        max_h: maxHeights,
        max_ratio: maxRatio,
        min_ratio: minRatio,
        t_hei: totalHeights,
        t_wid: totalWidths
    };

    return {
        item_title: manifest.label,
        dims: dims,
        max_zoom: lowestMaxZoom,
        pgs: pages,
        paged: manifest.viewingHint === 'paged' || sequence.viewingHint === 'paged'
    };
}

/**
 * Takes in a resource block from a canvas and outputs the following information associated with that resource:
 * - Image URL
 * - Image region to be displayed
 *
 * @param {Object} resource - an object representing the resource block of a canvas section in a IIIF manifest
 * @returns {Object} imageInfo - an object containing image URL and region
 */
function parseImageInfo(resource) {
    var url = resource['@id'];
    var fragmentRegex = /#xywh=([0-9]+,[0-9]+,[0-9]+,[0-9]+)/;
    var xywh = '';
    var stripURL = true;

    if (/\/([0-9]+,[0-9]+,[0-9]+,[0-9]+)\//.test(url)) {
        // if resource in image API format, extract region x,y,w,h from URL (after 4th slash from last)
        // matches coordinates in URLs of the form http://www.example.org/iiif/book1-page1/40,50,1200,1800/full/0/default.jpg
        var urlArray = url.split('/');
        xywh = urlArray[urlArray.length - 4];
    } else if (fragmentRegex.test(url)) {
        // matches coordinates of the style http://www.example.org/iiif/book1/canvas/p1#xywh=50,50,320,240
        var result = fragmentRegex.exec(url);
        xywh = result[1];
    } else if (resource.service && resource.service['@id']) {
        // assume canvas size based on image size
        url = resource.service['@id'];
        // this URL excludes region parameters so we don't need to remove them
        stripURL = false;
    }

    if (stripURL) {
        // extract URL up to identifier (we eliminate the last 5 parameters: /region/size/rotation/quality.format)
        url = url.split('/').slice(0, -4).join('/');
    }

    var imageInfo = {
        url: url
    };

    if (xywh.length) {
        // parse into separate components
        var dimensions = xywh.split(',');
        imageInfo.x = parseInt(dimensions[0], 10);
        imageInfo.y = parseInt(dimensions[1], 10);
        imageInfo.w = parseInt(dimensions[2], 10);
        imageInfo.h = parseInt(dimensions[3], 10);
    }

    return imageInfo;
}

/***/ }),

/***/ "./source/js/renderer.js":
/*!*******************************!*\
  !*** ./source/js/renderer.js ***!
  \*******************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _elt = __webpack_require__(/*! ./utils/elt */ "./source/js/utils/elt.js");

var _compositeImage = __webpack_require__(/*! ./composite-image */ "./source/js/composite-image.js");

var _compositeImage2 = _interopRequireDefault(_compositeImage);

var _documentLayout = __webpack_require__(/*! ./document-layout */ "./source/js/document-layout.js");

var _documentLayout2 = _interopRequireDefault(_documentLayout);

var _imageCache = __webpack_require__(/*! ./image-cache */ "./source/js/image-cache.js");

var _imageCache2 = _interopRequireDefault(_imageCache);

var _imageRequestHandler = __webpack_require__(/*! ./image-request-handler */ "./source/js/image-request-handler.js");

var _imageRequestHandler2 = _interopRequireDefault(_imageRequestHandler);

var _interpolateAnimation = __webpack_require__(/*! ./interpolate-animation */ "./source/js/interpolate-animation.js");

var _interpolateAnimation2 = _interopRequireDefault(_interpolateAnimation);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var debug = __webpack_require__(/*! debug */ "./node_modules/debug/src/browser.js")('diva:Renderer');
var debugPaints = __webpack_require__(/*! debug */ "./node_modules/debug/src/browser.js")('diva:Renderer:paints');

var REQUEST_DEBOUNCE_INTERVAL = 250;

var Renderer = function () {
    function Renderer(options, hooks) {
        _classCallCheck(this, Renderer);

        this._viewport = options.viewport;
        this._outerElement = options.outerElement;
        this._documentElement = options.innerElement;

        this._hooks = hooks || {};

        this._canvas = (0, _elt.elt)('canvas', { class: 'diva-viewer-canvas' });
        this._ctx = this._canvas.getContext('2d');

        this.layout = null;

        this._sourceResolver = null;
        this._renderedPages = null;
        this._config = null;
        this._zoomLevel = null;
        this._compositeImages = null;
        this._renderedTiles = null;
        this._animation = null;

        // FIXME(wabain): What level should this be maintained at?
        // Diva global?
        this._cache = new _imageCache2.default();
        this._pendingRequests = {};
    }

    _createClass(Renderer, [{
        key: 'load',
        value: function load(config, viewportPosition, sourceResolver) {
            this._clearAnimation();

            if (this._hooks.onViewWillLoad) {
                this._hooks.onViewWillLoad();
            }

            this._sourceResolver = sourceResolver;
            this._config = config;
            this._compositeImages = {};
            this._setLayoutToZoomLevel(viewportPosition.zoomLevel);

            // FIXME(wabain): Remove this when there's more confidence the check shouldn't be needed
            if (!this.layout.getPageInfo(viewportPosition.anchorPage)) {
                throw new Error('invalid page: ' + viewportPosition.anchorPage);
            }

            if (this._canvas.width !== this._viewport.width || this._canvas.height !== this._viewport.height) {
                debug('Canvas dimension change: (%s, %s) -> (%s, %s)', this._canvas.width, this._canvas.height, this._viewport.width, this._viewport.height);

                this._canvas.width = this._viewport.width;
                this._canvas.height = this._viewport.height;
            } else {
                debug('Reload, no size change');
            }

            // FIXME: What hooks should be called here?
            this.goto(viewportPosition.anchorPage, viewportPosition.verticalOffset, viewportPosition.horizontalOffset);

            if (this._canvas.parentNode !== this._outerElement) {
                this._outerElement.insertBefore(this._canvas, this._outerElement.firstChild);
            }

            if (this._hooks.onViewDidLoad) {
                this._hooks.onViewDidLoad();
            }
        }
    }, {
        key: '_setViewportPosition',
        value: function _setViewportPosition(viewportPosition) {
            if (viewportPosition.zoomLevel !== this._zoomLevel) {
                if (this._zoomLevel === null) {
                    throw new TypeError('The current view is not zoomable');
                } else if (viewportPosition.zoomLevel === null) {
                    throw new TypeError('The current view requires a zoom level');
                }

                this._setLayoutToZoomLevel(viewportPosition.zoomLevel);
            }

            this._goto(viewportPosition.anchorPage, viewportPosition.verticalOffset, viewportPosition.horizontalOffset);
        }
    }, {
        key: '_setLayoutToZoomLevel',
        value: function _setLayoutToZoomLevel(zoomLevel) {
            this.layout = new _documentLayout2.default(this._config, zoomLevel);
            this._zoomLevel = zoomLevel;

            (0, _elt.setAttributes)(this._documentElement, {
                style: {
                    height: this.layout.dimensions.height + 'px',
                    width: this.layout.dimensions.width + 'px'
                }
            });

            this._viewport.setInnerDimensions(this.layout.dimensions);
        }
    }, {
        key: 'adjust',
        value: function adjust() {
            this._clearAnimation();

            this._render();

            if (this._hooks.onViewDidUpdate) {
                this._hooks.onViewDidUpdate(this._renderedPages.slice(), null);
            }
        }
    }, {
        key: '_render',
        value: function _render() {
            var _this = this;

            var newRenderedPages = [];
            this.layout.pageGroups.forEach(function (group) {
                if (!_this._viewport.intersectsRegion(group.region)) {
                    return;
                }

                var visiblePages = group.pages.filter(function (page) {
                    return this.isPageVisible(page.index);
                }, _this).map(function (page) {
                    return page.index;
                });

                newRenderedPages.push.apply(newRenderedPages, visiblePages);
            }, this);

            this._ctx.clearRect(0, 0, this._canvas.width, this._canvas.height);
            this._paintOutline(newRenderedPages);

            newRenderedPages.forEach(function (pageIndex) {
                if (!_this._compositeImages[pageIndex]) {
                    var page = _this.layout.getPageInfo(pageIndex);
                    var zoomLevels = _this._sourceResolver.getAllZoomLevelsForPage(page);
                    var composite = new _compositeImage2.default(zoomLevels);
                    composite.updateFromCache(_this._cache);
                    _this._compositeImages[pageIndex] = composite;
                }
            }, this);

            this._initiateTileRequests(newRenderedPages);

            var changes = findChanges(this._renderedPages || [], newRenderedPages);

            changes.removed.forEach(function (pageIndex) {
                delete _this._compositeImages[pageIndex];
            }, this);

            this._renderedPages = newRenderedPages;
            this._paint();

            if (this._hooks.onPageWillLoad) {
                changes.added.forEach(function (pageIndex) {
                    _this._hooks.onPageWillLoad(pageIndex);
                }, this);
            }
        }
    }, {
        key: '_paint',
        value: function _paint() {
            var _this3 = this;

            debug('Repainting');

            var renderedTiles = [];

            this._renderedPages.forEach(function (pageIndex) {
                var _this2 = this;

                this._compositeImages[pageIndex].getTiles(this._zoomLevel).forEach(function (source) {
                    var scaled = getScaledTileRecord(source, _this2._zoomLevel);

                    if (_this2._isTileVisible(pageIndex, scaled)) {
                        renderedTiles.push(source.url);
                        _this2._drawTile(pageIndex, scaled, _this2._cache.get(source.url));
                    }
                }, this);
            }, this);

            var cache = this._cache;

            var changes = findChanges(this._renderedTiles || [], renderedTiles);

            changes.added.forEach(function (url) {
                cache.acquire(url);
            });

            changes.removed.forEach(function (url) {
                cache.release(url);
            });

            if (changes.removed) {
                // FIXME: Should only need to update the composite images
                // for which tiles were removed
                this._renderedPages.forEach(function (pageIndex) {
                    _this3._compositeImages[pageIndex].updateFromCache(_this3._cache);
                }, this);
            }

            this._renderedTiles = renderedTiles;
        }

        // Paint a page outline while the tiles are loading.

    }, {
        key: '_paintOutline',
        value: function _paintOutline(pages) {
            pages.forEach(function (pageIndex) {
                var pageInfo = this.layout.getPageInfo(pageIndex);
                var pageOffset = this._getImageOffset(pageIndex);

                // Ensure the document is drawn to the center of the viewport
                var viewportPaddingX = Math.max(0, (this._viewport.width - this.layout.dimensions.width) / 2);
                var viewportPaddingY = Math.max(0, (this._viewport.height - this.layout.dimensions.height) / 2);

                var viewportOffsetX = pageOffset.left - this._viewport.left + viewportPaddingX;
                var viewportOffsetY = pageOffset.top - this._viewport.top + viewportPaddingY;

                var destXOffset = viewportOffsetX < 0 ? -viewportOffsetX : 0;
                var destYOffset = viewportOffsetY < 0 ? -viewportOffsetY : 0;

                var canvasX = Math.max(0, viewportOffsetX);
                var canvasY = Math.max(0, viewportOffsetY);

                var destWidth = pageInfo.dimensions.width - destXOffset;
                var destHeight = pageInfo.dimensions.height - destYOffset;

                this._ctx.strokeStyle = '#AAA';
                // In order to get a 1px wide line using strokes, we need to start at a 'half pixel'
                this._ctx.strokeRect(canvasX + 0.5, canvasY + 0.5, destWidth, destHeight);
            }, this);
        }

        // This method should be sent all visible pages at once because it will initiate
        // all image requests and cancel any remaining image requests. In the case that
        // a request is ongoing and the tile is still visible in the viewport, the old request
        // is kept active instead of restarting it. The image requests are given a timeout
        // before loading in order to debounce them and have a small reaction time
        // to cancel them and avoid useless requests.

    }, {
        key: '_initiateTileRequests',
        value: function _initiateTileRequests(pages) {
            var _this4 = this;

            // Only requests in this object are kept alive, since all others are not visible in the viewport
            var newPendingRequests = {};

            // Used later as a closure to initiate the image requests with the right source and pageIndex
            var initiateRequest = function initiateRequest(source, pageIndex) {
                var composite = _this4._compositeImages[pageIndex];

                newPendingRequests[source.url] = new _imageRequestHandler2.default({
                    url: source.url,
                    timeoutTime: REQUEST_DEBOUNCE_INTERVAL,
                    load: function load(img) {
                        delete _this4._pendingRequests[source.url];
                        _this4._cache.put(source.url, img);

                        // Awkward way to check for updates
                        if (composite === _this4._compositeImages[pageIndex]) {
                            composite.updateWithLoadedUrls([source.url]);

                            if (_this4._isTileForSourceVisible(pageIndex, source)) {
                                _this4._paint();
                            } else {
                                debugPaints('Page %s, tile %s no longer visible on image load', pageIndex, source.url);
                            }
                        }
                    },
                    error: function error() {
                        // TODO: Could make a limited number of retries, etc.
                        delete _this4._pendingRequests[source.url];
                    }
                });
            };

            for (var i = 0; i < pages.length; i++) {
                var pageIndex = pages[i];
                var tiles = this._sourceResolver.getBestZoomLevelForPage(this.layout.getPageInfo(pageIndex)).tiles;

                for (var j = 0; j < tiles.length; j++) {
                    var source = tiles[j];
                    if (this._cache.has(source.url) || !this._isTileForSourceVisible(pageIndex, source)) {
                        continue;
                    }

                    // Don't create a new request if the tile is already being loaded
                    if (this._pendingRequests[source.url]) {
                        newPendingRequests[source.url] = this._pendingRequests[source.url];
                        delete this._pendingRequests[source.url];
                        continue;
                    }

                    // Use a closure since the load and error methods are going to be called later and
                    // we need to keep the right reference to the source and the page index
                    initiateRequest(source, pageIndex);
                }
            }

            for (var url in this._pendingRequests) {
                this._pendingRequests[url].abort();
            }
            this._pendingRequests = newPendingRequests;
        }
    }, {
        key: '_drawTile',
        value: function _drawTile(pageIndex, scaledTile, img) {
            var tileOffset = this._getTileToDocumentOffset(pageIndex, scaledTile);

            // Ensure the document is drawn to the center of the viewport
            var viewportPaddingX = Math.max(0, (this._viewport.width - this.layout.dimensions.width) / 2);
            var viewportPaddingY = Math.max(0, (this._viewport.height - this.layout.dimensions.height) / 2);

            var viewportOffsetX = tileOffset.left - this._viewport.left + viewportPaddingX;
            var viewportOffsetY = tileOffset.top - this._viewport.top + viewportPaddingY;

            var destXOffset = viewportOffsetX < 0 ? -viewportOffsetX : 0;
            var destYOffset = viewportOffsetY < 0 ? -viewportOffsetY : 0;

            var sourceXOffset = destXOffset / scaledTile.scaleRatio;
            var sourceYOffset = destYOffset / scaledTile.scaleRatio;

            var canvasX = Math.max(0, viewportOffsetX);
            var canvasY = Math.max(0, viewportOffsetY);

            // Ensure that the specified dimensions are no greater than the actual
            // size of the image. Safari won't display the tile if they are.
            var destWidth = Math.min(scaledTile.dimensions.width, img.width * scaledTile.scaleRatio) - destXOffset;
            var destHeight = Math.min(scaledTile.dimensions.height, img.height * scaledTile.scaleRatio) - destYOffset;

            var sourceWidth = destWidth / scaledTile.scaleRatio;
            var sourceHeight = destHeight / scaledTile.scaleRatio;

            if (debugPaints.enabled) {
                debugPaints('Drawing page %s, tile %sx (%s, %s) from %s, %s to viewport at %s, %s, scale %s%%', pageIndex, scaledTile.sourceZoomLevel, scaledTile.row, scaledTile.col, sourceXOffset, sourceYOffset, canvasX, canvasY, Math.round(scaledTile.scaleRatio * 100));
            }

            this._ctx.drawImage(img, sourceXOffset, sourceYOffset, sourceWidth, sourceHeight, canvasX, canvasY, destWidth, destHeight);
        }
    }, {
        key: '_isTileForSourceVisible',
        value: function _isTileForSourceVisible(pageIndex, tileSource) {
            return this._isTileVisible(pageIndex, getScaledTileRecord(tileSource, this._zoomLevel));
        }
    }, {
        key: '_isTileVisible',
        value: function _isTileVisible(pageIndex, scaledTile) {
            var tileOffset = this._getTileToDocumentOffset(pageIndex, scaledTile);

            // FIXME(wabain): This check is insufficient during a zoom transition
            return this._viewport.intersectsRegion({
                top: tileOffset.top,
                bottom: tileOffset.top + scaledTile.dimensions.height,
                left: tileOffset.left,
                right: tileOffset.left + scaledTile.dimensions.width
            });
        }
    }, {
        key: '_getTileToDocumentOffset',
        value: function _getTileToDocumentOffset(pageIndex, scaledTile) {
            var imageOffset = this._getImageOffset(pageIndex);

            return {
                top: imageOffset.top + scaledTile.offset.top,
                left: imageOffset.left + scaledTile.offset.left
            };
        }
    }, {
        key: '_getImageOffset',
        value: function _getImageOffset(pageIndex) {
            return this.layout.getPageOffset(pageIndex, { excludePadding: true });
        }

        // TODO: Update signature

    }, {
        key: 'goto',
        value: function goto(pageIndex, verticalOffset, horizontalOffset) {
            this._clearAnimation();
            this._goto(pageIndex, verticalOffset, horizontalOffset);
            if (this._hooks.onViewDidUpdate) {
                this._hooks.onViewDidUpdate(this._renderedPages.slice(), pageIndex);
            }
        }
    }, {
        key: '_goto',
        value: function _goto(pageIndex, verticalOffset, horizontalOffset) {
            // FIXME(wabain): Move this logic to the viewer
            var pageOffset = this.layout.getPageOffset(pageIndex);

            var desiredVerticalCenter = pageOffset.top + verticalOffset;
            var top = desiredVerticalCenter - parseInt(this._viewport.height / 2, 10);

            var desiredHorizontalCenter = pageOffset.left + horizontalOffset;
            var left = desiredHorizontalCenter - parseInt(this._viewport.width / 2, 10);

            this._viewport.top = top;
            this._viewport.left = left;

            this._render();
        }
    }, {
        key: 'transitionViewportPosition',
        value: function transitionViewportPosition(options) {
            var _this5 = this;

            this._clearAnimation();

            var getPosition = options.getPosition;
            var onViewDidTransition = this._hooks.onViewDidTransition;

            this._animation = _interpolateAnimation2.default.animate({
                duration: options.duration,
                parameters: options.parameters,
                onUpdate: function onUpdate(values) {
                    // TODO: Do image preloading, work with that
                    _this5._setViewportPosition(getPosition(values));
                    _this5._hooks.onZoomLevelWillChange(values.zoomLevel);

                    if (onViewDidTransition) {
                        onViewDidTransition();
                    }
                },
                onEnd: function onEnd(info) {
                    if (options.onEnd) {
                        options.onEnd(info);
                    }

                    if (_this5._hooks.onViewDidUpdate && !info.interrupted) {
                        _this5._hooks.onViewDidUpdate(_this5._renderedPages.slice(), null);
                    }
                }
            });
        }
    }, {
        key: '_clearAnimation',
        value: function _clearAnimation() {
            if (this._animation) {
                this._animation.cancel();
                this._animation = null;
            }
        }
    }, {
        key: 'preload',
        value: function preload() {
            // TODO
        }
    }, {
        key: 'isPageVisible',
        value: function isPageVisible(pageIndex) {
            if (!this.layout) {
                return false;
            }

            var page = this.layout.getPageInfo(pageIndex);

            if (!page) {
                return false;
            }

            return this._viewport.intersectsRegion(this.layout.getPageRegion(pageIndex));
        }
    }, {
        key: 'getRenderedPages',
        value: function getRenderedPages() {
            return this._renderedPages.slice();
        }
    }, {
        key: 'destroy',
        value: function destroy() {
            var _this6 = this;

            this._clearAnimation();

            // FIXME(wabain): I don't know if we should actually do this
            Object.keys(this._pendingRequests).forEach(function (req) {
                var handler = _this6._pendingRequests[req];
                delete _this6._pendingRequests[req];

                handler.abort();
            }, this);

            this._canvas.parentNode.removeChild(this._canvas);
        }
    }], [{
        key: 'getCompatibilityErrors',
        value: function getCompatibilityErrors() {
            if (typeof HTMLCanvasElement !== 'undefined') {
                return null;
            }

            return ['Your browser lacks support for the ', (0, _elt.elt)('pre', 'canvas'), ' element. Please upgrade your browser.'];
        }
    }]);

    return Renderer;
}();

exports.default = Renderer;


function getScaledTileRecord(source, scaleFactor) {
    var scaleRatio = void 0;

    if (scaleFactor === null) {
        scaleRatio = 1;
    } else {
        scaleRatio = Math.pow(2, scaleFactor - source.zoomLevel);
    }

    return {
        sourceZoomLevel: source.zoomLevel,
        scaleRatio: scaleRatio,
        row: source.row,
        col: source.col,
        dimensions: {
            width: source.dimensions.width * scaleRatio,
            height: source.dimensions.height * scaleRatio
        },
        offset: {
            left: source.offset.left * scaleRatio,
            top: source.offset.top * scaleRatio
        },
        url: source.url
    };
}

function findChanges(oldArray, newArray) {
    if (oldArray === newArray) {
        return {
            added: [],
            removed: []
        };
    }

    var removed = oldArray.filter(function (oldEntry) {
        return newArray.indexOf(oldEntry) === -1;
    });

    var added = newArray.filter(function (newEntry) {
        return oldArray.indexOf(newEntry) === -1;
    });

    return {
        added: added,
        removed: removed
    };
}

/***/ }),

/***/ "./source/js/settings-view.js":
/*!************************************!*\
  !*** ./source/js/settings-view.js ***!
  \************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = createSettingsView;
function createSettingsView(sources) {
    var obj = {};

    sources.forEach(function (source) {
        registerMixin(obj, source);
    });

    return obj;
}

function registerMixin(obj, mixin) {
    Object.keys(mixin).forEach(function (key) {
        Object.defineProperty(obj, key, {
            get: function get() {
                return mixin[key];
            },
            set: function set() {
                // TODO: Make everything strict mode so this isn't needed
                throw new TypeError('Cannot set settings.' + key);
            }
        });
    });
}

/***/ }),

/***/ "./source/js/tile-coverage-map.js":
/*!****************************************!*\
  !*** ./source/js/tile-coverage-map.js ***!
  \****************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var TileCoverageMap = function () {
    function TileCoverageMap(rows, cols) {
        _classCallCheck(this, TileCoverageMap);

        this._rows = rows;
        this._cols = cols;
        this._map = new Array(rows).fill(null).map(function () {
            return new Array(cols).fill(false);
        });
    }

    _createClass(TileCoverageMap, [{
        key: "isLoaded",
        value: function isLoaded(row, col) {
            // Return true for out of bounds tiles because they
            // don't need to load. (Unfortunately this will also
            // mask logical errors.)
            if (row >= this._rows || col >= this._cols) return true;

            return this._map[row][col];
        }
    }, {
        key: "set",
        value: function set(row, col, value) {
            this._map[row][col] = value;
        }
    }, {
        key: "get",
        value: function get() {
            console.log("JSHint: Requires a getter when setter is set, otherwise lint tests will fail.");
        }
    }]);

    return TileCoverageMap;
}();

exports.default = TileCoverageMap;

/***/ }),

/***/ "./source/js/toolbar.js":
/*!******************************!*\
  !*** ./source/js/toolbar.js ***!
  \******************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _divaGlobal = __webpack_require__(/*! ./diva-global */ "./source/js/diva-global.js");

var _divaGlobal2 = _interopRequireDefault(_divaGlobal);

var _elt = __webpack_require__(/*! ./utils/elt */ "./source/js/utils/elt.js");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var Toolbar = function () {
    function Toolbar(viewer) {
        _classCallCheck(this, Toolbar);

        this.viewer = viewer;
        this.settings = viewer.settings;
    }

    _createClass(Toolbar, [{
        key: '_elemAttrs',
        value: function _elemAttrs(ident, base) {
            var attrs = {
                id: this.settings.ID + ident,
                class: 'diva-' + ident
            };

            if (base) return Object.assign(attrs, base);else return attrs;
        }

        /** Convenience function to subscribe to a Diva event */

    }, {
        key: '_subscribe',
        value: function _subscribe(event, callback) {
            _divaGlobal2.default.Events.subscribe(event, callback, this.settings.ID);
        }
    }, {
        key: 'createButton',
        value: function createButton(name, label, callback, icon) {
            var button = (0, _elt.elt)('button', {
                type: 'button',
                id: this.settings.ID + name,
                class: 'diva-' + name + ' diva-button',
                title: label
            });

            if (icon) button.appendChild(icon);

            if (callback) button.addEventListener('click', callback);

            return button;
        }
    }, {
        key: 'createLabel',
        value: function createLabel(name, id, label, innerName, innerValue) {
            return (0, _elt.elt)('div', { id: this.settings.ID + id, class: name + ' diva-label' }, [label, (0, _elt.elt)('span', { id: this.settings.ID + innerName }, innerValue)]);
        }
    }, {
        key: 'createZoomButtons',
        value: function createZoomButtons() {
            var _this = this;

            var zoomOutIcon = this._createZoomOutIcon();
            var zoomInIcon = this._createZoomInIcon();

            var zoomButtons = [this.createButton('zoom-out-button', 'Zoom Out', function () {
                _this.viewer.setZoomLevel(_this.settings.zoomLevel - 1);
            }, zoomOutIcon), this.createButton('zoom-in-button', 'Zoom In', function () {
                _this.viewer.setZoomLevel(_this.settings.zoomLevel + 1);
            }, zoomInIcon), this.createLabel('diva-zoom-label', 'zoom-label', 'Zoom level: ', 'zoom-level', this.settings.zoomLevel + 1)];

            var zoomHandler = function zoomHandler() {
                var labelEl = document.getElementById(this.settings.ID + 'zoom-level');
                labelEl.textContent = this.settings.zoomLevel + 1;
            };

            this._subscribe('ZoomLevelDidChange', zoomHandler);
            this._subscribe('ViewerDidLoad', zoomHandler);

            return (0, _elt.elt)('div', { id: this.settings.ID + "zoom-controls", style: "display: none" }, zoomButtons);
        }
    }, {
        key: 'createGridControls',
        value: function createGridControls() {
            var _this2 = this;

            var gridMoreIcon = this._createGridMoreIcon();
            var gridFewerIcon = this._createGridFewerIcon();

            var gridButtons = [this.createButton('grid-out-button', 'Fewer', function () {
                _this2.viewer.setGridPagesPerRow(_this2.settings.pagesPerRow - 1);
            }, gridFewerIcon), this.createButton('grid-in-button', 'More', function () {
                _this2.viewer.setGridPagesPerRow(_this2.settings.pagesPerRow + 1);
            }, gridMoreIcon), this.createLabel('diva-grid-label', 'grid-label', 'Pages per row: ', 'pages-per-row', this.settings.pagesPerRow)];

            var gridChangeHandler = function gridChangeHandler() {
                var labelEl = document.getElementById(this.settings.ID + 'pages-per-row');
                labelEl.textContent = this.settings.pagesPerRow;
            };

            this._subscribe('GridRowNumberDidChange', gridChangeHandler);

            return (0, _elt.elt)('div', { id: this.settings.ID + "grid-controls", style: "display:none" }, gridButtons);
        }
    }, {
        key: 'createViewMenu',
        value: function createViewMenu() {
            var _this3 = this;

            var viewOptionsList = (0, _elt.elt)('div', this._elemAttrs('view-options'));
            var gridViewIcon = this._createGridViewIcon();
            var bookViewIcon = this._createBookViewIcon();
            var pageViewIcon = this._createPageViewIcon();

            var viewOptionsToggle = function viewOptionsToggle() {
                viewOptionsList.style.display = viewOptionsList.style.display === "none" ? "block" : "none";
            };

            var changeViewButton = this.createButton('view-icon', 'Change view', viewOptionsToggle);

            var selectView = function selectView(view) {
                _this3.viewer.changeView(view);

                //hide view menu
                viewOptionsList.style.display = "none";
            };

            var updateViewMenu = function updateViewMenu() {
                var viewIconClasses = ' diva-view-icon diva-button';

                // display the icon of the mode we're currently in (?)
                if (_this3.settings.inGrid) {
                    changeViewButton.appendChild(gridViewIcon);
                    changeViewButton.className = 'diva-grid-icon' + viewIconClasses;
                } else if (_this3.settings.inBookLayout) {
                    changeViewButton.appendChild(bookViewIcon);
                    changeViewButton.className = 'diva-book-icon' + viewIconClasses;
                } else {
                    changeViewButton.appendChild(pageViewIcon);
                    changeViewButton.className = 'diva-document-icon' + viewIconClasses;
                }

                var viewOptions = document.createDocumentFragment();

                // then display document, book, and grid buttons in that order, excluding the current view
                if (_this3.settings.inGrid || _this3.settings.inBookLayout) viewOptions.appendChild(_this3.createButton('document-icon', 'Document View', selectView.bind(null, 'document'), pageViewIcon));

                if (_this3.settings.inGrid || !_this3.settings.inBookLayout) viewOptions.appendChild(_this3.createButton('book-icon', 'Book View', selectView.bind(null, 'book'), bookViewIcon));

                if (!_this3.settings.inGrid) viewOptions.appendChild(_this3.createButton('grid-icon', 'Grid View', selectView.bind(null, 'grid'), gridViewIcon));

                // remove old menu
                while (viewOptionsList.firstChild) {
                    viewOptionsList.removeChild(viewOptionsList.firstChild);
                }

                // insert new menu
                viewOptionsList.appendChild(viewOptions);
            };

            document.addEventListener('mouseup', function (event) {
                if (viewOptionsList !== event.target) {
                    viewOptionsList.style.display = 'none';
                }
            });

            this._subscribe('ViewDidSwitch', updateViewMenu);
            this._subscribe('ObjectDidLoad', updateViewMenu);

            return (0, _elt.elt)('div', this._elemAttrs('view-menu'), changeViewButton, viewOptionsList);
        }
    }, {
        key: 'createFullscreenButton',
        value: function createFullscreenButton() {
            var _this4 = this;

            var fullscreenIcon = this._createFullscreenIcon();

            return this.createButton('fullscreen-icon', 'Toggle fullscreen mode', function () {
                _this4.viewer.toggleFullscreenMode();
            }, fullscreenIcon);
        }
    }, {
        key: 'toggleZoomGridControls',
        value: function toggleZoomGridControls() {
            if (!this.settings.inGrid) {
                document.getElementById(this.settings.ID + "zoom-controls").style.display = "block";
                document.getElementById(this.settings.ID + "grid-controls").style.display = "none";
            } else {
                document.getElementById(this.settings.ID + "zoom-controls").style.display = "none";
                document.getElementById(this.settings.ID + "grid-controls").style.display = "block";
            }
        }
    }, {
        key: 'render',
        value: function render() {
            this._subscribe("ViewDidSwitch", this.toggleZoomGridControls);
            this._subscribe("ObjectDidLoad", this.toggleZoomGridControls);

            var leftTools = [this.createZoomButtons(), this.createGridControls()];
            var rightTools = [this.createViewMenu(), this.createFullscreenButton()];

            var tools = (0, _elt.elt)('div', this._elemAttrs('tools'), (0, _elt.elt)('div', this._elemAttrs('tools-left'), leftTools), (0, _elt.elt)('div', this._elemAttrs('tools-right'), rightTools));

            this.settings.toolbarParentObject.insertBefore(tools, this.settings.toolbarParentObject.firstChild);
        }
    }, {
        key: '_createToolbarIcon',
        value: function _createToolbarIcon(paths) {
            var icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            icon.setAttributeNS(null, 'viewBox', "0 0 25 25");
            icon.setAttributeNS(null, 'x', '0px');
            icon.setAttributeNS(null, 'y', '0px');
            icon.setAttributeNS(null, 'style', "enable-background:new 0 0 48 48;");

            var glyph = document.createElementNS("http://www.w3.org/2000/svg", "g");
            glyph.setAttributeNS(null, "transform", "matrix(1, 0, 0, 1, -12, -12)");

            paths.forEach(function (path) {
                var pEl = document.createElementNS("http://www.w3.org/2000/svg", "path");
                pEl.setAttributeNS(null, "d", path);
                glyph.appendChild(pEl);
            });

            icon.appendChild(glyph);
            return icon;
        }
    }, {
        key: '_createZoomOutIcon',
        value: function _createZoomOutIcon() {
            var paths = ["M19.5,23c-0.275,0-0.5-0.225-0.5-0.5v-1c0-0.275,0.225-0.5,0.5-0.5h7c0.275,0,0.5,0.225,0.5,0.5v1c0,0.275-0.225,0.5-0.5,0.5H19.5z", "M37.219,34.257l-2.213,2.212c-0.202,0.202-0.534,0.202-0.736,0l-6.098-6.099c-1.537,0.993-3.362,1.577-5.323,1.577c-5.431,0-9.849-4.418-9.849-9.849c0-5.431,4.418-9.849,9.849-9.849c5.431,0,9.849,4.418,9.849,9.849c0,1.961-0.584,3.786-1.576,5.323l6.098,6.098C37.422,33.722,37.422,34.054,37.219,34.257z M29.568,22.099c0-3.706-3.014-6.72-6.72-6.72c-3.706,0-6.72,3.014-6.72,6.72c0,3.706,3.014,6.72,6.72,6.72C26.555,28.818,29.568,25.805,29.568,22.099z"];

            return this._createToolbarIcon(paths);
        }
    }, {
        key: '_createZoomInIcon',
        value: function _createZoomInIcon() {
            var paths = ["M37.469,34.257l-2.213,2.212c-0.202,0.202-0.534,0.202-0.736,0l-6.098-6.099c-1.537,0.993-3.362,1.577-5.323,1.577c-5.431,0-9.849-4.418-9.849-9.849c0-5.431,4.418-9.849,9.849-9.849c5.431,0,9.849,4.418,9.849,9.849c0,1.961-0.584,3.786-1.576,5.323l6.098,6.098C37.672,33.722,37.672,34.054,37.469,34.257z M29.818,22.099c0-3.706-3.014-6.72-6.72-6.72c-3.706,0-6.72,3.014-6.72,6.72c0,3.706,3.014,6.72,6.72,6.72C26.805,28.818,29.818,25.805,29.818,22.099z M26.5,21H24v-2.5c0-0.275-0.225-0.5-0.5-0.5h-1c-0.275,0-0.5,0.225-0.5,0.5V21h-2.5c-0.275,0-0.5,0.225-0.5,0.5v1c0,0.275,0.225,0.5,0.5,0.5H22v2.5c0,0.275,0.225,0.5,0.5,0.5h1c0.275,0,0.5-0.225,0.5-0.5V23h2.5c0.275,0,0.5-0.225,0.5-0.5v-1C27,21.225,26.775,21,26.5,21z"];
            return this._createToolbarIcon(paths);
        }
    }, {
        key: '_createGridMoreIcon',
        value: function _createGridMoreIcon() {
            var paths = ["M29.5,35c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H29.5z M21.5,35c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H21.5z M13.5,35c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H13.5z M29.5,27c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H29.5z M21.5,27c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H21.5z M13.5,27c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H13.5z M29.5,19c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H29.5z M21.5,19c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H21.5z M13.5,19c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H13.5z"];
            return this._createToolbarIcon(paths);
        }
    }, {
        key: '_createGridFewerIcon',
        value: function _createGridFewerIcon() {
            var paths = ["M25.5,35c-0.275,0-0.5-0.225-0.5-0.5v-9c0-0.275,0.225-0.5,0.5-0.5h9c0.275,0,0.5,0.225,0.5,0.5v9c0,0.275-0.225,0.5-0.5,0.5H25.5z M22.5,35c0.275,0,0.5-0.225,0.5-0.5v-9c0-0.275-0.225-0.5-0.5-0.5h-9c-0.275,0-0.5,0.225-0.5,0.5v9c0,0.275,0.225,0.5,0.5,0.5H22.5z M34.5,23c0.275,0,0.5-0.225,0.5-0.5v-9c0-0.275-0.225-0.5-0.5-0.5h-9c-0.275,0-0.5,0.225-0.5,0.5v9c0,0.275,0.225,0.5,0.5,0.5H34.5z M22.5,23c0.275,0,0.5-0.225,0.5-0.5v-9c0-0.275-0.225-0.5-0.5-0.5h-9c-0.275,0-0.5,0.225-0.5,0.5v9c0,0.275,0.225,0.5,0.5,0.5H22.5z"];
            return this._createToolbarIcon(paths);
        }
    }, {
        key: '_createGridViewIcon',
        value: function _createGridViewIcon() {
            var paths = ["M29.5,35c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H29.5z M21.5,35c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H21.5z M13.5,35c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H13.5z M29.5,27c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H29.5z M21.5,27c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H21.5z M13.5,27c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H13.5z M29.5,19c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H29.5z M21.5,19c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H21.5z M13.5,19c-0.275,0-0.5-0.225-0.5-0.5v-5c0-0.275,0.225-0.5,0.5-0.5h5c0.275,0,0.5,0.225,0.5,0.5v5c0,0.275-0.225,0.5-0.5,0.5H13.5z"];
            return this._createToolbarIcon(paths);
        }
    }, {
        key: '_createBookViewIcon',
        value: function _createBookViewIcon() {
            var paths = ["M35,16.8v-1.323c0,0-2.292-1.328-5.74-1.328c-3.448,0-5.26,1.25-5.26,1.25s-1.813-1.25-5.26-1.25c-3.448,0-5.74,1.328-5.74,1.328V16.8l-1,0.531v0.021v15.687c0,0,4.531-1.578,6.999-1.578c2.468,0,5.001,0.885,5.001,0.885s2.532-0.885,5-0.885c0.306,0,0.643,0.024,1,0.066v4.325l1.531-2.016L33,35.852v-3.72c2,0.43,3,0.906,3,0.906V17.352v-0.021L35,16.8z M23,29.03c-1-0.292-2.584-0.679-3.981-0.679c-2.246,0-3.019,0.404-4.019,0.699V16.634c0,0,1.125-0.699,4.019-0.699c1.694,0,2.981,0.417,3.981,1.126V29.03z M33,29.051c-1-0.295-1.773-0.699-4.02-0.699c-1.396,0-2.981,0.387-3.98,0.679V17.06c1-0.709,2.286-1.126,3.98-1.126c2.895,0,4.02,0.699,4.02,0.699V29.051z"];
            return this._createToolbarIcon(paths);
        }
    }, {
        key: '_createPageViewIcon',
        value: function _createPageViewIcon() {
            var paths = ["M29.425,29h4.47L29,33.934v-4.47C29,29.19,29.151,29,29.425,29z M34,14.563V28h-5.569C28.157,28,28,28.196,28,28.47V34H14.497C14.223,34,14,33.71,14,33.437V14.563C14,14.29,14.223,14,14.497,14h18.9C33.672,14,34,14.29,34,14.563z M25.497,26.497C25.497,26.223,25.275,26,25,26h-7c-0.275,0-0.497,0.223-0.497,0.497v1.006C17.503,27.777,17.725,28,18,28h7c0.275,0,0.497-0.223,0.497-0.497V26.497z M30.497,22.497C30.497,22.223,30.275,22,30,22H18c-0.275,0-0.497,0.223-0.497,0.497v1.006C17.503,23.777,17.725,24,18,24h12c0.275,0,0.497-0.223,0.497-0.497V22.497z M30.497,18.497C30.497,18.223,30.275,18,30,18H18c-0.275,0-0.497,0.223-0.497,0.497v1.006C17.503,19.777,17.725,20,18,20h12c0.275,0,0.497-0.223,0.497-0.497V18.497z"];

            return this._createToolbarIcon(paths);
        }
    }, {
        key: '_createFullscreenIcon',
        value: function _createFullscreenIcon() {
            var paths = ["M35,12H13c-0.55,0-1,0.45-1,1v22c0,0.55,0.45,1,1,1h22c0.55,0,1-0.45,1-1V13C36,12.45,35.55,12,35,12z M34,34H14V14h20V34z", "M17,21.75v-4.5c0-0.138,0.112-0.25,0.25-0.25h4.5c0.138,0,0.17,0.08,0.073,0.177l-1.616,1.616l1.823,1.823c0.097,0.097,0.097,0.256,0,0.354l-1.061,1.06c-0.097,0.097-0.256,0.097-0.354,0l-1.823-1.823l-1.616,1.616C17.08,21.92,17,21.888,17,21.75z M20.97,25.97c-0.097-0.097-0.256-0.097-0.354,0l-1.823,1.823l-1.616-1.616C17.08,26.08,17,26.112,17,26.25v4.5c0,0.138,0.112,0.25,0.25,0.25h4.5c0.138,0,0.17-0.08,0.073-0.177l-1.616-1.616l1.823-1.823c0.097-0.097,0.097-0.256,0-0.354L20.97,25.97z M30.75,17h-4.5c-0.138,0-0.17,0.08-0.073,0.177l1.616,1.616l-1.823,1.823c-0.097,0.097-0.097,0.256,0,0.354l1.061,1.06c0.097,0.097,0.256,0.097,0.354,0l1.823-1.823l1.616,1.616C30.92,21.92,31,21.888,31,21.75v-4.5C31,17.112,30.888,17,30.75,17z M30.823,26.177l-1.616,1.616l-1.823-1.823c-0.097-0.097-0.256-0.097-0.354,0l-1.061,1.06c-0.097,0.097-0.097,0.256,0,0.354l1.823,1.823l-1.616,1.616C26.08,30.92,26.112,31,26.25,31h4.5c0.138,0,0.25-0.112,0.25-0.25v-4.5C31,26.112,30.92,26.08,30.823,26.177z M26,22.5c0-0.275-0.225-0.5-0.5-0.5h-3c-0.275,0-0.5,0.225-0.5,0.5v3c0,0.275,0.225,0.5,0.5,0.5h3c0.275,0,0.5-0.225,0.5-0.5V22.5z"];

            return this._createToolbarIcon(paths);
        }
    }]);

    return Toolbar;
}();

// export default function createToolbar (viewer)
// {
//     const settings = viewer.getSettings();
//
//     // FIXME(wabain): Temporarily copied from within Diva
//     const elemAttrs = (ident, base) => {
//         const attrs = {
//             id: settings.ID + ident,
//             class: 'diva-' + ident
//         };
//
//         if (base)
//             return Object.assign(attrs, base);
//         else
//             return attrs;
//     };
//
//     /** Convenience function to subscribe to a Diva event */
//     const subscribe = (event, callback) => {
//         diva.Events.subscribe(event, callback, settings.ID);
//     };
//
//     // Creates a toolbar button
//     const createButtonElement = (name, label, callback) => {
//         const button = elt('button', {
//             type: 'button',
//             id: settings.ID + name,
//             class: 'diva-' + name + ' diva-button',
//             title: label
//         });
//
//         if (callback)
//             button.addEventListener('click', callback, false);
//
//         return button;
//     };
//
//     // Higher-level function for creators of zoom and grid controls
//     const getResolutionControlCreator = config => () => {
//         let controls;
//
//         switch (settings[config.controllerSetting])
//         {
//             case 'slider':
//                 controls = config.createSlider();
//                 break;
//
//             case 'buttons':
//                 controls = config.createButtons();
//                 break;
//
//             default:
//                 // Don't display anything
//                 return null;
//         }
//
//         const wrapper = elt('span',
//             controls,
//             config.createLabel()
//         );
//
//         const updateWrapper = () => {
//             if (settings.inGrid === config.showInGrid)
//                 wrapper.style.display = 'inline';
//             else
//                 wrapper.style.display = 'none';
//         };
//
//         subscribe('ViewDidSwitch', updateWrapper);
//         subscribe('ObjectDidLoad', updateWrapper);
//
//         // Set initial value
//         updateWrapper();
//
//         return wrapper;
//     };
//
//     // Zoom controls
//     const createZoomControls = getResolutionControlCreator({
//         controllerSetting: 'enableZoomControls',
//         showInGrid: false,
//
//         createSlider: function ()
//         {
//             const elem = createSlider('zoom-slider', {
//                 step: 0.1,
//                 value: settings.zoomLevel,
//                 min: settings.minZoomLevel,
//                 max: settings.maxZoomLevel
//             });
//
//             elem.addEventListener('input', () =>
//             {
//                 const floatValue = parseFloat(this.value);
//                 viewer.setZoomLevel(floatValue);
//             });
//
//             elem.addEventListener('change', () =>
//             {
//                 const floatValue = parseFloat(this.value);
//                 if (floatValue !== settings.zoomLevel)
//                     viewer.setZoomLevel(floatValue);
//             });
//
//             const updateSlider = () => {
//                 if (settings.zoomLevel !== $elem.val())
//                     $elem.val(settings.zoomLevel);
//             };
//
//             subscribe('ZoomLevelDidChange', updateSlider);
//             subscribe('ViewerDidLoad', () => {
//                 elt.setAttributes(elem, {
//                     min: settings.minZoomLevel,
//                     max: settings.maxZoomLevel
//                 });
//
//                 updateSlider();
//             });
//
//             return elem;
//         },
//
//         createButtons: function ()
//         {
//             return elt('span',
//                 createButtonElement('zoom-out-button', 'Zoom Out', () => {
//                     viewer.setZoomLevel(settings.zoomLevel - 1);
//                 }),
//                 createButtonElement('zoom-in-button', 'Zoom In', () => {
//                     viewer.setZoomLevel(settings.zoomLevel + 1);
//                 })
//             );
//         },
//
//         createLabel: function ()
//         {
//             const elem = createLabel('diva-zoom-label', 'zoom-label', 'Zoom level: ', 'zoom-level', settings.zoomLevel);
//             const textSpan = $(elem).find(settings.selector + 'zoom-level')[0];
//
//             const updateText = () => {
//                 textSpan.textContent = settings.zoomLevel.toFixed(2);
//             };
//
//             subscribe('ZoomLevelDidChange', updateText);
//             subscribe('ViewerDidLoad', updateText);
//
//             return elem;
//         }
//     });
//
//     // Grid controls
//     const createGridControls = getResolutionControlCreator({
//         controllerSetting: 'enableGridControls',
//         showInGrid: true,
//
//         createSlider: function ()
//         {
//             const elem = createSlider('grid-slider', {
//                 value: settings.pagesPerRow,
//                 min: settings.minPagesPerRow,
//                 max: settings.maxPagesPerRow
//             });
//
//             elem.addEventListener('input', () => {
//                 const intValue = parseInt(elem.value, 10);
//                 viewer.setGridPagesPerRow(intValue);
//             });
//
//             elem.addEventListener('change', () => {
//                 const intValue = parseInt(elem.value, 10);
//                 if (intValue !== settings.pagesPerRow)
//                     viewer.setGridPagesPerRow(intValue);
//             });
//
//             subscribe('GridRowNumberDidChange', () => {
//                 // Update the position of the handle within the slider
//                 if (settings.pagesPerRow !== $elem.val())
//                     $elem.val(settings.pagesPerRow);
//             });
//
//             return elem;
//         },
//
//         createButtons: function ()
//         {
//             return elt('span',
//                 createButtonElement('grid-out-button', 'Zoom Out', () => {
//                     viewer.setGridPagesPerRow(settings.pagesPerRow - 1);
//                 }),
//                 createButtonElement('grid-in-button', 'Zoom In', () => {
//                     viewer.setGridPagesPerRow(settings.pagesPerRow + 1);
//                 })
//             );
//         },
//
//         createLabel: function ()
//         {
//             const elem = createLabel('diva-grid-label', 'grid-label', 'Pages per row: ', 'pages-per-row', settings.pagesPerRow);
//             const textSpan = $(elem).find(settings.selector + 'pages-per-row')[0];
//
//             subscribe('GridRowNumberDidChange', () => {
//                 textSpan.textContent = settings.pagesPerRow;
//             });
//
//             return elem;
//         }
//     });
//
//     const createViewMenu = () => {
//         const viewOptionsList = elt('div', elemAttrs('view-options'));
//
//         const changeViewButton = createButtonElement('view-icon', 'Change view', () => {
//             $(viewOptionsList).toggle();
//         });
//
//         document.addEventListener('mouseup', event => {
//             const container = $(viewOptionsList);
//
//             if (!container.is(event.target) && container.has(event.target).length === 0 && event.target.id !== settings.ID + 'view-icon')
//             {
//                 container.hide();
//             }
//         });
//
//         const selectView = view => {
//             viewer.changeView(view);
//
//             //hide view menu
//             $(viewOptionsList).hide();
//         };
//
//         const updateViewMenu = () => {
//             const viewIconClasses = ' diva-view-icon diva-button';
//
//             // display the icon of the mode we're currently in (?)
//             if (settings.inGrid)
//             {
//                 changeViewButton.className = 'diva-grid-icon' + viewIconClasses;
//             }
//             else if (settings.inBookLayout)
//             {
//                 changeViewButton.className = 'diva-book-icon' + viewIconClasses;
//             }
//             else
//             {
//                 changeViewButton.className = 'diva-document-icon' + viewIconClasses;
//             }
//
//             const viewOptions = document.createDocumentFragment();
//
//             // then display document, book, and grid buttons in that order, excluding the current view
//             if (settings.inGrid || settings.inBookLayout)
//                 viewOptions.appendChild(createButtonElement('document-icon', 'Document View', selectView.bind(null, 'document')));
//
//             if (settings.inGrid || !settings.inBookLayout)
//                 viewOptions.appendChild(createButtonElement('book-icon', 'Book View', selectView.bind(null, 'book')));
//
//             if (!settings.inGrid)
//                 viewOptions.appendChild(createButtonElement('grid-icon', 'Grid View', selectView.bind(null, 'grid')));
//
//             // remove old menu
//             while (viewOptionsList.firstChild)
//             {
//                 viewOptionsList.removeChild(viewOptionsList.firstChild);
//             }
//
//             // insert new menu
//             viewOptionsList.appendChild(viewOptions);
//         };
//
//         subscribe('ViewDidSwitch', updateViewMenu);
//         subscribe('ObjectDidLoad', updateViewMenu);
//
//         return elt('div', elemAttrs('view-menu'),
//             changeViewButton,
//             viewOptionsList
//         );
//     };
//
//     const createSlider = (name, options) => elt('input', options, {
//         id: settings.ID + name,
//         class: 'diva-' + name + ' diva-slider',
//         type: 'range'
//     });
//
//     const createLabel = (name, id, label, innerName, innerValue) => elt('div', {
//             id: settings.ID + id,
//             class: name + ' diva-label'
//         },
//         [
//             label,
//             elt('span', {
//                 id: settings.ID + innerName
//             }, innerValue)
//         ]);
//
//     const createPageNavigationControls = () => {
//         // Go to page form
//         const gotoForm = settings.enableGotoPage ? createGotoPageForm() : null;
//
//         return elt('span', elemAttrs('page-nav'),
//             createPageLabel(), // 'Page x of y' label
//             gotoForm
//         );
//     };
//
//     const createGotoPageForm = () => {
//         const gotoPageInput = elt('input', {
//             id: settings.ID + 'goto-page-input',
//             class: 'diva-input diva-goto-page-input',
//             autocomplete: 'off',
//             type: 'text'
//         });
//
//         const gotoPageSubmit = elt('input', {
//             id: settings.ID + 'goto-page-submit',
//             class: 'diva-button diva-button-text',
//             type: 'submit',
//             value: 'Go'
//         });
//
//         const inputSuggestions = elt('div', {
//                 id: settings.ID + 'input-suggestions',
//                 class: 'diva-input-suggestions'
//             }
//         );
//
//         const gotoForm = elt('form', {
//                 id: settings.ID + 'goto-page',
//                 class: 'diva-goto-form'
//             },
//             gotoPageInput,
//             gotoPageSubmit,
//             inputSuggestions
//         );
//
//         $(gotoForm).on('submit', () => {
//             const desiredPageLabel = gotoPageInput.value;
//
//             if (settings.onGotoSubmit && typeof settings.onGotoSubmit === "function")
//             {
//                 const pageIndex = settings.onGotoSubmit(desiredPageLabel);
//                 if (!viewer.gotoPageByIndex(pageIndex))
//                     alert("No page could be found with that label or page number");
//
//             }
//             else // Default if no function is specified in the settings
//             {
//                 if (!viewer.gotoPageByLabel(desiredPageLabel))
//                     alert("No page could be found with that label or page number");
//             }
//
//             // Hide the suggestions
//             inputSuggestions.style.display = 'none';
//
//             // Prevent the default action of reloading the page
//             return false;
//         });
//
//         $(gotoPageInput).on('input focus', () => {
//             inputSuggestions.innerHTML = ''; // Remove all previous suggestions
//
//             const value = gotoPageInput.value;
//             let numSuggestions = 0;
//             if (settings.enableGotoSuggestions && value)
//             {
//                 const pages = settings.manifest.pages;
//                 for (let i = 0, len = pages.length; i < len && numSuggestions < 10; i++)
//                 {
//                     if (pages[i].l.toLowerCase().indexOf(value.toLowerCase()) > -1)
//                     {
//                         const newInputSuggestion = elt('div', {
//                                 class: 'diva-input-suggestion'
//                             },
//                             pages[i].l
//                         );
//
//                         inputSuggestions.appendChild(newInputSuggestion);
//
//                         numSuggestions++;
//                     }
//                 }
//
//                 // Show label suggestions
//                 if (numSuggestions > 0)
//                     inputSuggestions.style.display = 'block';
//             }
//             else
//                 inputSuggestions.style.display = 'none';
//         });
//
//         $(gotoPageInput).on('keydown', e => {
//             let el;
//             if (e.keyCode === 13) // 'Enter' key
//             {
//                 const active = $('.active', inputSuggestions);
//                 if (active.length)
//                     gotoPageInput.value = active.text();
//
//             }
//             if (e.keyCode === 38) // Up arrow key
//             {
//                 el = $('.active', inputSuggestions);
//                 const prevEl = el.prev();
//                 if (prevEl.length)
//                 {
//                     el.removeClass('active');
//                     prevEl.addClass('active');
//                 }
//                 else
//                 {
//                     el.removeClass('active');
//                     $('.diva-input-suggestion:last', inputSuggestions).addClass('active');
//                 }
//             }
//             else if (e.keyCode === 40) // Down arrow key
//             {
//                 el = $('.active', inputSuggestions);
//                 const nextEl = el.next();
//                 if (nextEl.length)
//                 {
//                     el.removeClass('active');
//                     nextEl.addClass('active');
//                 }
//                 else
//                 {
//                     el.removeClass('active');
//                     $('.diva-input-suggestion:first', inputSuggestions).addClass('active');
//                 }
//             }
//         });
//
//         $(inputSuggestions).on('mousedown', '.diva-input-suggestion', function()
//         {
//             gotoPageInput.value = this.textContent;
//             inputSuggestions.style.display = 'none';
//             $(gotoPageInput).trigger('submit');
//         });
//
//         $(gotoPageInput).on('blur', () => {
//             // Hide label suggestions
//             inputSuggestions.style.display = 'none';
//         });
//
//         return gotoForm;
//     };
//
//     const createPageLabel = () => {
//         // Current page
//         const currentPage = elt('span', {
//             id: settings.ID + 'current-page'
//         });
//
//         const updateCurrentPage = () => {
//             currentPage.textContent = viewer.getCurrentAliasedPageIndex();
//         };
//
//         subscribe('VisiblePageDidChange', updateCurrentPage);
//         subscribe('ViewerDidLoad', updateCurrentPage);
//
//         // Number of pages
//         const numPages = elt('span', {
//             id: settings.ID + 'num-pages'
//         });
//
//         const updateNumPages = () => {
//             numPages.textContent = settings.numPages;
//         };
//
//         subscribe('NumberOfPagesDidChange', updateNumPages);
//         subscribe('ObjectDidLoad', updateNumPages);
//
//         return elt('span', {
//                 class: 'diva-page-label diva-label'
//             },
//             'Page ', currentPage, ' of ', numPages
//         );
//     };
//
//     const createToolbarButtonGroup = () => {
//         const buttons = [createViewMenu()];
//
//         if (settings.enableLinkIcon)
//             buttons.push(createLinkIcon());
//
//         if (settings.enableNonPagedVisibilityIcon)
//             buttons.push(createToggleNonPagedButton());
//
//         if (settings.enableFullscreen)
//             buttons.push(createFullscreenButton());
//
//         return elt('span', elemAttrs('toolbar-button-group'), buttons);
//     };
//
//     const createLinkIcon = () => {
//         const elem = createButtonElement('link-icon', 'Link to this page');
//         const linkIcon = $(elem);
//
//         linkIcon.on('click', () => {
//             $('body').prepend(
//                 elt('div', {
//                     id: settings.ID + 'link-popup',
//                     class: 'diva-popup diva-link-popup'
//                 }, [
//                     elt('input', {
//                         id: settings.ID + 'link-popup-input',
//                         class: 'diva-input',
//                         type: 'text',
//                         value: viewer.getCurrentURL()
//                     })
//                 ])
//             );
//
//             if (settings.inFullscreen)
//             {
//                 $(settings.selector + 'link-popup').addClass('in-fullscreen');
//             }
//             else
//             {
//                 // Calculate the left and top offsets
//                 const leftOffset = linkIcon.offset().left - 222 + linkIcon.outerWidth();
//                 const topOffset = linkIcon.offset().top + linkIcon.outerHeight() - 1;
//
//                 $(settings.selector + 'link-popup').css({
//                     'top': topOffset + 'px',
//                     'left': leftOffset + 'px'
//                 });
//             }
//
//             // Catch onmouseup events outside of this div
//             $('body').mouseup(event => {
//                 const targetID = event.target.id;
//
//                 if (targetID !== settings.ID + 'link-popup' && targetID !== settings.ID + 'link-popup-input')
//                     $(settings.selector + 'link-popup').remove();
//             });
//
//             // Also delete it upon scroll and page up/down key events
//             // FIXME(wabain): This is aggressive
//             settings.viewportObject.scroll(() => {
//                 $(settings.selector + 'link-popup').remove();
//             });
//             $(settings.selector + 'link-popup input').click(function ()
//             {
//                 $(this).focus().select();
//             });
//
//             return false;
//         });
//
//         return elem;
//     };
//
//     var createFullscreenButton = () => createButtonElement('fullscreen-icon', 'Toggle fullscreen mode', () => {
//         viewer.toggleFullscreenMode();
//     });
//
//     var createToggleNonPagedButton = () => {
//         const getClassName = () => 'toggle-nonpaged-icon' + (viewer.getSettings().showNonPagedPages ? '-active' : '');
//
//         const toggleNonPagedButton = createButtonElement(getClassName(), 'Toggle visibility of non-paged pages', function()
//         {
//             viewer.toggleNonPagedPagesVisibility();
//             const newClassName = 'diva-' + getClassName();
//             this.className = this.className.replace(/diva-toggle-nonpaged-icon(-active)?/, newClassName);
//         });
//
//         const updateNonPagedButtonVisibility = () => {
//             const pages = settings.manifest.pages;
//             for (let i = 0; i < pages.length; i++)
//             {
//                 if (settings.manifest.paged && !pages[i].paged)
//                 {
//                     // Show the button, there is at least one non-paged page
//                     toggleNonPagedButton.style.display = 'inline-block';
//                     return;
//                 }
//             }
//
//             // No non-paged pages were found, hide the button
//             toggleNonPagedButton.style.display = 'none';
//         };
//         subscribe('ObjectDidLoad', updateNonPagedButtonVisibility);
//
//         return toggleNonPagedButton;
//     };
//
//     // Handles all status updating etc (both fullscreen and not)
//     const init = () => {
//         const leftTools = [createZoomControls(), createGridControls()];
//         const rightTools = [createPageNavigationControls(), createToolbarButtonGroup()];
//
//         const tools = elt('div', elemAttrs('tools'),
//             elt('div', elemAttrs('tools-left'), leftTools),
//             elt('div', elemAttrs('tools-right'), rightTools)
//         );
//
//         settings.toolbarParentObject.prepend(tools);
//
//         // Handle entry to and exit from fullscreen mode
//         const switchMode = () => {
//             const toolsRightElement = document.getElementById(settings.ID + 'tools-right');
//             const pageNavElement = document.getElementById(settings.ID + 'page-nav');
//
//             if (!settings.inFullscreen)
//             {
//                 // Leaving fullscreen
//                 $(tools).removeClass('diva-fullscreen-tools');
//
//                 //move ID-page-nav to beginning of tools right
//                 toolsRightElement.removeChild(pageNavElement);
//                 toolsRightElement.insertBefore(pageNavElement, toolsRightElement.firstChild);
//             }
//             else
//             {
//                 // Entering fullscreen
//                 $(tools).addClass('diva-fullscreen-tools');
//
//                 //move ID-page-nav to end of tools right
//                 toolsRightElement.removeChild(pageNavElement);
//                 toolsRightElement.appendChild(pageNavElement);
//             }
//         };
//
//         subscribe('ModeDidSwitch', switchMode);
//         subscribe('ViewerDidLoad', switchMode);
//
//         const toolbar = {
//             element: tools,
//             closePopups: function ()
//             {
//                 $('.diva-popup').css('display', 'none');
//             }
//         };
//
//         return toolbar;
//     };
//
//     return init();
// }


exports.default = Toolbar;

/***/ }),

/***/ "./source/js/utils/dragscroll.js":
/*!***************************************!*\
  !*** ./source/js/utils/dragscroll.js ***!
  \***************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
var __WEBPACK_AMD_DEFINE_FACTORY__, __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;

/**
 * @fileoverview dragscroll - scroll area by dragging
 * @version 0.0.8
 *
 * @license MIT, see http://github.com/asvd/dragscroll
 * @copyright 2015 asvd <heliosframework@gmail.com>
 */
(function (root, factory) {
    if (true) {
        !(__WEBPACK_AMD_DEFINE_ARRAY__ = [exports], __WEBPACK_AMD_DEFINE_FACTORY__ = (factory),
				__WEBPACK_AMD_DEFINE_RESULT__ = (typeof __WEBPACK_AMD_DEFINE_FACTORY__ === 'function' ?
				(__WEBPACK_AMD_DEFINE_FACTORY__.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__)) : __WEBPACK_AMD_DEFINE_FACTORY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
    } else {}
})(undefined, function (exports) {
    var _window = window;
    var _document = document;
    var mousemove = 'mousemove';
    var mouseup = 'mouseup';
    var mousedown = 'mousedown';
    var EventListener = 'EventListener';
    var addEventListener = 'add' + EventListener;
    var removeEventListener = 'remove' + EventListener;
    var newScrollX, newScrollY; // jshint ignore:line

    var dragged = [];

    var reset = function reset(i, el) {
        for (i = 0; i < dragged.length;) {
            el = dragged[i++];
            el = el.container || el;
            el[removeEventListener](mousedown, el.md, 0);
            _window[removeEventListener](mouseup, el.mu, 0);
            _window[removeEventListener](mousemove, el.mm, 0);
        }

        // suppress warning about functions in loops.
        /* jshint ignore:start */
        // cloning into array since HTMLCollection is updated dynamically
        dragged = [].slice.call(_document.getElementsByClassName('dragscroll'));
        for (i = 0; i < dragged.length;) {
            (function (el, lastClientX, lastClientY, pushed, scroller, cont) {
                (cont = el.container || el)[addEventListener](mousedown, cont.md = function (e) {
                    if (!el.hasAttribute('nochilddrag') || _document.elementFromPoint(e.pageX, e.pageY) === cont) {
                        pushed = 1;
                        lastClientX = e.clientX;
                        lastClientY = e.clientY;

                        e.preventDefault();
                    }
                }, 0);

                _window[addEventListener](mouseup, cont.mu = function () {
                    pushed = 0;
                }, 0);

                _window[addEventListener](mousemove, cont.mm = function (e) {
                    if (pushed) {
                        (scroller = el.scroller || el).scrollLeft -= newScrollX = -lastClientX + (lastClientX = e.clientX);
                        scroller.scrollTop -= newScrollY = -lastClientY + (lastClientY = e.clientY);
                        if (el === _document.body) {
                            (scroller = _document.documentElement).scrollLeft -= newScrollX;
                            scroller.scrollTop -= newScrollY;
                        }
                    }
                }, 0);
            })(dragged[i++]);
        }
        /* jshint ignore:end */
    };

    if (_document.readyState === 'complete') {
        reset();
    } else {
        _window[addEventListener]('load', reset, 0);
    }

    exports.reset = reset;
});

/***/ }),

/***/ "./source/js/utils/elt.js":
/*!********************************!*\
  !*** ./source/js/utils/elt.js ***!
  \********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

exports.elt = elt;
exports.setAttributes = setDOMAttributes;

/**
 * Convenience function to create a DOM element, set attributes on it, and
 * append children. All arguments which are not of primitive type, are not
 * arrays, and are not DOM nodes are treated as attribute hashes and are
 * handled as described for setDOMAttributes. Children can either be a DOM
 * node or a primitive value, which is converted to a text node. Arrays are
 * handled recursively. Null and undefined values are ignored.
 *
 * Inspired by the ProseMirror helper of the same name.
 */

function elt(tag) {
    var el = document.createElement(tag);
    var args = Array.prototype.slice.call(arguments, 1);

    while (args.length) {
        var arg = args.shift();
        handleEltConstructorArg(el, arg);
    }

    return el;
}

function handleEltConstructorArg(el, arg) {
    if (arg == null) // NB: == is correct;
        return;

    if ((typeof arg === 'undefined' ? 'undefined' : _typeof(arg)) !== 'object' && typeof arg !== 'function') {
        // Coerce to string
        el.appendChild(document.createTextNode(arg));
    } else if (arg instanceof window.Node) {
        el.appendChild(arg);
    } else if (arg instanceof Array) {
        var childCount = arg.length;
        for (var i = 0; i < childCount; i++) {
            handleEltConstructorArg(el, arg[i]);
        }
    } else {
        setDOMAttributes(el, arg);
    }
}

/**
 * Set attributes of a DOM element. The `style` property is special-cased to
 * accept either a string or an object whose own attributes are assigned to
 * el.style.
 */
function setDOMAttributes(el, attributes) {
    for (var prop in attributes) {
        if (!attributes.hasOwnProperty(prop)) continue;

        if (prop === 'style') {
            setStyle(el, attributes.style);
        } else {
            el.setAttribute(prop, attributes[prop]);
        }
    }
}

function setStyle(el, style) {
    if (!style) return;

    if ((typeof style === 'undefined' ? 'undefined' : _typeof(style)) !== 'object') {
        el.style.cssText = style;
        return;
    }

    for (var cssProp in style) {
        if (!style.hasOwnProperty(cssProp)) continue;

        el.style[cssProp] = style[cssProp];
    }
}

/***/ }),

/***/ "./source/js/utils/events.js":
/*!***********************************!*\
  !*** ./source/js/utils/events.js ***!
  \***********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

/**
 * Events. Pub/Sub system for Loosely Coupled logic.
 * Based on Peter Higgins' port from Dojo to jQuery
 * https://github.com/phiggins42/bloody-jquery-plugins/blob/master/pubsub.js
 *
 * Re-adapted to vanilla Javascript
 *
 * @class Events
 */

var DivaEvents = function () {
    function DivaEvents() {
        _classCallCheck(this, DivaEvents);

        this._cache = {};
    }

    /**
     * diva.Events.publish
     * e.g.: diva.Events.publish("PageDidLoad", [pageIndex, filename, pageSelector], this);
     *
     * @class Events
     * @method publish
     * @param topic {String}
     * @param args  {Array}
     * @param scope {Object=} Optional - Subscribed functions will be executed with the supplied object as `this`.
     *     It is necessary to supply this argument with the self variable when within a Diva instance.
     *     The scope argument is matched with the instance ID of subscribers to determine whether they
     *         should be executed. (See instanceID argument of subscribe.)
     */


    _createClass(DivaEvents, [{
        key: 'publish',
        value: function publish(topic, args, scope) {
            if (this._cache[topic]) {
                var thisTopic = this._cache[topic];

                if (typeof thisTopic.global !== 'undefined') {
                    var thisTopicGlobal = thisTopic.global;
                    var globalCount = thisTopicGlobal.length;

                    for (var i = 0; i < globalCount; i++) {
                        thisTopicGlobal[i].apply(scope || null, args || []);
                    }
                }

                if (scope && typeof scope.getInstanceId !== 'undefined') {
                    // get publisher instance ID from scope arg, compare, and execute if match
                    var instanceID = scope.getInstanceId();

                    if (this._cache[topic][instanceID]) {
                        var thisTopicInstance = this._cache[topic][instanceID];
                        var scopedCount = thisTopicInstance.length;

                        for (var j = 0; j < scopedCount; j++) {
                            thisTopicInstance[j].apply(scope, args || []);
                        }
                    }
                }
            }
        }

        /**
         * diva.Events.subscribe
         * e.g.: diva.Events.subscribe("PageDidLoad", highlight, settings.ID)
         *
         * @class Events
         * @method subscribe
         * @param {string} topic
         * @param {function} callback
         * @param {string=} instanceID  Optional - String representing the ID of a Diva instance; if provided,
         *                                       callback only fires for events published from that instance.
         * @return Event handler {Array}
         */

    }, {
        key: 'subscribe',
        value: function subscribe(topic, callback, instanceID) {
            if (!this._cache[topic]) {
                this._cache[topic] = {};
            }

            if (typeof instanceID === 'string') {
                if (!this._cache[topic][instanceID]) {
                    this._cache[topic][instanceID] = [];
                }

                this._cache[topic][instanceID].push(callback);
            } else {
                if (!this._cache[topic].global) {
                    this._cache[topic].global = [];
                }

                this._cache[topic].global.push(callback);
            }

            return instanceID ? [topic, callback, instanceID] : [topic, callback];
        }

        /**
         * diva.Events.unsubscribe
         * e.g.: var handle = Events.subscribe("PageDidLoad", highlight);
         *         Events.unsubscribe(handle);
         *
         * @class Events
         * @method unsubscribe
         * @param {array} handle
         * @param {boolean=} completely - Unsubscribe all events for a given topic.
         * @return {boolean} success
         */

    }, {
        key: 'unsubscribe',
        value: function unsubscribe(handle, completely) {
            var t = handle[0];

            if (this._cache[t]) {
                var topicArray = void 0;
                var instanceID = handle.length === 3 ? handle[2] : 'global';

                topicArray = this._cache[t][instanceID];

                if (!topicArray) {
                    return false;
                }

                if (completely) {
                    delete this._cache[t][instanceID];
                    return topicArray.length > 0;
                }

                var i = topicArray.length;

                while (i--) {
                    if (topicArray[i] === handle[1]) {
                        this._cache[t][instanceID].splice(i, 1);
                        return true;
                    }
                }
            }

            return false;
        }

        /**
         * diva.Events.unsubscribeAll
         * e.g.: diva.Events.unsubscribeAll('global');
         *
         * @class Events
         * @param {string=} instanceID Optional - instance ID to remove subscribers from or 'global' (if omitted,
         *                              subscribers in all scopes removed)
         * @method unsubscribeAll
         */

    }, {
        key: 'unsubscribeAll',
        value: function unsubscribeAll(instanceID) {
            if (instanceID) {
                var topics = Object.keys(this._cache);
                var i = topics.length;
                var topic = void 0;

                while (i--) {
                    topic = topics[i];

                    if (typeof this._cache[topic][instanceID] !== 'undefined') {
                        delete this._cache[topic][instanceID];
                    }
                }
            } else {
                this._cache = {};
            }
        }
    }]);

    return DivaEvents;
}();

var Events = exports.Events = new DivaEvents();

/***/ }),

/***/ "./source/js/utils/get-scrollbar-width.js":
/*!************************************************!*\
  !*** ./source/js/utils/get-scrollbar-width.js ***!
  \************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = getScrollbarWidth;
// From http://www.alexandre-gomes.com/?p=115, modified slightly
function getScrollbarWidth() {
    var inner = document.createElement('p');
    inner.style.width = '100%';
    inner.style.height = '200px';

    var outer = document.createElement('div');
    outer.style.position = 'absolute';
    outer.style.top = '0px';
    outer.style.left = '0px';
    outer.style.visibility = 'hidden';
    outer.style.width = '200px';
    outer.style.height = '150px';
    outer.style.overflow = 'hidden';
    outer.appendChild(inner);

    document.body.appendChild(outer);

    var w1 = inner.offsetWidth;
    outer.style.overflow = 'scroll';
    var w2 = inner.offsetWidth;
    if (w1 === w2) {
        w2 = outer.clientWidth; // for IE i think
    }

    document.body.removeChild(outer);
    return w1 - w2;
}

/***/ }),

/***/ "./source/js/utils/hash-params.js":
/*!****************************************!*\
  !*** ./source/js/utils/hash-params.js ***!
  \****************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = {
    get: getHashParam,
    update: updateHashParam
};

// For getting the #key values from the URL. For specifying a page and zoom level
// Look into caching, because we only need to get this during the initial load
// Although for the tests I guess we would need to override caching somehow

function getHashParam(key) {
    var hash = window.location.hash;

    if (hash !== '') {
        // Check if there is something that looks like either &key= or #key=
        var startIndex = hash.indexOf('&' + key + '=') > 0 ? hash.indexOf('&' + key + '=') : hash.indexOf('#' + key + '=');

        // If startIndex is still -1, it means it can't find either
        if (startIndex >= 0) {
            // Add the length of the key plus the & and =
            startIndex += key.length + 2;

            // Either to the next ampersand or to the end of the string
            var endIndex = hash.indexOf('&', startIndex);
            if (endIndex > startIndex) {
                return decodeURIComponent(hash.substring(startIndex, endIndex));
            } else if (endIndex < 0) {
                // This means this hash param is the last one
                return decodeURIComponent(hash.substring(startIndex));
            }
            // If the key doesn't have a value I think
            return '';
        } else {
            // If it can't find the key
            return false;
        }
    } else {
        // If there are no hash params just return false
        return false;
    }
}

function updateHashParam(key, value) {
    // First make sure that we have to do any work at all
    var originalValue = getHashParam(key);
    var hash = window.location.hash;

    if (originalValue !== value) {
        // Is the key already in the URL?
        if (typeof originalValue === 'string') {
            // Already in the URL. Just get rid of the original value
            var startIndex = hash.indexOf('&' + key + '=') > 0 ? hash.indexOf('&' + key + '=') : hash.indexOf('#' + key + '=');
            var endIndex = startIndex + key.length + 2 + originalValue.length;
            // # if it's the first, & otherwise
            var startThing = startIndex === 0 ? '#' : '&';
            window.location.replace(hash.substring(0, startIndex) + startThing + key + '=' + value + hash.substring(endIndex));
        } else {
            // It's not present - add it
            if (hash.length === 0) {
                window.location.replace('#' + key + '=' + value);
            } else {
                // Append it
                window.location.replace(hash + '&' + key + '=' + value);
            }
        }
    }
}

/***/ }),

/***/ "./source/js/utils/vanilla.kinetic.js":
/*!********************************************!*\
  !*** ./source/js/utils/vanilla.kinetic.js ***!
  \********************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


/*
 The MIT License (MIT)
 Copyright (c) <2011> <Dave Taylor http://the-taylors.org>

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is furnished
 to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

 Port to vanilla Javascript by Jacek Nowacki http://jacek-nowacki.net/
**/

(function () {
    var _raf = window.requestAnimationFrame;

    var _isTouch = 'ontouchend' in document;

    // this is simple, no "deep" support
    var _extend = function _extend() {
        for (var i = 1; i < arguments.length; i++) {
            for (var key in arguments[i]) {
                if (arguments[i].hasOwnProperty(key)) {
                    arguments[0][key] = arguments[i][key];
                }
            }
        }
        return arguments[0];
    };

    var VanillaKinetic = function VanillaKinetic(element, settings) {
        this.settings = _extend({}, VanillaKinetic.DEFAULTS, settings);
        this.el = element;
        this.ACTIVE_CLASS = "kinetic-active";

        this._initElements();

        this.el._VanillaKinetic = this;
        return this;
    };

    VanillaKinetic.DEFAULTS = {
        cursor: 'move',
        decelerate: true,
        triggerHardware: false,
        threshold: 0,
        y: true,
        x: true,
        slowdown: 0.9,
        maxvelocity: 40,
        throttleFPS: 60,
        invert: false,
        movingClass: {
            up: 'kinetic-moving-up',
            down: 'kinetic-moving-down',
            left: 'kinetic-moving-left',
            right: 'kinetic-moving-right'
        },
        deceleratingClass: {
            up: 'kinetic-decelerating-up',
            down: 'kinetic-decelerating-down',
            left: 'kinetic-decelerating-left',
            right: 'kinetic-decelerating-right'
        }
    };

    // Public functions
    VanillaKinetic.prototype.start = function (options) {
        this.settings = _extend(this.settings, options);
        this.velocity = options.velocity || this.velocity;
        this.velocityY = options.velocityY || this.velocityY;
        this.settings.decelerate = false;
        this._move();
    };

    VanillaKinetic.prototype.end = function () {
        this.settings.decelerate = true;
    };

    VanillaKinetic.prototype.stop = function () {
        this.velocity = 0;
        this.velocityY = 0;
        this.settings.decelerate = true;
        if (typeof this.settings.stopped === 'function') {
            this.settings.stopped.call(this);
        }
    };

    VanillaKinetic.prototype.detach = function () {
        this._detachListeners();
        this.el.classList.remove(this.ACTIVE_CLASS);
        this.el.style.cursor = '';
    };

    VanillaKinetic.prototype.attach = function () {
        if (this.el.classList.contains(this.ACTIVE_CLASS)) {
            return;
        }
        this._attachListeners();
        this.el.classList.add(this.ACTIVE_CLASS);
        this.el.style.cursor = this.settings.cursor;
    };

    // Internal functions

    VanillaKinetic.prototype._initElements = function () {
        this.el.classList.add(this.ACTIVE_CLASS);

        _extend(this, {
            xpos: null,
            prevXPos: false,
            ypos: null,
            prevYPos: false,
            mouseDown: false,
            throttleTimeout: 1000 / this.settings.throttleFPS,
            lastMove: null,
            elementFocused: null
        });

        this.velocity = 0;
        this.velocityY = 0;

        var that = this;
        this.documentResetHandler = function () {
            that._resetMouse.apply(that);
        };

        // FIXME make sure to remove this
        var html = document.documentElement;
        html.addEventListener("mouseup", this.documentResetHandler, false);
        html.addEventListener("click", this.documentResetHandler, false);

        this._initEvents();

        this.el.style.cursor = this.settings.cursor;

        if (this.settings.triggerHardware) {
            var prefixes = ['', '-ms-', '-webkit-', '-moz-'];
            var styles = {
                'transform': 'translate3d(0,0,0)',
                'perspective': '1000', // TODO is this even valid? is this even needed?
                'backface-visibility': 'hidden'
            };
            for (var i = 0; i < prefixes.length; i++) {
                var prefix = prefixes[i];
                for (var key in styles) {
                    if (styles.hasOwnProperty(key)) {
                        this.el.style[prefix + key] = styles[key];
                    }
                }
            }
        }
    };

    VanillaKinetic.prototype._initEvents = function () {
        var self = this;
        this.settings.events = {
            touchStart: function touchStart(e) {
                var touch;
                if (self._useTarget(e.target, e)) {
                    touch = e.originalEvent.touches[0];
                    self.threshold = self._threshold(e.target, e);
                    self._start(touch.clientX, touch.clientY);
                    e.stopPropagation();
                }
            },
            touchMove: function touchMove(e) {
                var touch;
                if (self.mouseDown) {
                    touch = e.originalEvent.touches[0];
                    self._inputmove(touch.clientX, touch.clientY);
                    if (e.preventDefault) {
                        e.preventDefault();
                    }
                }
            },
            inputDown: function inputDown(e) {
                if (self._useTarget(e.target, e)) {
                    self.threshold = self._threshold(e.target, e);
                    self._start(e.clientX, e.clientY);
                    self.elementFocused = e.target;
                    if (e.target.nodeName === "IMG") {
                        e.preventDefault();
                    }
                    e.stopPropagation();
                }
            },
            inputEnd: function inputEnd(e) {
                if (self._useTarget(e.target, e)) {
                    self._end();
                    self.elementFocused = null;
                    if (e.preventDefault) {
                        e.preventDefault();
                    }
                }
            },
            inputMove: function inputMove(e) {
                if (self.mouseDown) {
                    self._inputmove(e.clientX, e.clientY);
                    if (e.preventDefault) {
                        e.preventDefault();
                    }
                }
            },
            scroll: function scroll(e) {
                if (typeof self.settings.moved === 'function') {
                    self.settings.moved.call(self, self.settings);
                }
                if (e.preventDefault) {
                    e.preventDefault();
                }
            },
            inputClick: function inputClick(e) {
                if (Math.abs(self.velocity) > 0 || Math.abs(self.velocityY) > 0) {
                    e.preventDefault();
                    if (e.stopPropagation) {
                        e.stopPropagation();
                    }
                    return false;
                }
            },
            dragStart: function dragStart(e) {
                if (self._useTarget(e.target, e) && self.elementFocused) {
                    if (e.preventDefault) {
                        e.preventDefault();
                    }
                    if (e.stopPropagation) {
                        e.stopPropagation();
                    }
                    return false;
                }
            },
            selectStart: function selectStart(e) {
                if (typeof self.settings.selectStart === 'function') {
                    return self.settings.selectStart.apply(self, arguments);
                } else if (self._useTarget(e.target, e)) {
                    if (e.preventDefault) {
                        e.preventDefault();
                    }
                    if (e.stopPropagation) {
                        e.stopPropagation();
                    }
                    return false;
                }
            }
        };

        this._attachListeners();
    };

    VanillaKinetic.prototype._inputmove = function (clientX, clientY) {
        if (!this.lastMove || new Date() > new Date(this.lastMove.getTime() + this.throttleTimeout)) {
            this.lastMove = new Date();

            if (this.mouseDown && (this.xpos || this.ypos)) {
                var movedX = clientX - this.xpos;
                var movedY = clientY - this.ypos;
                if (this.settings.invert) {
                    movedX *= -1;
                    movedY *= -1;
                }
                if (this.threshold > 0) {
                    var moved = Math.sqrt(movedX * movedX + movedY * movedY);
                    if (this.threshold > moved) {
                        return;
                    } else {
                        this.threshold = 0;
                    }
                }
                if (this.elementFocused) {
                    this.elementFocused.blur();
                    this.elementFocused = null;
                    this.el.focus();
                }

                this.settings.decelerate = false;
                this.velocity = this.velocityY = 0;

                var scrollLeft = this.scrollLeft();
                var scrollTop = this.scrollTop();

                this.scrollLeft(this.settings.x ? scrollLeft - movedX : scrollLeft);
                this.scrollTop(this.settings.y ? scrollTop - movedY : scrollTop);

                this.prevXPos = this.xpos;
                this.prevYPos = this.ypos;
                this.xpos = clientX;
                this.ypos = clientY;

                this._calculateVelocities();
                this._setMoveClasses(this.settings.movingClass);

                if (typeof this.settings.moved === 'function') {
                    this.settings.moved.call(this, this.settings);
                }
            }
        }
    };

    VanillaKinetic.prototype._calculateVelocities = function () {
        this.velocity = this._capVelocity(this.prevXPos - this.xpos, this.settings.maxvelocity);
        this.velocityY = this._capVelocity(this.prevYPos - this.ypos, this.settings.maxvelocity);
        if (this.settings.invert) {
            this.velocity *= -1;
            this.velocityY *= -1;
        }
    };

    VanillaKinetic.prototype._end = function () {
        if (this.xpos && this.prevXPos && this.settings.decelerate === false) {
            this.settings.decelerate = true;
            this._calculateVelocities();
            this.xpos = this.prevXPos = this.mouseDown = false;
            this._move();
        }
    };

    VanillaKinetic.prototype._useTarget = function (target, event) {
        if (typeof this.settings.filterTarget === 'function') {
            return this.settings.filterTarget.call(this, target, event) !== false;
        }
        return true;
    };

    VanillaKinetic.prototype._threshold = function (target, event) {
        if (typeof this.settings.threshold === 'function') {
            return this.settings.threshold.call(this, target, event);
        }
        return this.settings.threshold;
    };

    VanillaKinetic.prototype._start = function (clientX, clientY) {
        this.mouseDown = true;
        this.velocity = this.prevXPos = 0;
        this.velocityY = this.prevYPos = 0;
        this.xpos = clientX;
        this.ypos = clientY;
    };

    VanillaKinetic.prototype._resetMouse = function () {
        this.xpos = false;
        this.ypos = false;
        this.mouseDown = false;
    };

    VanillaKinetic.prototype._decelerateVelocity = function (velocity, slowdown) {
        return Math.floor(Math.abs(velocity)) === 0 ? 0 // is velocity less than 1?
        : velocity * slowdown; // reduce slowdown
    };

    VanillaKinetic.prototype._capVelocity = function (velocity, max) {
        var newVelocity = velocity;
        if (velocity > 0) {
            if (velocity > max) {
                newVelocity = max;
            }
        } else {
            if (velocity < 0 - max) {
                newVelocity = 0 - max;
            }
        }
        return newVelocity;
    };

    VanillaKinetic.prototype._setMoveClasses = function (classes) {
        // The fix-me comment below is from original jQuery.kinetic project
        // FIXME: consider if we want to apply PL #44, this should not remove
        // classes we have not defined on the element!
        var settings = this.settings;
        var el = this.el;

        el.classList.remove(settings.movingClass.up);
        el.classList.remove(settings.movingClass.down);
        el.classList.remove(settings.movingClass.left);
        el.classList.remove(settings.movingClass.right);
        el.classList.remove(settings.deceleratingClass.up);
        el.classList.remove(settings.deceleratingClass.down);
        el.classList.remove(settings.deceleratingClass.left);
        el.classList.remove(settings.deceleratingClass.right);

        if (this.velocity > 0) {
            el.classList.add(classes.right);
        }
        if (this.velocity < 0) {
            el.classList.add(classes.left);
        }
        if (this.velocityY > 0) {
            el.classList.add(classes.down);
        }
        if (this.velocityY < 0) {
            el.classList.add(classes.up);
        }
    };

    VanillaKinetic.prototype._move = function () {
        var scroller = this._getScroller();
        var self = this;
        var settings = this.settings;

        if (settings.x && scroller.scrollWidth > 0) {
            this.scrollLeft(this.scrollLeft() + this.velocity);
            if (Math.abs(this.velocity) > 0) {
                this.velocity = settings.decelerate ? self._decelerateVelocity(this.velocity, settings.slowdown) : this.velocity;
            }
        } else {
            this.velocity = 0;
        }

        if (settings.y && scroller.scrollHeight > 0) {
            this.scrollTop(this.scrollTop() + this.velocityY);
            if (Math.abs(this.velocityY) > 0) {
                this.velocityY = settings.decelerate ? self._decelerateVelocity(this.velocityY, settings.slowdown) : this.velocityY;
            }
        } else {
            this.velocityY = 0;
        }

        self._setMoveClasses(settings.deceleratingClass);

        if (typeof settings.moved === 'function') {
            settings.moved.call(this, settings);
        }

        if (Math.abs(this.velocity) > 0 || Math.abs(this.velocityY) > 0) {
            if (!this.moving) {
                this.moving = true;
                // tick for next movement
                _raf(function () {
                    self.moving = false;
                    self._move();
                });
            }
        } else {
            self.stop();
        }
    };

    VanillaKinetic.prototype._getScroller = function () {
        // FIXME we may want to normalize behaviour across browsers as in original jQuery.kinetic
        // currently this won't work correctly on all brwosers when attached to html or body element
        return this.el;
    };

    VanillaKinetic.prototype.scrollLeft = function (left) {
        var scroller = this._getScroller();
        if (typeof left === 'number') {
            scroller.scrollLeft = left;
            this.settings.scrollLeft = left;
        } else {
            return scroller.scrollLeft;
        }
    };

    VanillaKinetic.prototype.scrollTop = function (top) {
        var scroller = this._getScroller();
        if (typeof top === 'number') {
            scroller.scrollTop = top;
            this.settings.scrollTop = top;
        } else {
            return scroller.scrollTop;
        }
    };

    VanillaKinetic.prototype._attachListeners = function () {
        var el = this.el;
        var settings = this.settings;

        if (_isTouch) {
            el.addEventListener('touchstart', settings.events.touchStart, false);
            el.addEventListener('touchend', settings.events.inputEnd, false);
            el.addEventListener('touchmove', settings.events.touchMove, false);
        }

        el.addEventListener('mousedown', settings.events.inputDown, false);
        el.addEventListener('mouseup', settings.events.inputEnd, false);
        el.addEventListener('mousemove', settings.events.inputMove, false);

        el.addEventListener('click', settings.events.inputClick, false);
        el.addEventListener('scroll', settings.events.scroll, false);
        el.addEventListener('selectstart', settings.events.selectStart, false);
        el.addEventListener('dragstart', settings.events.dragStart, false);
    };

    VanillaKinetic.prototype._detachListeners = function () {
        var el = this.el;
        var settings = this.settings;

        if (_isTouch) {
            el.removeEventListener('touchstart', settings.events.touchStart, false);
            el.removeEventListener('touchend', settings.events.inputEnd, false);
            el.removeEventListener('touchmove', settings.events.touchMove, false);
        }

        el.removeEventListener('mousedown', settings.events.inputDown, false);
        el.removeEventListener('mouseup', settings.events.inputEnd, false);
        el.removeEventListener('mousemove', settings.events.inputMove, false);

        el.removeEventListener('click', settings.events.inputClick, false);
        el.removeEventListener('scroll', settings.events.scroll, false);
        el.removeEventListener('selectstart', settings.events.selectStart, false);
        el.removeEventListener('dragstart', settings.events.dragStart, false);
    };

    window.VanillaKinetic = VanillaKinetic;
})();

/***/ }),

/***/ "./source/js/validation-runner.js":
/*!****************************************!*\
  !*** ./source/js/validation-runner.js ***!
  \****************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var ValidationRunner = function () {
    function ValidationRunner(options) {
        _classCallCheck(this, ValidationRunner);

        this.whitelistedKeys = options.whitelistedKeys || [];
        this.additionalProperties = options.additionalProperties || [];
        this.validations = options.validations;
    }

    _createClass(ValidationRunner, [{
        key: 'isValid',
        value: function isValid(key, value, settings) {
            // Get the validation index
            var validationIndex = null;

            this.validations.some(function (validation, index) {
                if (validation.key !== key) {
                    return false;
                }

                validationIndex = index;
                return true;
            });

            if (validationIndex === null) {
                return true;
            }

            // Run the validation
            var dummyChanges = {};
            dummyChanges[key] = value;
            var proxier = createSettingsProxier(settings, dummyChanges, this);

            return !this._runValidation(validationIndex, value, proxier);
        }
    }, {
        key: 'validate',
        value: function validate(settings) {
            this._validateOptions({}, settings);
        }
    }, {
        key: 'getValidatedOptions',
        value: function getValidatedOptions(settings, options) {
            var cloned = Object.assign({}, options);
            this._validateOptions(settings, cloned);
            return cloned;
        }
    }, {
        key: '_validateOptions',
        value: function _validateOptions(settings, options) {
            var settingsProxier = createSettingsProxier(settings, options, this);
            this._applyValidations(options, settingsProxier);
        }
    }, {
        key: '_applyValidations',
        value: function _applyValidations(options, proxier) {
            var _this = this;

            this.validations.forEach(function (validation, index) {
                if (!options.hasOwnProperty(validation.key)) {
                    return;
                }

                var input = options[validation.key];
                var corrected = _this._runValidation(index, input, proxier);

                if (corrected) {
                    if (!corrected.warningSuppressed) {
                        emitWarning(validation.key, input, corrected.value);
                    }

                    options[validation.key] = corrected.value;
                }
            }, this);
        }
    }, {
        key: '_runValidation',
        value: function _runValidation(index, input, proxier) {
            var validation = this.validations[index];

            proxier.index = index;

            var warningSuppressed = false;
            var config = {
                suppressWarning: function suppressWarning() {
                    warningSuppressed = true;
                }
            };

            var outputValue = validation.validate(input, proxier.proxy, config);

            if (outputValue === undefined || outputValue === input) {
                return null;
            }

            return {
                value: outputValue,
                warningSuppressed: warningSuppressed
            };
        }
    }]);

    return ValidationRunner;
}();

/**
 * The settings proxy wraps the settings object and ensures that
 * only values which have previously been validated are accessed,
 * throwing a TypeError otherwise.
 *
 * FIXME(wabain): Is it worth keeping this? When I wrote it I had
 * multiple validation stages and it was a lot harder to keep track
 * of everything, so this was more valuable.
 */


exports.default = ValidationRunner;
function createSettingsProxier(settings, options, runner) {
    var proxier = {
        proxy: {},
        index: null
    };

    var lookup = lookupValue.bind(null, settings, options);

    var properties = {};

    runner.whitelistedKeys.forEach(function (whitelisted) {
        properties[whitelisted] = {
            get: lookup.bind(null, whitelisted)
        };
    });

    runner.additionalProperties.forEach(function (additional) {
        properties[additional.key] = {
            get: additional.get
        };
    });

    runner.validations.forEach(function (validation, validationIndex) {
        properties[validation.key] = {
            get: function get() {
                if (validationIndex < proxier.index) {
                    return lookup(validation.key);
                }

                var currentKey = runner.validations[proxier.index].key;
                throw new TypeError('Cannot access setting ' + validation.key + ' while validating ' + currentKey);
            }
        };
    });

    Object.defineProperties(proxier.proxy, properties);

    return proxier;
}

function emitWarning(key, original, corrected) {
    console.warn('Invalid value for ' + key + ': ' + original + '. Using ' + corrected + ' instead.');
}

function lookupValue(base, extension, key) {
    if (key in extension) {
        return extension[key];
    }

    return base[key];
}

/***/ }),

/***/ "./source/js/viewer-core.js":
/*!**********************************!*\
  !*** ./source/js/viewer-core.js ***!
  \**********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _elt = __webpack_require__(/*! ./utils/elt */ "./source/js/utils/elt.js");

var _getScrollbarWidth = __webpack_require__(/*! ./utils/get-scrollbar-width */ "./source/js/utils/get-scrollbar-width.js");

var _getScrollbarWidth2 = _interopRequireDefault(_getScrollbarWidth);

var _gestureEvents = __webpack_require__(/*! ./gesture-events */ "./source/js/gesture-events.js");

var _gestureEvents2 = _interopRequireDefault(_gestureEvents);

var _divaGlobal = __webpack_require__(/*! ./diva-global */ "./source/js/diva-global.js");

var _divaGlobal2 = _interopRequireDefault(_divaGlobal);

var _documentHandler = __webpack_require__(/*! ./document-handler */ "./source/js/document-handler.js");

var _documentHandler2 = _interopRequireDefault(_documentHandler);

var _gridHandler = __webpack_require__(/*! ./grid-handler */ "./source/js/grid-handler.js");

var _gridHandler2 = _interopRequireDefault(_gridHandler);

var _pageOverlayManager = __webpack_require__(/*! ./page-overlay-manager */ "./source/js/page-overlay-manager.js");

var _pageOverlayManager2 = _interopRequireDefault(_pageOverlayManager);

var _renderer = __webpack_require__(/*! ./renderer */ "./source/js/renderer.js");

var _renderer2 = _interopRequireDefault(_renderer);

var _pageLayouts = __webpack_require__(/*! ./page-layouts */ "./source/js/page-layouts/index.js");

var _pageLayouts2 = _interopRequireDefault(_pageLayouts);

var _settingsView = __webpack_require__(/*! ./settings-view */ "./source/js/settings-view.js");

var _settingsView2 = _interopRequireDefault(_settingsView);

var _validationRunner = __webpack_require__(/*! ./validation-runner */ "./source/js/validation-runner.js");

var _validationRunner2 = _interopRequireDefault(_validationRunner);

var _viewport = __webpack_require__(/*! ./viewport */ "./source/js/viewport.js");

var _viewport2 = _interopRequireDefault(_viewport);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var debug = __webpack_require__(/*! debug */ "./node_modules/debug/src/browser.js")('diva:ViewerCore');

function generateId() {
    return generateId.counter++;
}
generateId.counter = 1;

// Define validations
var optionsValidations = [{
    key: 'goDirectlyTo',
    validate: function validate(value, settings) {
        if (value < 0 || value >= settings.manifest.pages.length) return 0;
    }
}, {
    key: 'minPagesPerRow',
    validate: function validate(value) {
        return Math.max(2, value);
    }
}, {
    key: 'maxPagesPerRow',
    validate: function validate(value, settings) {
        return Math.max(value, settings.minPagesPerRow);
    }
}, {
    key: 'pagesPerRow',
    validate: function validate(value, settings) {
        // Default to the maximum
        if (value < settings.minPagesPerRow || value > settings.maxPagesPerRow) return settings.maxPagesPerRow;
    }
}, {
    key: 'maxZoomLevel',
    validate: function validate(value, settings, config) {
        // Changing this value isn't really an error, it just depends on the
        // source manifest
        config.suppressWarning();

        if (value < 0 || value > settings.manifest.maxZoom) return settings.manifest.maxZoom;
    }
}, {
    key: 'minZoomLevel',
    validate: function validate(value, settings, config) {
        // Changes based on the manifest value shouldn't trigger a
        // warning
        if (value > settings.manifest.maxZoom) {
            config.suppressWarning();
            return 0;
        }

        if (value < 0 || value > settings.maxZoomLevel) return 0;
    }
}, {
    key: 'zoomLevel',
    validate: function validate(value, settings, config) {
        if (value > settings.manifest.maxZoom) {
            config.suppressWarning();
            return 0;
        }

        if (value < settings.minZoomLevel || value > settings.maxZoomLevel) return settings.minZoomLevel;
    }
}];

var ViewerCore = function () {
    function ViewerCore(element, options, publicInstance) {
        var _this = this;

        _classCallCheck(this, ViewerCore);

        this.parentObject = element;
        this.publicInstance = publicInstance;

        // Things that cannot be changed because of the way they are used by the script
        // Many of these are declared with arbitrary values that are changed later on
        this.viewerState = {
            currentPageIndex: 0, // The current page in the viewport (center-most page)
            horizontalOffset: 0, // Distance from the center of the diva element to the top of the current page
            horizontalPadding: 0, // Either the fixed padding or adaptive padding
            ID: null, // The prefix of the IDs of the elements (usually 1-diva-)
            initialKeyScroll: false, // Holds the initial state of enableKeyScroll
            initialSpaceScroll: false, // Holds the initial state of enableSpaceScroll
            innerElement: null, // The native .diva-outer DOM object
            innerObject: {}, // $(settings.ID + 'inner'), for selecting the .diva-inner element
            isActiveDiva: true, // In the case that multiple diva panes exist on the same page, this should have events funneled to it.
            isScrollable: true, // Used in enable/disableScrollable public methods
            isZooming: false, // Flag to keep track of whether zooming is still in progress, for handleZoom
            loaded: false, // A flag for when everything is loaded and ready to go.
            manifest: null,
            mobileWebkit: false, // Checks if the user is on a touch device (iPad/iPod/iPhone/Android)
            numPages: 0, // Number of pages in the array
            oldZoomLevel: -1, // Holds the previous zoom level after zooming in or out
            options: options,
            outerElement: null, // The native .diva-outer DOM object
            outerObject: {}, // $(settings.ID + 'outer'), for selecting the .diva-outer element
            pageOverlays: new _pageOverlayManager2.default(),
            pageTools: [], // The plugins which are enabled as page tools
            parentObject: this.parentObject, // JQuery object referencing the parent element
            pendingManifestRequest: null, // Reference to the xhr request retrieving the manifest. Used to cancel the request on destroy()
            pluginInstances: [], // Filled with the enabled plugins from the registry
            renderer: null,
            resizeTimer: -1, // Holds the ID of the timeout used when resizing the window (for clearing)
            scrollbarWidth: 0, // Set to the actual scrollbar width in init()
            selector: '', // Uses the generated ID prefix to easily select elements
            throbberTimeoutID: -1, // Holds the ID of the throbber loading timeout
            toolbar: null, // Holds an object with some toolbar-related functions
            verticalOffset: 0, // Distance from the center of the diva element to the left side of the current page
            verticalPadding: 0, // Either the fixed padding or adaptive padding
            viewHandler: null,
            viewport: null, // Object caching the viewport dimensions
            viewportElement: null,
            viewportObject: null,
            zoomDuration: 600
        };

        this.settings = (0, _settingsView2.default)([options, this.viewerState]);

        // Generate an ID that can be used as a prefix for all the other IDs
        var idNumber = generateId();
        this.viewerState.ID = 'diva-' + idNumber + '-';
        this.viewerState.selector = this.settings.ID;

        // Aliases for compatibility
        Object.defineProperties(this.settings, {
            // Height of the document viewer pane
            panelHeight: {
                get: function get() {
                    return _this.viewerState.viewport.height;
                }
            },
            // Width of the document viewer pane
            panelWidth: {
                get: function get() {
                    return _this.viewerState.viewport.width;
                }
            }
        });

        this.optionsValidator = new _validationRunner2.default({
            additionalProperties: [{
                key: 'manifest',
                get: function get() {
                    return _this.viewerState.manifest;
                }
            }],

            validations: optionsValidations
        });

        this.viewerState.scrollbarWidth = (0, _getScrollbarWidth2.default)();

        // If window.orientation is defined, then it's probably mobileWebkit
        this.viewerState.mobileWebkit = window.orientation !== undefined;

        if (options.hashParamSuffix === null) {
            // Omit the suffix from the first instance
            if (idNumber === 1) options.hashParamSuffix = '';else options.hashParamSuffix = idNumber + '';
        }

        // Create the inner and outer panels
        var innerElem = (0, _elt.elt)('div', this.elemAttrs('inner', { class: 'diva-inner' }));
        var viewportElem = (0, _elt.elt)('div', this.elemAttrs('viewport'), innerElem);
        var outerElem = (0, _elt.elt)('div', this.elemAttrs('outer'), viewportElem, (0, _elt.elt)('div', this.elemAttrs('throbber'), [(0, _elt.elt)('div', { class: 'cube cube1' }), (0, _elt.elt)('div', { class: 'cube cube2' }), (0, _elt.elt)('div', { class: 'cube cube3' }), (0, _elt.elt)('div', { class: 'cube cube4' }), (0, _elt.elt)('div', { class: 'cube cube5' }), (0, _elt.elt)('div', { class: 'cube cube6' }), (0, _elt.elt)('div', { class: 'cube cube7' }), (0, _elt.elt)('div', { class: 'cube cube8' }), (0, _elt.elt)('div', { class: 'cube cube9' })]));

        this.viewerState.innerElement = innerElem;
        this.viewerState.viewportElement = viewportElem;
        this.viewerState.outerElement = outerElem;

        this.viewerState.innerObject = innerElem;
        this.viewerState.viewportObject = viewportElem;
        this.viewerState.outerObject = outerElem;

        this.settings.parentObject.append(outerElem);

        this.viewerState.viewport = new _viewport2.default(this.viewerState.viewportElement, {
            intersectionTolerance: this.settings.viewportMargin
        });

        this.boundScrollFunction = this.scrollFunction.bind(this);
        this.boundEscapeListener = this.escapeListener.bind(this);

        // Do all the plugin initialisation
        this.initPlugins();
        this.handleEvents();

        // Show the throbber while waiting for the manifest to load
        this.showThrobber();
    }

    _createClass(ViewerCore, [{
        key: 'isValidOption',
        value: function isValidOption(key, value) {
            return this.optionsValidator.isValid(key, value, this.viewerState.options);
        }
    }, {
        key: 'elemAttrs',
        value: function elemAttrs(ident, base) {
            var attrs = {
                id: this.settings.ID + ident,
                class: 'diva-' + ident
            };

            if (base) return Object.assign(attrs, base);else return attrs;
        }
    }, {
        key: 'getPageData',
        value: function getPageData(pageIndex, attribute) {
            return this.settings.manifest.pages[pageIndex].d[this.settings.zoomLevel][attribute];
        }

        // Reset some settings and empty the viewport

    }, {
        key: 'clearViewer',
        value: function clearViewer() {
            this.viewerState.viewport.top = 0;

            // Clear all the timeouts to prevent undesired pages from loading
            clearTimeout(this.viewerState.resizeTimer);
        }
    }, {
        key: 'hasChangedOption',
        value: function hasChangedOption(options, key) {
            return key in options && options[key] !== this.settings[key];
        }

        //Shortcut for closing fullscreen with the escape key

    }, {
        key: 'escapeListener',
        value: function escapeListener(e) {
            if (e.keyCode === 27) {
                this.reloadViewer({
                    inFullscreen: !this.settings.inFullscreen
                });
            }
        }

        /**
         * Update settings to match the specified options. Load the viewer,
         * fire appropriate events for changed options.
         */

    }, {
        key: 'reloadViewer',
        value: function reloadViewer(newOptions) {
            var _this2 = this;

            var queuedEvents = [];

            newOptions = this.optionsValidator.getValidatedOptions(this.settings, newOptions);

            // Set the zoom level if valid and fire a ZoomLevelDidChange event
            if (this.hasChangedOption(newOptions, 'zoomLevel')) {
                this.viewerState.oldZoomLevel = this.settings.zoomLevel;
                this.viewerState.options.zoomLevel = newOptions.zoomLevel;
                queuedEvents.push(["ZoomLevelDidChange", newOptions.zoomLevel]);
            }

            // Set the pages per row if valid and fire an event
            if (this.hasChangedOption(newOptions, 'pagesPerRow')) {
                this.viewerState.options.pagesPerRow = newOptions.pagesPerRow;
                queuedEvents.push(["GridRowNumberDidChange", newOptions.pagesPerRow]);
            }

            // Update verticallyOriented (no event fired)
            if (this.hasChangedOption(newOptions, 'verticallyOriented')) this.viewerState.options.verticallyOriented = newOptions.verticallyOriented;

            // Show/Hide non-paged pages
            if (this.hasChangedOption(newOptions, 'showNonPagedPages')) {
                this.viewerState.options.showNonPagedPages = newOptions.showNonPagedPages;
            }

            // Update page position (no event fired here)
            if ('goDirectlyTo' in newOptions) {
                this.viewerState.options.goDirectlyTo = newOptions.goDirectlyTo;

                if ('verticalOffset' in newOptions) this.viewerState.verticalOffset = newOptions.verticalOffset;

                if ('horizontalOffset' in newOptions) this.viewerState.horizontalOffset = newOptions.horizontalOffset;
            } else {
                // Otherwise the default is to remain on the current page
                this.viewerState.options.goDirectlyTo = this.settings.currentPageIndex;
            }

            if (this.hasChangedOption(newOptions, 'inGrid') || this.hasChangedOption(newOptions, 'inBookLayout')) {
                if ('inGrid' in newOptions) this.viewerState.options.inGrid = newOptions.inGrid;

                if ('inBookLayout' in newOptions) this.viewerState.options.inBookLayout = newOptions.inBookLayout;

                queuedEvents.push(["ViewDidSwitch", this.settings.inGrid]);
            }

            // Note: prepareModeChange() depends on inGrid and the vertical/horizontalOffset (for now)
            if (this.hasChangedOption(newOptions, 'inFullscreen')) {
                this.viewerState.options.inFullscreen = newOptions.inFullscreen;
                this.prepareModeChange(newOptions);
                queuedEvents.push(["ModeDidSwitch", this.settings.inFullscreen]);
            }

            this.clearViewer();
            this.updateViewHandlerAndRendering();

            if (this.viewerState.renderer) {
                // TODO: The usage of padding variables is still really
                // messy and inconsistent
                var rendererConfig = {
                    pageLayouts: (0, _pageLayouts2.default)(this.settings),
                    padding: this.getPadding(),
                    maxZoomLevel: this.settings.inGrid ? null : this.viewerState.manifest.maxZoom,
                    verticallyOriented: this.settings.verticallyOriented || this.settings.inGrid
                };

                var viewportPosition = {
                    zoomLevel: this.settings.inGrid ? null : this.settings.zoomLevel,
                    anchorPage: this.settings.goDirectlyTo,
                    verticalOffset: this.viewerState.verticalOffset,
                    horizontalOffset: this.viewerState.horizontalOffset
                };

                var sourceProvider = this.getCurrentSourceProvider();

                if (debug.enabled) {
                    var serialized = Object.keys(rendererConfig).filter(function (key) {
                        // Too long
                        return key !== 'pageLayouts' && key !== 'padding';
                    }).map(function (key) {
                        var value = rendererConfig[key];
                        return key + ': ' + JSON.stringify(value);
                    }).join(', ');

                    debug('reload with %s', serialized);
                }

                this.viewerState.renderer.load(rendererConfig, viewportPosition, sourceProvider);
            }

            queuedEvents.forEach(function (params) {
                _this2.publish.apply(_this2, params);
            });

            return true;
        }

        // Handles switching in and out of fullscreen mode

    }, {
        key: 'prepareModeChange',
        value: function prepareModeChange(options) {
            // Toggle the classes
            var changeClass = options.inFullscreen ? 'add' : 'remove';
            this.viewerState.outerObject.classList[changeClass]('diva-fullscreen');
            document.body.classList[changeClass]('diva-hide-scrollbar');
            this.settings.parentObject.classList[changeClass]('diva-full-width');

            // Adjust Diva's internal panel size, keeping the old values
            var storedHeight = this.settings.panelHeight;
            var storedWidth = this.settings.panelWidth;
            this.viewerState.viewport.invalidate();

            // If this isn't the original load, the offsets matter, and the position isn't being changed...
            if (!this.viewerState.loaded && !this.settings.inGrid && !('verticalOffset' in options)) {
                //get the updated panel size
                var newHeight = this.settings.panelHeight;
                var newWidth = this.settings.panelWidth;

                //and re-center the new panel on the same point
                this.viewerState.verticalOffset += (storedHeight - newHeight) / 2;
                this.viewerState.horizontalOffset += (storedWidth - newWidth) / 2;
            }

            //turn on/off escape key listener
            if (options.inFullscreen) document.addEventListener('keyup', this.boundEscapeListener);else document.removeEventListener('keyup', this.boundEscapeListener);
        }

        // Update the view handler and the view rendering for the current view

    }, {
        key: 'updateViewHandlerAndRendering',
        value: function updateViewHandlerAndRendering() {
            var Handler = this.settings.inGrid ? _gridHandler2.default : _documentHandler2.default;

            if (this.viewerState.viewHandler && !(this.viewerState.viewHandler instanceof Handler)) {
                this.viewerState.viewHandler.destroy();
                this.viewerState.viewHandler = null;
            }

            if (!this.viewerState.viewHandler) this.viewerState.viewHandler = new Handler(this);

            if (!this.viewerState.renderer) this.initializeRenderer();
        }

        // TODO: This could probably be done upon ViewerCore initialization

    }, {
        key: 'initializeRenderer',
        value: function initializeRenderer() {
            var _this3 = this;

            var compatErrors = _renderer2.default.getCompatibilityErrors();

            if (compatErrors) {
                this.showError(compatErrors);
            } else {
                var options = {
                    viewport: this.viewerState.viewport,
                    outerElement: this.viewerState.outerElement,
                    innerElement: this.viewerState.innerElement
                };

                var hooks = {
                    onViewWillLoad: function onViewWillLoad() {
                        _this3.viewerState.viewHandler.onViewWillLoad();
                    },
                    onViewDidLoad: function onViewDidLoad() {
                        _this3.updatePageOverlays();
                        _this3.viewerState.viewHandler.onViewDidLoad();
                    },
                    onViewDidUpdate: function onViewDidUpdate(pages, targetPage) {
                        _this3.updatePageOverlays();
                        _this3.viewerState.viewHandler.onViewDidUpdate(pages, targetPage);
                    },
                    onViewDidTransition: function onViewDidTransition() {
                        _this3.updatePageOverlays();
                    },
                    onPageWillLoad: function onPageWillLoad(pageIndex) {
                        _this3.publish('PageWillLoad', pageIndex);
                    },
                    onZoomLevelWillChange: function onZoomLevelWillChange(zoomLevel) {
                        _this3.publish('ZoomLevelWillChange', zoomLevel);
                    }
                };

                this.viewerState.renderer = new _renderer2.default(options, hooks);
            }
        }
    }, {
        key: 'getCurrentSourceProvider',
        value: function getCurrentSourceProvider() {
            var _this4 = this;

            if (this.settings.inGrid) {
                var gridSourceProvider = {
                    getAllZoomLevelsForPage: function getAllZoomLevelsForPage(page) {
                        return [gridSourceProvider.getBestZoomLevelForPage(page)];
                    },
                    getBestZoomLevelForPage: function getBestZoomLevelForPage(page) {
                        var url = _this4.settings.manifest.getPageImageURL(page.index, {
                            width: page.dimensions.width
                        });

                        return {
                            zoomLevel: 1, // FIXME
                            rows: 1,
                            cols: 1,
                            tiles: [{
                                url: url,
                                zoomLevel: 1, // FIXME
                                row: 0,
                                col: 0,
                                dimensions: page.dimensions,
                                offset: {
                                    top: 0,
                                    left: 0
                                }
                            }]
                        };
                    }
                };

                return gridSourceProvider;
            }

            var tileDimensions = {
                width: this.settings.tileWidth,
                height: this.settings.tileHeight
            };

            return {
                getBestZoomLevelForPage: function getBestZoomLevelForPage(page) {
                    return _this4.settings.manifest.getPageImageTiles(page.index, Math.ceil(_this4.settings.zoomLevel), tileDimensions);
                },
                getAllZoomLevelsForPage: function getAllZoomLevelsForPage(page) {
                    var levels = [];
                    var levelCount = _this4.viewerState.manifest.maxZoom;

                    for (var level = 0; level <= levelCount; level++) {
                        levels.push(_this4.settings.manifest.getPageImageTiles(page.index, level, tileDimensions));
                    }

                    levels.reverse();

                    return levels;
                }
            };
        }
    }, {
        key: 'getPadding',
        value: function getPadding() {
            var topPadding = void 0,
                leftPadding = void 0;
            var docVPadding = void 0,
                docHPadding = void 0;

            if (this.settings.inGrid) {
                docVPadding = this.settings.fixedPadding;
                topPadding = leftPadding = docHPadding = 0;
            } else {
                topPadding = this.settings.verticallyOriented ? this.viewerState.verticalPadding : 0;
                leftPadding = this.settings.verticallyOriented ? 0 : this.viewerState.horizontalPadding;

                docVPadding = this.settings.verticallyOriented ? 0 : this.viewerState.verticalPadding;
                docHPadding = this.settings.verticallyOriented ? this.viewerState.horizontalPadding : 0;
            }

            return {
                document: {
                    top: docVPadding,
                    bottom: docVPadding,
                    left: docHPadding,
                    right: docHPadding
                },
                page: {
                    top: topPadding,
                    bottom: 0,
                    left: leftPadding,
                    right: 0
                }
            };
        }
    }, {
        key: 'updatePageOverlays',
        value: function updatePageOverlays() {
            this.viewerState.pageOverlays.updateOverlays(this.viewerState.renderer.getRenderedPages());
        }

        // Called to handle any zoom level

    }, {
        key: 'handleZoom',
        value: function handleZoom(newZoomLevel, focalPoint) {
            var _this5 = this;

            // If the zoom level provided is invalid, return false
            if (!this.isValidOption('zoomLevel', newZoomLevel)) return false;

            // While zooming, don't update scroll offsets based on the scaled version of diva-inner
            this.viewerState.viewportObject.removeEventListener('scroll', this.boundScrollFunction);

            // If no focal point was given, zoom on the center of the viewport
            if (!focalPoint) {
                var viewport = this.viewerState.viewport;
                var currentRegion = this.viewerState.renderer.layout.getPageRegion(this.settings.currentPageIndex);

                focalPoint = {
                    anchorPage: this.settings.currentPageIndex,
                    offset: {
                        left: viewport.width / 2 - (currentRegion.left - viewport.left),
                        top: viewport.height / 2 - (currentRegion.top - viewport.top)
                    }
                };
            }

            var pageRegion = this.viewerState.renderer.layout.getPageRegion(focalPoint.anchorPage);

            // calculate distance from cursor coordinates to center of viewport
            var focalXToCenter = pageRegion.left + focalPoint.offset.left - (this.settings.viewport.left + this.settings.viewport.width / 2);
            var focalYToCenter = pageRegion.top + focalPoint.offset.top - (this.settings.viewport.top + this.settings.viewport.height / 2);

            var getPositionForZoomLevel = function getPositionForZoomLevel(zoomLevel, initZoom) {
                var zoomRatio = Math.pow(2, zoomLevel - initZoom);

                //TODO(jeromepl): Calculate position from page top left to viewport top left
                // calculate horizontal/verticalOffset: distance from viewport center to page upper left corner
                var horizontalOffset = focalPoint.offset.left * zoomRatio - focalXToCenter;
                var verticalOffset = focalPoint.offset.top * zoomRatio - focalYToCenter;

                return {
                    zoomLevel: zoomLevel,
                    anchorPage: focalPoint.anchorPage,
                    verticalOffset: verticalOffset,
                    horizontalOffset: horizontalOffset
                };
            };

            this.viewerState.options.zoomLevel = newZoomLevel;
            var initialZoomLevel = this.viewerState.oldZoomLevel;
            this.viewerState.oldZoomLevel = this.settings.zoomLevel;
            var endPosition = getPositionForZoomLevel(newZoomLevel, initialZoomLevel);
            this.viewerState.options.goDirectlyTo = endPosition.anchorPage;
            this.viewerState.verticalOffset = endPosition.verticalOffset;
            this.viewerState.horizontalOffset = endPosition.horizontalOffset;

            this.viewerState.renderer.transitionViewportPosition({
                duration: this.settings.zoomDuration,
                parameters: {
                    zoomLevel: {
                        from: initialZoomLevel,
                        to: newZoomLevel
                    }
                },
                getPosition: function getPosition(parameters) {
                    return getPositionForZoomLevel(parameters.zoomLevel, initialZoomLevel);
                },
                onEnd: function onEnd(info) {
                    _this5.viewerState.viewportObject.addEventListener('scroll', _this5.boundScrollFunction);

                    if (info.interrupted) _this5.viewerState.oldZoomLevel = newZoomLevel;
                }
            });

            // Send off the zoom level did change event.
            this.publish("ZoomLevelDidChange", newZoomLevel);

            return true;
        }

        /*
         Gets the Y-offset for a specific point on a specific page
         Acceptable values for "anchor":
         "top" (default) - will anchor top of the page to the top of the diva-outer element
         "bottom" - top, s/top/bottom
         "center" - will center the page on the diva element
         Returned value will be the distance from the center of the diva-outer element to the top of the current page for the specified anchor
         */

    }, {
        key: 'getYOffset',
        value: function getYOffset(pageIndex, anchor) {
            var pidx = typeof pageIndex === "undefined" ? this.settings.currentPageIndex : pageIndex;

            if (anchor === "center" || anchor === "centre") //how you can tell an American coded this
                {
                    return parseInt(this.getPageData(pidx, "h") / 2, 10);
                } else if (anchor === "bottom") {
                return parseInt(this.getPageData(pidx, "h") - this.settings.panelHeight / 2, 10);
            } else {
                return parseInt(this.settings.panelHeight / 2, 10);
            }
        }

        //Same as getYOffset with "left" and "right" as acceptable values instead of "top" and "bottom"

    }, {
        key: 'getXOffset',
        value: function getXOffset(pageIndex, anchor) {
            var pidx = typeof pageIndex === "undefined" ? this.settings.currentPageIndex : pageIndex;

            if (anchor === "left") {
                return parseInt(this.settings.panelWidth / 2, 10);
            } else if (anchor === "right") {
                return parseInt(this.getPageData(pidx, "w") - this.settings.panelWidth / 2, 10);
            } else {
                return parseInt(this.getPageData(pidx, "w") / 2, 10);
            }
        }

        // updates panelHeight/panelWidth on resize

    }, {
        key: 'updatePanelSize',
        value: function updatePanelSize() {
            this.viewerState.viewport.invalidate();

            // FIXME(wabain): This should really only be called after initial load
            if (this.viewerState.renderer) {
                this.updateOffsets();
                this.viewerState.renderer.goto(this.settings.currentPageIndex, this.viewerState.verticalOffset, this.viewerState.horizontalOffset);
            }

            return true;
        }
    }, {
        key: 'updateOffsets',
        value: function updateOffsets() {
            var pageOffset = this.viewerState.renderer.layout.getPageToViewportCenterOffset(this.settings.currentPageIndex, this.viewerState.viewport);

            if (pageOffset) {
                this.viewerState.horizontalOffset = pageOffset.x;
                this.viewerState.verticalOffset = pageOffset.y;
            }
        }

        // Bind mouse events (drag to scroll, double-click)

    }, {
        key: 'bindMouseEvents',
        value: function bindMouseEvents() {
            var _this6 = this;

            // Set drag scroll on the viewport object
            this.viewerState.viewportObject.classList.add('dragscroll');

            _gestureEvents2.default.onDoubleClick(this.viewerState.viewportObject, function (event, coords) {
                debug('Double click at %s, %s', coords.left, coords.top);
                _this6.viewerState.viewHandler.onDoubleClick(event, coords);
            });
        }
    }, {
        key: 'onResize',
        value: function onResize() {
            var _this7 = this;

            this.updatePanelSize();
            // Cancel any previously-set resize timeouts
            clearTimeout(this.viewerState.resizeTimer);

            this.viewerState.resizeTimer = setTimeout(function () {
                var pageOffset = _this7.viewerState.renderer.layout.getPageToViewportCenterOffset(_this7.settings.currentPageIndex, _this7.viewerState.viewport);

                if (pageOffset) {
                    _this7.reloadViewer({
                        goDirectlyTo: _this7.settings.currentPageIndex,
                        verticalOffset: pageOffset.y,
                        horizontalOffset: pageOffset.x
                    });
                } else {
                    _this7.reloadViewer({
                        goDirectlyTo: _this7.settings.currentPageIndex
                    });
                }
            }, 200);
        }

        // Bind touch and orientation change events

    }, {
        key: 'bindTouchEvents',
        value: function bindTouchEvents() {
            // Block the user from moving the window only if it's not integrated
            if (this.settings.blockMobileMove) {
                document.body.addEventListener('touchmove', function (event) {
                    var e = event.originalEvent;
                    e.preventDefault();

                    return false;
                });
            }

            // Touch events for swiping in the viewport to scroll pages
            // this.viewerState.viewportObject.addEventListener('scroll', this.scrollFunction.bind(this));

            _gestureEvents2.default.onPinch(this.viewerState.viewportObject, function (event, coords, start, end) {
                debug('Pinch %s at %s, %s', end - start, coords.left, coords.top);
                this.viewerState.viewHandler.onPinch(event, coords, start, end);
            });

            _gestureEvents2.default.onDoubleTap(this.viewerState.viewportObject, function (event, coords) {
                debug('Double tap at %s, %s', coords.left, coords.top);
                this.viewerState.viewHandler.onDoubleClick(event, coords);
            });
        }

        // Handle the scroll

    }, {
        key: 'scrollFunction',
        value: function scrollFunction() {
            var previousTopScroll = this.viewerState.viewport.top;
            var previousLeftScroll = this.viewerState.viewport.left;

            var direction = void 0;

            this.viewerState.viewport.invalidate();

            var newScrollTop = this.viewerState.viewport.top;
            var newScrollLeft = this.viewerState.viewport.left;

            if (this.settings.verticallyOriented || this.settings.inGrid) direction = newScrollTop - previousTopScroll;else direction = newScrollLeft - previousLeftScroll;

            //give adjust the direction we care about
            this.viewerState.renderer.adjust();

            var primaryScroll = this.settings.verticallyOriented || this.settings.inGrid ? newScrollTop : newScrollLeft;

            this.publish("ViewerDidScroll", primaryScroll);

            if (direction > 0) {
                this.publish("ViewerDidScrollDown", primaryScroll);
            } else if (direction < 0) {
                this.publish("ViewerDidScrollUp", primaryScroll);
            }

            this.updateOffsets();
        }

        // Binds most of the event handlers (some more in createToolbar)

    }, {
        key: 'handleEvents',
        value: function handleEvents() {
            var _this8 = this;

            // Change the cursor for dragging
            this.viewerState.innerObject.addEventListener('mousedown', function () {
                _this8.viewerState.innerObject.classList.add('diva-grabbing');
            });

            this.viewerState.innerObject.addEventListener('mouseup', function () {
                _this8.viewerState.innerObject.classList.remove('diva-grabbing');
            });

            this.bindMouseEvents();
            this.viewerState.viewportObject.addEventListener('scroll', this.boundScrollFunction);

            var upArrowKey = 38,
                downArrowKey = 40,
                leftArrowKey = 37,
                rightArrowKey = 39,
                spaceKey = 32,
                pageUpKey = 33,
                pageDownKey = 34,
                homeKey = 36,
                endKey = 35;

            // Catch the key presses in document
            document.addEventListener('keydown.diva', function (event) {
                if (!_this8.viewerState.isActiveDiva) return true;

                // Space or page down - go to the next page
                if (_this8.settings.enableSpaceScroll && !event.shiftKey && event.keyCode === spaceKey || _this8.settings.enableKeyScroll && event.keyCode === pageDownKey) {
                    _this8.viewerState.viewport.top += _this8.settings.panelHeight;
                    return false;
                } else if (!_this8.settings.enableSpaceScroll && event.keyCode === spaceKey) {
                    event.preventDefault();
                }

                if (_this8.settings.enableKeyScroll) {
                    // Don't steal keyboard shortcuts (metaKey = command [OS X], super [Win/Linux])
                    if (event.shiftKey || event.ctrlKey || event.metaKey) return true;

                    switch (event.keyCode) {
                        case pageUpKey:
                            // Page up - go to the previous page
                            _this8.viewerState.viewport.top -= _this8.settings.panelHeight;
                            return false;

                        case upArrowKey:
                            // Up arrow - scroll up
                            _this8.viewerState.viewport.top -= _this8.settings.arrowScrollAmount;
                            return false;

                        case downArrowKey:
                            // Down arrow - scroll down
                            _this8.viewerState.viewport.top += _this8.settings.arrowScrollAmount;
                            return false;

                        case leftArrowKey:
                            // Left arrow - scroll left
                            _this8.viewerState.viewport.left -= _this8.settings.arrowScrollAmount;
                            return false;

                        case rightArrowKey:
                            // Right arrow - scroll right
                            _this8.viewerState.viewport.left += _this8.settings.arrowScrollAmount;
                            return false;

                        case homeKey:
                            // Home key - go to the beginning of the document
                            _this8.viewerState.viewport.top = 0;
                            return false;

                        case endKey:
                            // End key - go to the end of the document
                            // Count on the viewport coordinate value being normalized
                            if (_this8.settings.verticallyOriented) _this8.viewerState.viewport.top = Infinity;else _this8.viewerState.viewport.left = Infinity;

                            return false;

                        default:
                            return true;
                    }
                }
                return true;
            });

            _divaGlobal2.default.Events.subscribe('ViewerDidTerminate', function () {
                document.removeEventListener('keydown.diva');
            }, this.settings.ID);

            // this.bindTouchEvents();

            // Handle window resizing events
            window.addEventListener('resize', this.onResize.bind(this), false);

            _divaGlobal2.default.Events.subscribe('ViewerDidTerminate', function () {
                window.removeEventListener('resize', this.onResize, false);
            }, this.settings.ID);

            // Handle orientation change separately
            if ('onorientationchange' in window) {
                window.addEventListener('orientationchange', this.onResize, false);

                _divaGlobal2.default.Events.subscribe('ViewerDidTerminate', function () {
                    window.removeEventListener('orientationchange', this.onResize, false);
                }, this.settings.ID);
            }

            _divaGlobal2.default.Events.subscribe('PanelSizeDidChange', this.updatePanelSize, this.settings.ID);

            // Clear page and resize timeouts when the viewer is destroyed
            _divaGlobal2.default.Events.subscribe('ViewerDidTerminate', function () {
                if (_this8.viewerState.renderer) _this8.viewerState.renderer.destroy();

                clearTimeout(_this8.viewerState.resizeTimer);
            }, this.settings.ID);
        }
    }, {
        key: 'initPlugins',
        value: function initPlugins() {
            var _this9 = this;

            if (!this.settings.hasOwnProperty('plugins')) return null;

            this.viewerState.pluginInstances = this.settings.plugins.map(function (plugin) {
                var p = new plugin(_this9);

                if (p.isPageTool) _this9.viewerState.pageTools.push(p);

                return p;
            });
        }
    }, {
        key: 'showThrobber',
        value: function showThrobber() {
            var _this10 = this;

            this.hideThrobber();

            this.viewerState.throbberTimeoutID = setTimeout(function () {
                var thb = document.getElementById(_this10.settings.selector + 'throbber');
                if (thb) thb.style.display = 'block';
            }, this.settings.throbberTimeout);
        }
    }, {
        key: 'hideThrobber',
        value: function hideThrobber() {
            // Clear the timeout, if it hasn't executed yet
            clearTimeout(this.viewerState.throbberTimeoutID);

            var thb = document.getElementById(this.settings.selector + 'throbber');
            // Hide the throbber if it has already executed
            if (thb) thb.style.display = 'none';
        }
    }, {
        key: 'showError',
        value: function showError(message) {
            var errorElement = (0, _elt.elt)('div', this.elemAttrs('error'), [(0, _elt.elt)('button', this.elemAttrs('error-close', { 'aria-label': 'Close dialog' })), (0, _elt.elt)('p', (0, _elt.elt)('strong', 'Error')), (0, _elt.elt)('div', message)]);

            this.viewerState.outerObject.appendChild(errorElement);

            //bind dialog close button
            document.querySelector(this.settings.selector + 'error-close').addEventListener('click', function () {
                errorElement.parentNode.removeChild(errorElement);
            });
        }
    }, {
        key: 'setManifest',
        value: function setManifest(manifest, loadOptions) {
            this.viewerState.manifest = manifest;

            this.hideThrobber();

            // Convenience value
            this.viewerState.numPages = this.settings.manifest.pages.length;

            this.optionsValidator.validate(this.viewerState.options);

            this.publish('NumberOfPagesDidChange', this.settings.numPages);

            if (this.settings.enableAutoTitle) {
                var title = document.getElementById(this.settings.selector + 'title');

                if (title) {
                    title.innerHTML(this.settings.manifest.itemTitle);
                } else {
                    this.settings.parentObject.insertBefore((0, _elt.elt)('div', this.elemAttrs('title'), [this.settings.manifest.itemTitle]), this.settings.parentObject.firstChild);
                }
            }

            // Calculate the horizontal and vertical inter-page padding based on the dimensions of the average zoom level
            if (this.settings.adaptivePadding > 0) {
                var z = Math.floor((this.settings.minZoomLevel + this.settings.maxZoomLevel) / 2);
                this.viewerState.horizontalPadding = parseInt(this.settings.manifest.getAverageWidth(z) * this.settings.adaptivePadding, 10);
                this.viewerState.verticalPadding = parseInt(this.settings.manifest.getAverageHeight(z) * this.settings.adaptivePadding, 10);
            } else {
                // It's less than or equal to 0; use fixedPadding instead
                this.viewerState.horizontalPadding = this.settings.fixedPadding;
                this.viewerState.verticalPadding = this.settings.fixedPadding;
            }

            // Make sure the vertical padding is at least 40, if plugin icons are enabled
            if (this.viewerState.pageTools.length) {
                this.viewerState.verticalPadding = Math.max(40, this.viewerState.verticalPadding);
            }

            // If we detect a viewingHint of 'paged' in the manifest or sequence, enable book view by default
            if (this.settings.manifest.paged) {
                this.viewerState.options.inBookLayout = true;
            }

            // Plugin setup hooks should be bound to the ObjectDidLoad event
            this.publish('ObjectDidLoad', this.settings);

            // Adjust the document panel dimensions
            this.updatePanelSize();

            var needsXCoord = void 0,
                needsYCoord = void 0;

            var anchoredVertically = false;
            var anchoredHorizontally = false;

            // NB: `==` here will check both null and undefined
            if (loadOptions.goDirectlyTo == null) {
                loadOptions.goDirectlyTo = this.settings.goDirectlyTo;
                needsXCoord = needsYCoord = true;
            } else {
                needsXCoord = loadOptions.horizontalOffset == null || isNaN(loadOptions.horizontalOffset);
                needsYCoord = loadOptions.verticalOffset == null || isNaN(loadOptions.verticalOffset);
            }

            // Set default values for the horizontal and vertical offsets
            if (needsXCoord) {
                // FIXME: What if inBookLayout/verticallyOriented is changed by loadOptions?
                if (loadOptions.goDirectlyTo === 0 && this.settings.inBookLayout && this.settings.verticallyOriented) {
                    // if in book layout, center the first opening by default
                    loadOptions.horizontalOffset = this.viewerState.horizontalPadding;
                } else {
                    anchoredHorizontally = true;
                    loadOptions.horizontalOffset = this.getXOffset(loadOptions.goDirectlyTo, "center");
                }
            }

            if (needsYCoord) {
                anchoredVertically = true;
                loadOptions.verticalOffset = this.getYOffset(loadOptions.goDirectlyTo, "top");
            }

            this.reloadViewer(loadOptions);

            //prep dimensions one last time now that pages have loaded
            this.updatePanelSize();

            // FIXME: This is a hack to ensure that the outerElement scrollbars are taken into account
            if (this.settings.verticallyOriented) this.viewerState.innerElement.style.minWidth = this.settings.panelWidth + 'px';else this.viewerState.innerElement.style.minHeight = this.settings.panelHeight + 'px';

            // FIXME: If the page was supposed to be positioned relative to the viewport we need to
            // recalculate it to take into account the scrollbars
            if (anchoredVertically || anchoredHorizontally) {
                if (anchoredVertically) this.viewerState.verticalOffset = this.getYOffset(this.settings.currentPageIndex, "top");

                if (anchoredHorizontally) this.viewerState.horizontalOffset = this.getXOffset(this.settings.currentPageIndex, "center");

                this.viewerState.renderer.goto(this.settings.currentPageIndex, this.viewerState.verticalOffset, this.viewerState.horizontalOffset);
            }

            // signal that everything should be set up and ready to go.
            this.viewerState.loaded = true;

            this.publish("ViewerDidLoad", this.settings);
        }
    }, {
        key: 'publish',
        value: function publish(event) {
            var args = Array.prototype.slice.call(arguments, 1);
            _divaGlobal2.default.Events.publish(event, args, this.publicInstance);
        }
    }, {
        key: 'getSettings',
        value: function getSettings() {
            return this.settings;
        }

        // Temporary accessor for the state of the viewer core
        // TODO: Replace this with a more restricted view of whatever needs
        // be exposed through settings for backwards compat

    }, {
        key: 'getInternalState',
        value: function getInternalState() {
            return this.viewerState;
        }
    }, {
        key: 'getPublicInstance',
        value: function getPublicInstance() {
            return this.publicInstance;
        }
    }, {
        key: 'getPageTools',
        value: function getPageTools() {
            return this.viewerState.pageTools;
        }
    }, {
        key: 'getCurrentLayout',
        value: function getCurrentLayout() {
            return this.viewerState.renderer ? this.viewerState.renderer.layout : null;
        }

        /** Get a copy of the current viewport dimensions */

    }, {
        key: 'getViewport',
        value: function getViewport() {
            var viewport = this.viewerState.viewport;

            return {
                top: viewport.top,
                left: viewport.left,
                bottom: viewport.bottom,
                right: viewport.right,

                width: viewport.width,
                height: viewport.height
            };
        }
    }, {
        key: 'addPageOverlay',
        value: function addPageOverlay(overlay) {
            this.viewerState.pageOverlays.addOverlay(overlay);
        }
    }, {
        key: 'removePageOverlay',
        value: function removePageOverlay(overlay) {
            this.viewerState.pageOverlays.removeOverlay(overlay);
        }
    }, {
        key: 'getPageRegion',
        value: function getPageRegion(pageIndex, options) {
            var layout = this.viewerState.renderer.layout;
            var region = layout.getPageRegion(pageIndex, options);

            if (options && options.incorporateViewport) {
                var secondaryDim = this.settings.verticallyOriented ? 'width' : 'height';

                if (this.viewerState.viewport[secondaryDim] > layout.dimensions[secondaryDim]) {
                    var docOffset = (this.viewerState.viewport[secondaryDim] - layout.dimensions[secondaryDim]) / 2;

                    if (this.settings.verticallyOriented) {
                        return {
                            top: region.top,
                            bottom: region.bottom,

                            left: region.left + docOffset,
                            right: region.right + docOffset
                        };
                    } else {
                        return {
                            top: region.top + docOffset,
                            bottom: region.bottom + docOffset,

                            left: region.left,
                            right: region.right
                        };
                    }
                }
            }

            return region;
        }
    }, {
        key: 'getPagePositionAtViewportOffset',
        value: function getPagePositionAtViewportOffset(coords) {
            var docCoords = {
                left: coords.left + this.viewerState.viewport.left,
                top: coords.top + this.viewerState.viewport.top
            };

            var renderedPages = this.viewerState.renderer.getRenderedPages();
            var pageCount = renderedPages.length;

            // Find the page on which the coords occur
            for (var i = 0; i < pageCount; i++) {
                var pageIndex = renderedPages[i];
                var region = this.viewerState.renderer.layout.getPageRegion(pageIndex);

                if (region.left <= docCoords.left && region.right >= docCoords.left && region.top <= docCoords.top && region.bottom >= docCoords.top) {
                    return {
                        anchorPage: pageIndex,
                        offset: {
                            left: docCoords.left - region.left,
                            top: docCoords.top - region.top
                        }
                    };
                }
            }

            // Fall back to current page
            // FIXME: Would be better to use the closest page or something
            var currentRegion = this.viewerState.renderer.layout.getPageRegion(this.settings.currentPageIndex);

            return {
                anchorPage: this.settings.currentPageIndex,
                offset: {
                    left: docCoords.left - currentRegion.left,
                    top: docCoords.top - currentRegion.top
                }
            };
        }

        // setManifest (manifest, loadOptions)
        // {
        //     setManifest(manifest, loadOptions || {});
        // }

        /**
         * Set the current page to the given index, firing VisiblePageDidChange
         *
         * @param pageIndex
         */

    }, {
        key: 'setCurrentPage',
        value: function setCurrentPage(pageIndex) {
            if (this.viewerState.currentPageIndex !== pageIndex) {
                this.viewerState.currentPageIndex = pageIndex;
                this.publish("VisiblePageDidChange", pageIndex, this.getPageName(pageIndex));

                // Publish an event if the page we're switching to has other images.
                if (this.viewerState.manifest.pages[pageIndex].otherImages.length > 0) this.publish('VisiblePageHasAlternateViews', pageIndex);
            }
        }
    }, {
        key: 'getPageName',
        value: function getPageName(pageIndex) {
            return this.viewerState.manifest.pages[pageIndex].f;
        }
    }, {
        key: 'reload',
        value: function reload(newOptions) {
            this.reloadViewer(newOptions);
        }
    }, {
        key: 'zoom',
        value: function zoom(zoomLevel, focalPoint) {
            return this.handleZoom(zoomLevel, focalPoint);
        }
    }, {
        key: 'enableScrollable',
        value: function enableScrollable() {
            if (!this.viewerState.isScrollable) {
                this.bindMouseEvents();
                this.viewerState.options.enableKeyScroll = this.viewerState.initialKeyScroll;
                this.viewerState.options.enableSpaceScroll = this.viewerState.initialSpaceScroll;
                this.viewerState.viewportElement.style.overflow = 'auto';
                this.viewerState.isScrollable = true;
            }
        }
    }, {
        key: 'disableScrollable',
        value: function disableScrollable() {
            if (this.viewerState.isScrollable) {
                // block dragging/double-click zooming
                if (this.viewerState.innerObject.hasClass('diva-dragger')) this.viewerState.innerObject.mousedown = null;

                this.viewerState.outerObject.dblclick = null;
                this.viewerState.outerObject.contextmenu = null;

                // disable all other scrolling actions
                this.viewerState.viewportElement.style.overflow = 'hidden';

                // block scrolling keys behavior, respecting initial scroll settings
                this.viewerState.initialKeyScroll = this.settings.enableKeyScroll;
                this.viewerState.initialSpaceScroll = this.settings.enableSpaceScroll;
                this.viewerState.options.enableKeyScroll = false;
                this.viewerState.options.enableSpaceScroll = false;

                this.viewerState.isScrollable = false;
            }
        }

        // isValidOption (key, value)
        // {
        //     return isValidOption(key, value);
        // }

        // getXOffset (pageIndex, xAnchor)
        // {
        //     return getXOffset(pageIndex, xAnchor);
        // }

        // getYOffset (pageIndex, yAnchor)
        // {
        //     return getYOffset(pageIndex, yAnchor);
        // }

        // this.publish = publish;

    }, {
        key: 'clear',
        value: function clear() {
            this.clearViewer();
        }
    }, {
        key: 'setPendingManifestRequest',
        value: function setPendingManifestRequest(pendingManifestRequest) {
            this.viewerState.pendingManifestRequest = pendingManifestRequest;
        }
    }, {
        key: 'destroy',
        value: function destroy() {
            // Useful event to access elements in diva before they get destroyed. Used by the highlight plugin.
            this.publish('ViewerWillTerminate', this.settings);

            // Cancel any pending request retrieving a manifest
            if (this.settings.pendingManifestRequest) this.settings.pendingManifestRequest.abort();

            // Removes the hide-scrollbar class from the body
            document.body.removeClass('diva-hide-scrollbar');

            // Empty the parent container and remove any diva-related data
            this.settings.parentObject.parent().empty().removeData('diva');

            // Remove any additional styling on the parent element
            this.settings.parentObject.parent().removeAttr('style').removeAttr('class');

            this.publish('ViewerDidTerminate', this.settings);

            // Clear the Events cache
            _divaGlobal2.default.Events.unsubscribeAll(this.settings.ID);
        }
    }]);

    return ViewerCore;
}();

exports.default = ViewerCore;

/***/ }),

/***/ "./source/js/viewport.js":
/*!*******************************!*\
  !*** ./source/js/viewport.js ***!
  \*******************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var Viewport = function () {
    function Viewport(outer, options) {
        _classCallCheck(this, Viewport);

        options = options || {};

        this.intersectionTolerance = options.intersectionTolerance || 0;
        this.maxExtent = options.maxExtent || 2000;

        this.outer = outer;

        this._top = this._left = this._width = this._height = this._innerDimensions = null;

        this.invalidate();
    }

    _createClass(Viewport, [{
        key: 'intersectsRegion',
        value: function intersectsRegion(region) {
            return this.hasHorizontalOverlap(region) && this.hasVerticalOverlap(region);
        }
    }, {
        key: 'hasVerticalOverlap',
        value: function hasVerticalOverlap(region) {
            var top = this.top - this.intersectionTolerance;
            var bottom = this.bottom + this.intersectionTolerance;

            return fallsBetween(region.top, top, bottom) || fallsBetween(region.bottom, top, bottom) || region.top <= top && region.bottom >= bottom;
        }
    }, {
        key: 'hasHorizontalOverlap',
        value: function hasHorizontalOverlap(region) {
            var left = this.left - this.intersectionTolerance;
            var right = this.right + this.intersectionTolerance;

            return fallsBetween(region.left, left, right) || fallsBetween(region.right, left, right) || region.left <= left && region.right >= right;
        }
    }, {
        key: 'invalidate',
        value: function invalidate() {
            // FIXME: Should this check the inner dimensions as well?
            this._width = clampMax(this.outer.clientWidth, this.maxExtent);
            this._height = clampMax(this.outer.clientHeight, this.maxExtent);

            this._top = this.outer.scrollTop;
            this._left = this.outer.scrollLeft;
        }
    }, {
        key: 'setInnerDimensions',
        value: function setInnerDimensions(dimensions) {
            this._innerDimensions = dimensions;

            if (dimensions) {
                this._top = clamp(this._top, 0, dimensions.height - this._height);
                this._left = clamp(this._left, 0, dimensions.width - this._width);
            }
        }
    }]);

    return Viewport;
}();

exports.default = Viewport;


Object.defineProperties(Viewport.prototype, {
    top: getCoordinateDescriptor('top', 'height'),
    left: getCoordinateDescriptor('left', 'width'),

    width: getDimensionDescriptor('width'),
    height: getDimensionDescriptor('height'),

    bottom: {
        get: function get() {
            return this._top + this._height;
        }
    },
    right: {
        get: function get() {
            return this._left + this._width;
        }
    }
});

function getCoordinateDescriptor(coord, associatedDimension) {
    var privateProp = '_' + coord;
    var source = 'scroll' + coord.charAt(0).toUpperCase() + coord.slice(1);

    return {
        get: function get() {
            return this[privateProp];
        },
        set: function set(newValue) {
            var normalized = void 0;

            if (this._innerDimensions) {
                var maxAllowed = this._innerDimensions[associatedDimension] - this[associatedDimension];
                normalized = clamp(newValue, 0, maxAllowed);
            } else {
                normalized = clampMin(newValue, 0);
            }

            this[privateProp] = this.outer[source] = normalized;
        }
    };
}

function getDimensionDescriptor(dimen) {
    return {
        get: function get() {
            return this['_' + dimen];
        }
    };
}

function fallsBetween(point, start, end) {
    return point >= start && point <= end;
}

function clamp(value, min, max) {
    return clampMin(clampMax(value, max), min);
}

function clampMin(value, min) {
    return Math.max(value, min);
}

function clampMax(value, max) {
    return Math.min(value, max);
}

/***/ }),

/***/ 0:
/*!*******************************************************************!*\
  !*** multi whatwg-fetch array.prototype.fill ./source/js/diva.js ***!
  \*******************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(/*! whatwg-fetch */"./node_modules/whatwg-fetch/fetch.js");
__webpack_require__(/*! array.prototype.fill */"./node_modules/array.prototype.fill/index.js");
module.exports = __webpack_require__(/*! ./source/js/diva.js */"./source/js/diva.js");


/***/ })

/******/ });
//# sourceMappingURL=diva.js.map