const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const FileManagerPlugin = require('filemanager-webpack-plugin');

module.exports = {
  mode: 'development',
  entry: ['babel-polyfill', './src/index.js'],
  output: {
    path: path.resolve(__dirname, 'public'),
    filename: 'app.js',
    publicPath: '/'
  },
  plugins: [
    new HtmlWebpackPlugin({
      inject: true,
      template: './src/index.html'
    }),
    new FileManagerPlugin({
        onEnd: {
          copy: [
            { source: './public/app.js', destination: '../../static/moderation/moderator-api/app.js' },
          ],
        }
    })
  ],
  module: {
    rules: [
      {
        test: /\.js?$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            cacheDirectory: true,
            babelrc: false,
            presets: [['env', { targets: { browsers: ['last 2 versions'] } }]]
          },
        },
      },
      {
          test:/\.css$/,
          use:['style-loader','css-loader']
      },
      {
        test: /\.svelte$/,
        exclude: /node_modules/,
        use: {
          loader: 'svelte-loader',
          options: {
            cascade: false
          }
        }
      }
    ]
  }
};
