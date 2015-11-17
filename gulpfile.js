var gulp  = require('gulp');
var gutil = require('gulp-util');

var autoprefixer   = require('gulp-autoprefixer');
var compass        = require('gulp-compass');
var concat         = require('gulp-concat');
var imagemin       = require('gulp-imagemin');
var livereload     = require('gulp-livereload');
var mainBowerFiles = require('main-bower-files');
var minifyCSS      = require('gulp-minify-css');
var plumber        = require('gulp-plumber');
var uglify         = require('gulp-uglify');

var dev = 'app/assets/';
var pub = 'public/assets/';

/**
 * Define paths
 */
var paths = {
	dev: {
		fonts:            dev + 'fonts/**',
		images:           dev + 'images/**/*',
		javascripts:      dev + 'javascripts',
		javascripts_all: [dev + 'javascripts/*', dev + 'javascripts/**'],
		sass:             dev + 'sass',
		sass_all:        [dev + 'sass/*', dev + 'sass/**']
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
		.pipe( minifyCSS() )
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
		paths.dev.javascripts + '/script.js'
	])
		.pipe( concat( 'script.js' ) )
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
 * Watch for changes
 */
gulp.task('watcher', function() {

	livereload.listen();

	gulp.watch(paths.dev.sass_all, ['css']);
	gulp.watch(paths.dev.javascripts_all, ['js']);
	gulp.watch(paths.dev.images, ['images']);

});

/**
 * Set up default tasks
 */
gulp.task('default', ['images', 'js', 'css']);

gulp.task('watch', ['default', 'watcher']);
