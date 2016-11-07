var gulp = require('gulp'),
  livereload = require('gulp-livereload'),
  sass = require('gulp-sass'),
  imagemin = require('gulp-imagemin'),
  autoprefixer = require('gulp-autoprefixer'),
  sourcemaps = require('gulp-sourcemaps'),
  watch = require('gulp-watch'),
  minifycss = require('gulp-minify-css'),
  uglify = require('gulp-uglify'),
  rename = require('gulp-rename'),
  gzip = require('gulp-gzip'),
  changed = require('gulp-changed'),
  watchify = require('watchify'),
  browserify = require('browserify'),
  source = require('vinyl-source-stream'),
  buffer = require('vinyl-buffer'),
  gutil = require('gulp-util'),
  _ = require('lodash'),
  gulpcopy = require('gulp-copy'),
  exit = require('gulp-exit');

var gzipOptions = {
    threshold: '1kb',
    gzipOptions: {
        level: 9
    }
};

/* Browserify config */
var browserifyOptions = {
  entries: ['pages/static/src/js/app.js'],
  debug: true
}
var opts = _.assign({}, watchify.args, browserifyOptions);
var b = watchify(browserify(opts));

gulp.task('js', bundle); // so you can run `gulp js` to build the file
// b.on('update', bundle); // on any dep update, runs the bundler
b.on('log', gutil.log); // output build logs to terminal

// Compile JS, minify
function bundle() {
  return b.bundle()
    // log errors if they happen
    .on('error', gutil.log.bind(gutil, 'Browserify Error'))
    .pipe(source('bundle.js'))
    // optional, remove if you don't need to buffer file contents
    .pipe(buffer())
    .pipe(uglify())
    .pipe(rename({suffix: '.min'}))
    // optional, remove if you dont want sourcemaps
    .pipe(sourcemaps.init({loadMaps: true})) // loads map from browserify file
     // Add transformation tasks to the pipeline here.
    .pipe(sourcemaps.write('./')) // writes .map file
    .pipe(gulp.dest('pages/static/dist/js'))
    .pipe(livereload())
    .pipe(exit());
}

/* Compile SASS */
gulp.task('sass', function() {
  return gulp.src('pages/static/src/scss/main.scss')
  .pipe(sass().on('error', sass.logError))
  .pipe(sourcemaps.write())
  .pipe(autoprefixer({
      browsers: ['last 2 versions','iOS 7', 'iOS 8', 'ie 9-11', 'android 4.3'],
      cascade: false
  }))
  .pipe(gulp.dest('pages/static/dist/css'))
  .pipe(livereload())
  .pipe(minifycss())
  .pipe(rename({suffix: '.min'}))
  .pipe(gulp.dest('pages/static/dist/css'))
  .pipe(gzip(gzipOptions))
  .pipe(gulp.dest('pages/static/dist/css'))
  .pipe(livereload());
});

/* Optimize Images */
gulp.task('images', function() {
  return gulp.src('pages/static/src/img/**/*.{jpg,png,svg}')
    .pipe(changed('pages/static/dist/img/'))
    .pipe(imagemin())
    .pipe(gulp.dest('pages/static/dist/img/'))
});

/* Copy Fonts to Dist */
gulp.task('fonts', function() {
  return gulp.src('pages/static/src/fonts/**/*')
    .pipe(gulp.dest('pages/static/dist/fonts'))
})

/* Watch Files For Changes and Live Reload Browser */
gulp.task('watch', function() {
    livereload.listen();

    /* Trigger SASS and a live reload on SCSS changes */
    gulp.watch('pages/static/src/scss/**/*.scss', {interval: 500}, ['sass']);

    /* Trigger imagemin and live reload on image changes */
    gulp.watch('pages/static/src/img/**/*', {interval: 500}, ['images']);

    /* Trigger browserify and live reload on JS changes */
    gulp.watch('pages/static/src/js/**/*', {interval: 500}, ['js']);

    /* Trigger a live reload on any Django template changes */
    gulp.watch('**/templates/*', {interval: 500}).on('change', livereload.changed);

});

gulp.task('build', ['sass', 'js', 'images', 'fonts']);
gulp.task('default', ['sass', 'js', 'watch']);
