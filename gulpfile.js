/**
 * Load Gulp and Gulp-adjacent dependencies
 */
const gulp           = require('gulp')
const gutil          = require('gulp-util')
const concat         = require('gulp-concat')
const cssnano        = require('gulp-cssnano')
const eyeglass       = require('eyeglass')
const imagemin       = require('gulp-imagemin')
const minimist       = require('minimist')
const sass           = require('gulp-sass')
const sassAssetFuncs = require('node-sass-asset-functions')
const sassglob       = require('gulp-sass-glob')
const sourcemaps     = require('gulp-sourcemaps')
const svgo           = require('gulp-svgo')
const svgSprite      = require('gulp-svg-sprite')
const uglify         = require('gulp-uglify')
const webpack        = require('webpack-stream')

var options = minimist(process.argv.slice(2), {
  string: 'env',
  default: {
    env: process.env.NODE_ENV || 'production'
  },
})

/**
 * Sass to CSS compilation, minification, and prefixing
 */
gulp.task('css', () => {
  const sassConfig = {
    functions: sassAssetFuncs({
      'images_path':      'public/assets/img/',
      'http_images_path': '../img/',
      'fonts_path':       'public/assets/fonts/',
      'http_fonts_path':  '../fonts/',
    }),
    includePaths: [
      './node_modules',
    ],
  }

  let stream = gulp.src('app/assets/sass/*.scss')
    .pipe(sassglob())
    .pipe(sourcemaps.init())
    .pipe(sass(eyeglass(sassConfig)).on('error', sass.logError))
    .pipe(cssnano({
      autoprefixer: {
        browsers: ['last 2 versions'],
        cascade: false,
      },
      discardComments: {
        removeAll: true,
      },
      zindex: false,
    }))

  // Write sourcemaps if we're outside of production
  stream = (options.env === 'production')
    ? stream
    : stream.pipe(sourcemaps.write())

  // Write the output
  return stream.pipe(gulp.dest('public/assets/css/'))
})

/**
 * Font placement
 */
gulp.task('fonts', () => {
  return gulp.src('app/assets/fonts/**/*')
    .pipe(gulp.dest('public/assets/fonts/'))
})

/**
 * Image minification
 */
gulp.task('images', () => {
  return gulp.src([
    'app/assets/img/**/*',
    '!app/assets/img/**/*.svg',
  ])
    .pipe(imagemin({
      progressive: true,
      multipass: true,
    }))
    .pipe(gulp.dest('public/assets/img/'))
})

/**
 * Spritify SVGs
 */
gulp.task('sprites', () => {
  return gulp.src('app/assets/sprites/**/*.svg')
    .pipe(svgSprite({
      mode: {
        symbol: true
      }
    }))
    .pipe(gulp.dest('public/assets/sprites'))
})

/**
 * Handle normal SVGs
 */
gulp.task('svg', () => {
  return gulp.src('app/assets/img/**/*.svg')
    .pipe(svgo())
    .pipe(gulp.dest('public/assets/img'))
})

/**
 * JavaScript compilation
 */
gulp.task('js', () => {
  // Grab the config file
  let webpackConfig = require('./webpack.config.js')

  return gulp.src('app/assets/js/index.js')
    .pipe(webpack(webpackConfig[options.env]))
    .pipe(gulp.dest('public/assets/js/'))
})

/**
 * Watch filesystem for changes
 */
gulp.task('watcher', () => {
  const isWatching = true

  gulp.watch('app/assets/sass/**/*.scss',   gulp.parallel('css'))
  gulp.watch('app/assets/fonts/**/*',       gulp.parallel('fonts'))
  gulp.watch('app/assets/img/**/*',         gulp.parallel('images'))
  gulp.watch('app/assets/svg/**/*',         gulp.parallel('svg'))
  gulp.watch('app/assets/sprites/**/*.svg', gulp.parallel('sprites'))
})

/**
 * Set up default task
 */
gulp.task('default', gulp.parallel(
  'images',
  'svg',
  'sprites',
  'js',
  'fonts',
  'css',
))

/**
 * Set up watch task
 */
gulp.task('watch', gulp.parallel(
  'default',
  'watcher',
))
