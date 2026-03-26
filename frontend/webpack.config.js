const path = require('path');
const CopyPlugin = require("copy-webpack-plugin");

module.exports = {
    entry: './src/main.js',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'build'),
        clean: true,
    },
    devtool: 'source-map',
    devServer: {
        static: path.join(__dirname, 'public'),
        port: 8080,
        historyApiFallback: true,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
        },
    },
    plugins: [
        new CopyPlugin({
            patterns: [{ from: 'public' }],
        }),
    ],
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /(node_modules)/,
                use: ['babel-loader']
            },
            {
                test: /\.css$/i,
                use: ['style-loader', 'css-loader']
            }
        ]
    }
};
