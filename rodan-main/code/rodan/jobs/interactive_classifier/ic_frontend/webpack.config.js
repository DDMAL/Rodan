"use strict";

var path = require('path'),
    webpack = require('webpack'),
    yargs = require('yargs').argv;

var APP_BASE_DIR = path.resolve(__dirname, 'public/js'),
    APP_DIR = path.resolve(APP_BASE_DIR, 'app'),
    LIB_DIR = path.resolve(__dirname, 'public/node_modules'),
    TMP_DIR = path.resolve(__dirname, '.tmp');

/**
 * Return the absolute path to a library file
 *
 * @param lib
 * @returns {string}
 */
function libPath(lib)
{
    return path.resolve(LIB_DIR, lib);
}

function configureBuildMode(config)
{
    if (yargs.release)
    {
        config.plugins.push(new webpack.optimize.UglifyJsPlugin({
            compress: {
                warnings: false
            }
        }));
    }
    else
    {
        config.devtool = 'cheap-module-source-map';
    }

    return config;
}

module.exports = configureBuildMode({
    context: APP_DIR,

    entry: {
        classifier: './init/Init.js',
        'classifier-static': './init/StaticFile.js'
    },

    output: {
        filename: '[name].min.js',
        chunkFilename: 'classifier.chunk.[id].min.js',
        path: path.resolve(__dirname, '../static/js/compiled/'),
        publicPath: '/static/js/app/'
    },

    resolve: {
        root: [APP_DIR, LIB_DIR, TMP_DIR],

        alias: {
            marionette: 'backbone.marionette',

            // Alias the Diva path to make it easier to access the plugins, etc.
            diva: "diva.js/source/js"
        }
    },

    module: {
        loaders: [
            {
                test: /\.js$/,
                include: [APP_BASE_DIR],
                loader: 'babel-loader'
            },

            {
                test: /\.template\.html$/,
                include: [APP_BASE_DIR],
                loader: 'underscore-template-loader?engine=underscore'
            },

            // Export the Diva global, which for mysterious
            // reasons is defined in the utils file
            {
                include: [libPath('diva.js/source/js/utils.js')],
                loader: 'exports?diva'
            },

            // Import and re-export the Diva global from the diva.js file
            {
                include: [libPath('diva.js/source/js/diva.js')],
                loaders: ['imports?diva=./utils', 'exports?diva']
            }
        ]
    },

    plugins: [
        // Inject globals that Diva relies on. While this plugin applies
        // globally, ESLint should ensure that these aren't injected in
        // app code.
        new webpack.ProvidePlugin({
            diva: 'diva',
            jQuery: 'jquery',
            'window.jQuery': 'jquery',
            $: 'jquery'
        }),

        // Resolve main files which differ from the package.json entries
        new webpack.ResolverPlugin([
            // Bootstrap only has a main entry for jspm
            new webpack.ResolverPlugin.FileAppendPlugin(['/dist/js/bootstrap.js']),

            // We've aliased Diva's path so there's no main to look for
            new webpack.ResolverPlugin.FileAppendPlugin(['/diva.js'])
        ])
    ]
});
