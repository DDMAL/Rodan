"use strict";

module.exports = function (config)
{
    var path = require('path'),
        _ = require('underscore'),
        webpack = require('webpack'),
        generalWebpackConfig = require('./webpack.config');

    var webpackConfig = _.defaults({
        devtool: 'inline-source-map',

        // Hack to let .tmp/templates be built
        bundleDelay: 1000,

        plugins: generalWebpackConfig.plugins.concat([
            new webpack.optimize.LimitChunkCountPlugin({
                maxChunks: 1
            })
        ])
    }, generalWebpackConfig);

    // Support the "test" module
    webpackConfig.resolve.alias.test = path.resolve(__dirname, 'public/js/test');

    // Delete the entry point; this will be set dynamically
    delete webpackConfig.entry;

    config.set({
        browsers: ['PhantomJS'],
        files: ['public/js/**/*.spec.js'],
        frameworks: ['jasmine-jquery', 'jasmine-ajax', 'jasmine'],

        preprocessors: {
            'public/js/**/*.js': ['webpack', 'sourcemap']
        },

        webpack: webpackConfig,

        webpackMiddleware: {
            noInfo: true
        }
    });
};