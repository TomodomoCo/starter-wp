/**
 * Load Gulp and Gulp-adjacent dependencies
 */
var gulp           = require('gulp')
var gutil          = require('gulp-util')
var concat         = require('gulp-concat')
var cssnano        = require('gulp-cssnano')
var imagemin       = require('gulp-imagemin')
var mainBowerFiles = require('main-bower-files')
var sass           = require('gulp-sass')
var sassAssetFuncs = require('node-sass-asset-functions')
var sassglob       = require('gulp-sass-glob')
var svgo           = require('gulp-svgo')
var svgSprite      = require('gulp-svg-sprite')
var uglify         = require('gulp-uglify')

/**
 * Sass to CSS compilation, minification, and prefixing
 */
gulp.task('css', function() {
  gulp.src('app/assets/sass/*.scss')
    .pipe(sassglob())
    .pipe(sass({
      functions: sassAssetFuncs({
        'images_path': 'public/assets/img/',
        'http_images_path': '/assets/img/',
        'fonts_path': 'public/assets/fonts/',
        'http_fonts_path': '/assets/fonts/',
      }),
      includePaths: [
        './vendor/bower_components',
        './vendor/bower_components/breakpoint-sass/stylesheets'
      ]
    }).on('error', sass.logError))
    .pipe(cssnano({
      autoprefixer: {
        browsers: ['last 2 versions'],
        cascade: false
      },
      discardComments: {
        removeAll: true
      },
      zindex: false,
    }))
    .pipe(gulp.dest('public/assets/css/'))
})

/**
 * Font placement
 */
gulp.task('fonts', function () {
  gulp.src('app/assets/fonts/**/*')
    .pipe(gulp.dest('public/assets/fonts/'))
})

/**
 * Image minification
 */
gulp.task('images', function () {
  gulp.src('app/assets/images/**/*')
    .pipe(imagemin({
      progressive: true,
      multipass: true
    }))
    .pipe(gulp.dest('public/assets/images/'))
})

/**
 * Spritify SVGs
 */
gulp.task('sprites', function () {
  gulp.src('app/assets/sprites/**/*.svg')
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
gulp.task('svg', function () {
  gulp.src('app/assets/svg/**/*.svg')
    .pipe(svgo())
    .pipe(gulp.dest('public/assets/img'))
})

/**
 * JavaScript compilation
 */
gulp.task('js', function () {
  /**
   * Default function for compiling JS
   *
   * @param source
   * @param filename
   */
  function jsCompile(source, filename) {
    return gulp.src(source)
      .pipe(concat(filename))
      .on('error', gutil.log)
      .pipe(uglify())
      .on('error', gutil.log)
      .pipe(gulp.dest('public/assets/js/'))
  }

  // libraries.js
  jsCompile(mainBowerFiles({
    paths: {
      bowerDirectory: 'vendor/bower_components'
    },
    filter: /\.js$/i
  }), 'libraries.js')

  // script.js
  jsCompile([
    'app/assets/javascripts/script.js',
  ], 'script.js')
})

/**
 * Watch filesystem for changes
 */
gulp.task('watcher', function () {
  gulp.watch('app/assets/sass/**/*.scss',      ['css'])
  gulp.watch('app/assets/fonts/**/*',          ['fonts'])
  gulp.watch('app/assets/images/**/*',         ['images'])
  gulp.watch('app/assets/javascripts/**/*.js', ['js'])
  gulp.watch('app/assets/sprites/**/*.svg',    ['sprites'])
  gulp.watch('app/assets/svg/**/*.svg',        ['svg'])
})

/**
 * Set up default task
 */
gulp.task('default', [
  'images',
  'sprites',
  'svg',
  'js',
  'fonts',
  'css',
])

/**
 * Set up watch task
 */
gulp.task('watch', [
  'default',
  'watcher'
])
