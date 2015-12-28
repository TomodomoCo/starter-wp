/**
 * Load Gulp and Gulp-adjacent dependencies
 */
var gulp           = require( 'gulp' ),
    gutil          = require( 'gulp-util' ),
    compass        = require( 'gulp-compass' ),
    concat         = require( 'gulp-concat' ),
    exec           = require( 'gulp-exec' ),
    imagemin       = require( 'gulp-imagemin' ),
    livereload     = require( 'gulp-livereload' ),
    mainBowerFiles = require( 'main-bower-files' ),
    cssnano        = require( 'gulp-cssnano' ),
    plumber        = require( 'gulp-plumber' ),
    uglify         = require( 'gulp-uglify' )
    ;

/**
 * Define paths
 */
var src  = 'app/assets/',
    dest = 'public/assets/'
    ;

var paths = {
  src: {
    fonts:       src + 'fonts/**/*',
    images:      src + 'images/**/*',
    javascripts: src + 'javascripts',
    sass:        src + 'sass'
  },
  dest: {
    css:         dest + 'css/',
    fonts:       dest + 'fonts/',
    images:      dest + 'img/',
    javascripts: dest + 'js/'
  }
};

/**
 * CSS tasks
 */
gulp.task( 'css', function() {

  return gulp.src( paths.src.sass + '/*.scss' )
    .pipe( plumber({
      errorHandler: function (error) {
        console.log( error.message );
        this.emit( 'end' );
      }
    }) )
    .pipe( compass({
      sass:  paths.src.sass,
      css:   paths.dest.css,
      image: paths.dest.images,
      font:  paths.dest.fonts,
      require: [
        'breakpoint',
        'sass-globbing',
        'compass-normalize'
      ],
      import_path: [
        'vendor/bower_components'
      ],
      bundle_exec: true
    }) )
    .on('error', gutil.log)
    .pipe( cssnano({
      autoprefixer: {
        browsers: ['last 2 versions'],
        cascade: false
      },
      discardComments: {
        removeAll: true
      }
    }) )
    .pipe( gulp.dest( paths.dest.css ) )
    .pipe( livereload() );

} );

/**
 * JavaScript tasks
 */
gulp.task( 'javascripts', function() {

  /**
   * Default function for compiling JS
   *
   * @param source
   * @param filename
   */
  function compileJavaScripts( source, filename ) {
    return gulp.src( source )
             .pipe( concat( filename ) )
             .on( 'error', gutil.log )
             .pipe( uglify() )
             .on( 'error', gutil.log )
             .pipe( gulp.dest( paths.dest.javascripts ) )
             .pipe( livereload() )
             ;
  }

  /**
   * libraries.js
   */
  compileJavaScripts( mainBowerFiles({
    paths: {
      bowerDirectory: 'vendor/bower_components'
    },
    filter: /\.js$/i
  }), 'libraries.js' );

  /**
   * script.js
   */
  compileJavaScripts( [
    paths.src.javascripts + '/script.js',
  ], 'script.js' );

} );

/**
 * Images
 */
gulp.task( 'images', function () {

  gulp.src( paths.src.images )
    .pipe( imagemin({
      progressive: true,
      multipass: true
    }) )
    .pipe( gulp.dest( paths.dest.images ) )
    .pipe( livereload() );

} );

/**
 * Clean out compiled static assets
 */
gulp.task( 'clean', function() {

  gulp.src('').pipe( exec( 'rm -rf <%= options.dest %>', { dest: dest } ) );

} );

/**
 * Watch for changes and automatically reload the browser
 */
gulp.task( 'watcher', function() {

  // Activate LiveReload's listener
  livereload.listen();

  // Watch src paths and execute callback tasks as necessary
  gulp.watch( paths.src.sass + '/**/*',        ['css'] );
  gulp.watch( paths.src.javascripts + '/**/*', ['js'] );
  gulp.watch( paths.src.images,                ['images'] );

} );

/**
 * Set up default task
 */
gulp.task( 'default', [
  'images',
  'javascripts',
  'css'
] );

/**
 * Set up watch task
 */
gulp.task( 'watch', [
  'default',
  'watcher'
] );
