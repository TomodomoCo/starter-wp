var gulp           = require( 'gulp' ),
    gutil          = require( 'gulp-util' ),
    autoprefixer   = require( 'gulp-autoprefixer' ),
    compass        = require( 'gulp-compass' ),
    concat         = require( 'gulp-concat' ),
    exec           = require( 'gulp-exec' ),
    imagemin       = require( 'gulp-imagemin' ),
    livereload     = require( 'gulp-livereload' ),
    mainBowerFiles = require( 'main-bower-files' ),
    minifyCss      = require( 'gulp-minify-css' ),
    plumber        = require( 'gulp-plumber' ),
    uglify         = require( 'gulp-uglify' )
    ;

/**
 * Define paths
 */
var dev = 'app/assets/',
    pub = 'public/assets/'
    ;

var paths = {
  dev: {
    fonts:       dev + 'fonts/**/*',
    images:      dev + 'images/**/*',
    javascripts: dev + 'javascripts',
    sass:        dev + 'sass'
  },
  pub: {
    css:         pub + 'css/',
    fonts:       pub + 'fonts/',
    images:      pub + 'img/',
    javascripts: pub + 'js/'
  }
};

/**
 * CSS tasks
 */
gulp.task('css', function() {

  return gulp.src(paths.dev.sass + '/*.scss')
    .pipe( plumber({
      errorHandler: function (error) {
        console.log( error.message );
        this.emit( 'end' );
      }
    }) )
    .pipe( compass({
      sass:  paths.dev.sass,
      css:   paths.pub.css,
      image: paths.pub.images,
      font:  paths.pub.fonts,
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
    .pipe( autoprefixer({
      browser: ['last 2 versions'],
      cascade: false
    }) )
    .pipe( gulp.dest( paths.pub.css ) )
    .pipe( minifyCss({
      advanced: false
    }) )
    .pipe( gulp.dest( paths.pub.css ) )
    .pipe( livereload() );

});

/**
 * JS tasks
 */
gulp.task('js', function() {

  /**
   * libraries.js
   */
  gulp.src( mainBowerFiles({
    paths: {
      bowerDirectory: 'vendor/bower_components'
    },
    filter: /\.js$/i
  }) )
    .pipe( concat( 'libraries.js' ) )
    .on( 'error', gutil.log )
    .pipe( uglify() )
    .on( 'error', gutil.log )
    .pipe( gulp.dest( paths.pub.javascripts ) )
    .pipe( livereload() );

  /**
   * script.js
   */
  gulp.src([
    paths.dev.javascripts + '/formGeneric.js',
    paths.dev.javascripts + '/formAsk.js',
    paths.dev.javascripts + '/formPayment.js',
    paths.dev.javascripts + '/formSignup.js',
    paths.dev.javascripts + '/stripeHandler.js',
    paths.dev.javascripts + '/svg.js',
    paths.dev.javascripts + '/tabs.js'
  ])
    .pipe( concat( 'script.js' ) )
    .on( 'error', gutil.log )
    .pipe( uglify() )
    .on( 'error', gutil.log )
    .pipe( gulp.dest( paths.pub.javascripts ) )
    .pipe( livereload() );

  /**
   * login.js
   */
  gulp.src([
    paths.dev.javascripts + '/login.js',
  ])
    .pipe( concat( 'login.js' ) )
    .on( 'error', gutil.log )
    .pipe( uglify() )
    .on( 'error', gutil.log )
    .pipe( gulp.dest( paths.pub.javascripts ) )
    .pipe( livereload() );

});

/**
 * Images
 */
gulp.task('images', function () {

  gulp.src( paths.dev.images )
    .pipe( imagemin({
      progressive: true,
      multipass: true
    }) )
    .pipe( gulp.dest( paths.pub.images ) )
    .pipe( livereload() );

});

/**
 * Clean out old files
 */
gulp.task( 'clean', function() {

  var execOptions = { pub: pub };

  gulp.src('').pipe( exec( 'rm -rf <%= options.pub %>', execOptions ) );

} );

/**
 * Watch for changes
 */
gulp.task( 'watcher', function() {
  // Activate LiveReload's listener
  livereload.listen();

  // Watch dev paths and execute callback tasks as necessary
  gulp.watch( paths.dev.sass + '/**/*', ['css'] );
  gulp.watch( paths.dev.javascripts + '/**/*', ['js'] );
  gulp.watch( paths.dev.images, ['images'] );
} );

/**
 * Set up default task
 */
gulp.task( 'default', [
  'images',
  'js',
  'css'
] );

/**
 * Set up watch task
 */
gulp.task( 'watch', [
  'default',
  'watcher'
] );
