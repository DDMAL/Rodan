'use strict';

////////////////////////////////////////////////////////////////////////////////
// REQUIRE
////////////////////////////////////////////////////////////////////////////////
const async = require('async');
const del = require('del');
const fs = require('fs');
const gulp = require('gulp');
const ip = require('ip');
const path = require('path');
const recread = require('recursive-readdir');
const sass = require('gulp-sass');
const vfs = require('vinyl-fs');
const webpack = require('webpack');
const WebpackDevServer = require("webpack-dev-server");

////////////////////////////////////////////////////////////////////////////////
// CONFIGURATION - Develop
////////////////////////////////////////////////////////////////////////////////
const DEVELOP_HOST = process.env.RODAN_CLIENT_DEVELOP_HOST || "localhost";
const DEVELOP_PORT = 9002;
const DEVELOP_SOURCEMAP = 'eval-source-map';
const DEVELOP_WEBROOT = '__develop__';

////////////////////////////////////////////////////////////////////////////////
// CONFIGURATION - Dist
////////////////////////////////////////////////////////////////////////////////
const DIST_SOURCEMAP = 'source-map';
const DIST_WEBROOT = 'dist';

////////////////////////////////////////////////////////////////////////////////
// NOTE: don't edit this unless you know what you're doing.
////////////////////////////////////////////////////////////////////////////////
const CONFIGURATION_FILE = 'configuration.json';
const CONFIGURATION_EXAMPLE_FILE = 'configuration.example.json';
const ENTRY_FILE = './src/js/main.js';
const INFO_FILE = 'info.json';
const NODE_MODULES_DIRECTORY = '/node_modules';
const OUTPUT_FILE = 'rodan_client.min.js';
const PACKAGE_FILE = 'package.json';
const PLUGINS_INCLUSION_FILE = '/plugins.json';
const PLUGINS_FILE = '.plugins.js';
const RESOURCES_DIRECTORY = 'resources';
const SOURCE_DIRECTORY = 'src/js';
const TEMPLATE_DIRECTORY = 'templates';

////////////////////////////////////////////////////////////////////////////////
// WEBPACK
////////////////////////////////////////////////////////////////////////////////
var webpackConfig =
{
    entry: ENTRY_FILE,
    output:
    {
        filename: OUTPUT_FILE
    },
    module: {rules: []},
    resolve:
    {
        modules: [
            path.resolve(__dirname + '/src'),
            path.resolve(__dirname + '/node_modules')
        ]
    },
    plugins: [new webpack.ProvidePlugin({jQuery: "jquery"})]
};
var webpackServerConfig = {};

////////////////////////////////////////////////////////////////////////////////
// TASKS - Plugins
////////////////////////////////////////////////////////////////////////////////
/**
 * Create '.plugins.js' based on contents of config.
 */
const pluginsImport = function(callback) {
    var pluginList = getPluginList();
    var pluginsPath = path.resolve(__dirname, SOURCE_DIRECTORY + '/' + PLUGINS_FILE);
    var plugins = 'import WorkflowBuilderGUI from \'./WorkflowBuilderGUI.js\'';

    /**
    for (var i = 0; i < pluginList.length; i++)
    {
        plugins += 'import \'' + pluginList[i] + '\';\n';
    } */

    fs.writeFileSync(pluginsPath, plugins);

    // Set the creation and modification time for the newly generated file to 10 seconds ago,
    // to work around a bug in webpack.
    // See https://github.com/webpack/watchpack/issues/25#issuecomment-287789288
    var tenSecondsAgo = Date.now() / 1000 - 10
    fs.utimes(pluginsPath, tenSecondsAgo, tenSecondsAgo, function (err) { if (err) throw err; });

    callback();
};

////////////////////////////////////////////////////////////////////////////////
// TASKS - Develop
////////////////////////////////////////////////////////////////////////////////

/**
 * Clean out develop
 */
const developClean = function() {
    return del([DEVELOP_WEBROOT]);
};

/**
 * Make web directory.
 */
const developMkdir = gulp.series(developClean, function(callback) {
    return fs.mkdir(DEVELOP_WEBROOT, callback);
});

/**
 * Build Webpack configs for develop.
 */
const developConfig = function(callback) {
    webpackConfig.mode = 'development';
    webpackConfig.devtool = DEVELOP_SOURCEMAP;
    webpackConfig.output.path = path.resolve(__dirname, DEVELOP_WEBROOT);
    webpackServerConfig.contentBase = DEVELOP_WEBROOT;
    callback();
};

/**
 * Build templates.
 */
const developTemplates = function(callback) {
    // Get plugin templates. When done, get the main templates.
    var pluginList = getPluginList();
    var pluginTemplates = '';
    async.each(pluginList, function(plugin, done)
    {
        var pluginPath = path.resolve(__dirname, NODE_MODULES_DIRECTORY + '/' + plugin + '/templates');
        buildTemplates(pluginPath, [], function(error, templates)
        {
            if (error)
            {
                done(error);
            }
            pluginTemplates += templates;
            done();
        });
    },
    function(error)
    {
        if (error)
        {
            callback(error);
        }

        // Get the main templates.
        buildTemplates(TEMPLATE_DIRECTORY, ['index.html'], function(err, mainTemplates)
        {
            var indexFile = fs.readFileSync(TEMPLATE_DIRECTORY + '/index.html', 'utf8');
            indexFile = indexFile.replace('{templates}', mainTemplates + pluginTemplates);
            fs.writeFileSync(DEVELOP_WEBROOT + '/index.html', indexFile);
            callback();
        });
    });
};

/**
 * Compile SCSS to CSS.
 */
const developStyles = function() {
    return gulp.src('styles/default.scss')
        .pipe(sass())
        .pipe(gulp.dest(DEVELOP_WEBROOT));
};

/**
 * Creates info.json. This holds client data, such as version.
 * It's basically a trimmed 'package.json'
 */
const developInfo = function(callback) {
    var info = createInfo(function(err, data)
    {
        fs.writeFileSync(DEVELOP_WEBROOT + '/' + INFO_FILE, JSON.stringify(data, null, 4));
        callback();
    });
};

/**
 * Links build results to web directory.
 */
const developLink = function() {
    return gulp.src([CONFIGURATION_FILE, RESOURCES_DIRECTORY]).pipe(vfs.symlink(DEVELOP_WEBROOT));
};

/**
 * Bundle (Webpack) and start the development server.
 */
const develop = gulp.series(
    pluginsImport,
    developMkdir,
    developConfig,
    gulp.parallel(developStyles, developTemplates, developInfo, developLink),
    function(callback) {
        var compiler = webpack(webpackConfig);
        var server = new WebpackDevServer(compiler, webpackServerConfig);
        server.listen(DEVELOP_PORT, DEVELOP_HOST, function(err)
        {
            console.log('');
            console.log('==========');
            console.log('Starting server on: http://' + DEVELOP_HOST + ':' + DEVELOP_PORT);
            console.log('Serving: ' + DEVELOP_WEBROOT);
            console.log('');
            console.log('Make sure ' + DEVELOP_HOST + ':' + DEVELOP_PORT + ' is allowed access to the Rodan server');
            console.log('==========');
            console.log('');
        });
    });

////////////////////////////////////////////////////////////////////////////////
// TASKS - Distribution
////////////////////////////////////////////////////////////////////////////////
/**
 * Cleans out dist.
 */
 const distClean = function() {
     return del([DIST_WEBROOT]);
 }

 /**
  * Make dist directory
  */
 const distMkdir = gulp.series(distClean, function(callback) {
     return fs.mkdir(DIST_WEBROOT, callback);
 });

 /**
  * Build Webpack configs for dist.
  */
 const distConfig = function(callback) {
     var babelRule = {
         test: /\.(js)$/,
         exclude: /node_modules/,
         use: {
             loader: 'babel-loader',
             options: {
                 presets: [
                     [
                         '@babel/preset-env',
                         {
                             targets: 'defaults',
                             useBuiltIns: 'usage',
                             corejs: { version: 3, proposals: true }
                         }
                     ]
                 ]
             }
         }
     };
     // No more babel. This kills the rodan client.
     // webpackConfig.module.rules.push(babelRule);
     webpackConfig.mode = 'development';
     webpackConfig.devtool = DIST_SOURCEMAP;
     webpackConfig.output.path = path.resolve(__dirname, DIST_WEBROOT);
     callback();
 };

 /**
  * Build templates.
  */
 const distTemplates = function(callback) {
     // Get plugin templates. When done, get the main templates.
     var pluginList = getPluginList();
     var pluginTemplates = '';
     async.each(pluginList, function(plugin, done)
     {
         var pluginPath = path.resolve(__dirname, NODE_MODULES_DIRECTORY + '/' + plugin + '/templates');
         buildTemplates(pluginPath, [], function(error, templates)
         {
             if (error)
             {
                 done(error);
             }
             pluginTemplates += templates;
             done();
         });
     },
     function(error)
     {
         if (error)
         {
             callback(error);
         }

         // Get the main templates.
         buildTemplates(TEMPLATE_DIRECTORY, ['index.html'], function(err, mainTemplates)
         {
             var indexFile = fs.readFileSync(TEMPLATE_DIRECTORY + '/index.html', 'utf8');
             indexFile = indexFile.replace('{templates}', mainTemplates + pluginTemplates);
             fs.writeFileSync(DIST_WEBROOT + '/index.html', indexFile);
             callback();
         });
     });
 };

/**
 * Compile SCSS to CSS.
 */
const distStyles = function() {
    return gulp.src('styles/default.scss')
        .pipe(sass())
        .pipe(gulp.dest(DIST_WEBROOT));
};

/**
 * Creates info.json.
 */
const distInfo = function(callback) {
    var info = createInfo(function(err, data) {
        fs.writeFileSync(DIST_WEBROOT + '/' + INFO_FILE, JSON.stringify(data, null, 4));
        callback();
    });
};

/**
 * Copy to dist.
 */
const distCopy = function() {
    return gulp.src([RESOURCES_DIRECTORY + '/*', CONFIGURATION_FILE, PACKAGE_FILE], {base: './'})
               .pipe(gulp.dest(DIST_WEBROOT));
};

const dist = gulp.series(
    pluginsImport,
    distMkdir,
    distConfig,
    gulp.parallel(
        distCopy,
        distTemplates,
        distStyles,
        distInfo
    ),
    function(callback) {
        webpack(webpackConfig, callback);
    });

////////////////////////////////////////////////////////////////////////////////
// UTILITIES
////////////////////////////////////////////////////////////////////////////////
/**
 * Returns '<script>'-enclosed templates to be placed in index.html.
 */
function buildTemplates(directory, ignoreArray, callback)
{
    recread(directory, ignoreArray, function(err, files)
    {
        var templates = '';
        for (var index in files)
        {
            var filename = files[index];
            var templateName = filename.substring(filename.lastIndexOf('/') + 1);
            templateName = templateName.substring(0, templateName.length - 5);
            var data = fs.readFileSync(files[index], 'utf8');
            templates += '<script type="text/template" id="' + templateName + '">';
            templates += data;
            templates += '</script>';
        }
        callback(null, templates);
    });
}

/**
 * Creates data for info.json.
 */
function createInfo(callback)
{
    var json = require('./' + PACKAGE_FILE);
    var info = {CLIENT: json};
    callback(null, info);
}

/**
 * Reads config file to determine which plugins should be included.
 */
function getPluginList()
{
    var pluginsInclusionFile = path.resolve(__dirname, + '/' + PLUGINS_INCLUSION_FILE);
    try
    {
        var plugins = require(pluginsInclusionFile);
        return Object.keys(plugins);
    }
    catch (error)
    {
        return [];
    }
}

exports.develop = develop;
exports.dist = dist;
exports.clean = gulp.parallel(distClean, developClean);
exports.default = develop;
