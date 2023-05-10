"use strict";

var gulp = require('gulp');
var runSequence = require('run-sequence');
var eslint = require('gulp-eslint');
var jscs = require('gulp-jscs');
var jsdoc = require('gulp-jsdoc3');
var concat = require('gulp-concat');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
var gulpif = require('gulp-if');
var autoprefixer = require('gulp-autoprefixer');
var livereload = require('gulp-livereload');

var lazypipe = require('lazypipe');
var yargs = require('yargs').argv;
var webpack = require('webpack');
var modernizr = require('modernizr');
var del = require('del');
var path = require('path');
var fs = require('fs');
var mkdirp = require('mkdirp');

// Set path variables
var sources = {
    appJS: ['public/js/app/**/*.js', '!public/js/app/**/*.spec.js', 'public/modernizr-config.json'],
    buildJS: ['./*.js'],
    templates: ['public/js/app/**/*.template.html'],
    css: ['public/css/**/*{.css,.scss}'],
    jsdocDest: "../docs/jsdoc"
};

sources.clientJS = ['public/node_modules'].concat(sources.appJS).concat(sources.templates);

var getWebpackCompiler = (function ()
{
    var compiler = null;

    return function ()
    {
        if (!compiler)
            compiler = webpack(require('./webpack.config'));

        return compiler;
    };
})();

/*
 * High-level tasks
 */

gulp.task('default', function (cb)
{
    runSequence(['lint-nofail:js', 'build'], 'watch', cb);
});

gulp.task('build', ['build:js', 'build:css', 'build:jsdoc']);

/*
 * JavaScript linting
 */

gulp.task('lint:js', function ()
{
    return lintJS()
        .pipe(jscs.reporter('fail'))
        .pipe(eslint.failAfterError());
});

gulp.task('lint-nofail:js', function ()
{
    return lintJS();
});

/*
 * JavaScript build tasks
 */

gulp.task('build:js', function (cb)
{
    runSequence(
        'clean:js',
        'bundle:js',
        cb
    );
});

gulp.task('rebuild:js', ['bundle:js']);

gulp.task('bundle:js', ['build:modernizr'], function (cb)
{
    var onBundleComplete = function (err, stats)
    {
        console.log(stats.toString({
            colors: true,
            hash: false,
            version: false
        }));

        if (err)
        {
            cb(err);
        }
        else
        {
            var fullStats = stats.toJson();

            // Reload changed files
            fullStats.assets.filter(function (asset)
            {
                return asset.emitted;
            }).map(function (asset)
            {
                return fullStats.publicPath  + asset.name;
            }).forEach(function (path)
            {
                livereload.changed(path);
            });

            cb();
        }
    };

    getWebpackCompiler().run(onBundleComplete);
});

gulp.task('clean:js', function (done)
{
    del(['../static/js/compiled/', './.tmp'], {force: true}, function (err)
    {
        if (err)
            done(err);
        else
            done();
    });
});

/*
Build JSDocs
 */
gulp.task('build:jsdoc', function(cb)
{
    // Clean the old jsdocs
    runSequence("clean:jsdoc");

    var config = {
        "opts": {
            "template": "templates/default",
            "destination": sources.jsdocDest
        },
        "plugins": ["plugins/markdown"]
    };

    gulp.src(sources.appJS, {read: false})
        .pipe(jsdoc(config, cb));
});

gulp.task('clean:jsdoc', function (done)
{
    del(sources.jsdocDest, {force: true}, function (err)
    {
        if (err)
            done(err);
        else
            done();
    });
});

gulp.task('build:modernizr', function (cb)
{
    //if (!modifiedAfter('.tmp/modernizr.js', ))
    fs.readFile('public/modernizr-config.json', function (err, config)
    {
        if (err)
        {
            cb(err);
            return;
        }

        var json = JSON.parse(config);

        modernizr.build(json, function (result)
        {
            mkdirp('.tmp');

            fs.writeFile('.tmp/modernizr.js', result, function (err)
            {
                if (err)
                    cb(err);
                else
                    cb();
            });
        });
    });
});

/*
 * CSS build tasks
 */

gulp.task('build:css', function (done)
{
    runSequence(
        'clean:css',
        'bundle:css',
        done
    );
});

gulp.task('rebuild:css', ['bundle:css']);

gulp.task('bundle:css', function ()
{
    var sources = [
        './public/css/bootstrap-theme.min.css',
        './public/css/diva.min.css',
        './public/css/styles.scss'
    ];

    var isScssFile = /\.scss$/;
    var isCssFile = /\.css$/;
    var isDevBuild = !yargs.release;

    var compileScss = lazypipe()
        .pipe(function ()
        {
            return sass({outputStyle: 'compressed'}).on('error', sass.logError);
        })
        .pipe(autoprefixer, {browsers: ['> 1%', 'last 2 versions', 'Firefox ESR', 'Opera 12.1', 'ie >= 9']});

    return gulp.src(sources, {base: './public/css/'})
        .pipe(gulpif(isDevBuild, sourcemaps.init()))
        .pipe(gulpif(isScssFile, compileScss()))
        .pipe(concat('classifier.min.css'))
        .pipe(gulpif(isDevBuild, sourcemaps.write('.')))
        .pipe(gulp.dest('../static/css/'))
        .pipe(gulpif(isCssFile, livereload())); // Don't reload for sourcemaps
});

gulp.task('clean:css', function (done)
{
    del('../static/css/', {force: true}, function (err)
    {
        if (err)
            done(err);
        else
            done();
    });
});

/*
 * Watching
 */

gulp.task('watch', function (done) // eslint-disable-line no-unused-vars
{
    // Never call the callback: this runs forever

    // Run the livereload server
    livereload.listen();

    var jsWatcher = gulp.watch(sources.clientJS, ['lint-nofail:js', 'rebuild:js', 'build:jsdoc']);
    var cssWatcher = gulp.watch(sources.css, ['rebuild:css']);

    jsWatcher.on('change', logWatchedChange);
    cssWatcher.on('change', logWatchedChange);
});

/**
 * Output a log message for a gulp.watch event
 *
 * @param ev The change event
 */
function logWatchedChange(ev)
{
    console.log("File '" + path.relative('.', ev.path) + "' was " + ev.type);
}

function lintJS()
{
    var testEslintConfig = {
        configFile: 'public/js/.eslintrc.test.json'
    };

    return gulp.src(sources.buildJS.concat('public/js/**/*.js'))
        .pipe(gulpif((/\.spec\.js$/), eslint(testEslintConfig), eslint()))
        .pipe(eslint.format())
        .pipe(jscs())
        .pipe(jscs.reporter());
}
