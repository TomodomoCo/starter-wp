const _ = require('lodash')

// Set the defaults
const defaults = {
  watch: true,
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
          },
        },
      },
    ],
  },
  externals: {
    jquery: 'jQuery',
  },
  output: {
    filename: 'script.js',
  },
}

// Build the whole config
const config = {
  dev: _.defaults(
    {
      mode: 'development',
      watch: true,
      stats: {
        colors: true,
      },
      devtool: 'source-map',
    },
    defaults
  ),
  production: _.defaults(
    {
      mode: 'production',
      watch: false,
    },
    defaults
  ),
}

module.exports = config
