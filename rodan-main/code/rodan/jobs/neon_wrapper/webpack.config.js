const path = require("path");
const webpack = require("webpack");
const childProcess = require('child_process');

let commitHash = childProcess.execSync('(cd Neon && git rev-parse --short HEAD)').toString();

module.exports = {
    mode: "production",
    entry: {
        editor: "./editor.ts",
    },
    output: {
        path: path.resolve(__dirname, "static", "Neon"),
        filename: "[name].js"
    },
    node: {
        fs: 'empty'
    },
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: [
                    'awesome-typescript-loader'
                ],
                exclude: /node_modules/
            },
            {
                test: /Worker\.js/,
                use: [
                    {
                      loader: 'worker-loader',
                    }
                ]
            }
        ]
    },
    externals: {
        'verovio-dev': 'verovio',
        d3: 'd3'
    },
    resolve: {
      extensions: [ '.ts', '.js' ]
    },
    plugins: [
        new webpack.DefinePlugin({
            __LINK_LOCATION__: JSON.stringify('#'),
            __NEON_VERSION__: JSON.stringify('Commit ' + commitHash),
            __ASSET_PREFIX__: JSON.stringify('Neon/')
        })
    ]
};
