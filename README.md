# Our Revolution

## Prerequisites

1. [Pip](https://pip.pypa.io/en/stable/installing/)
2. Postgres — I recommend Homebrew: `brew install postgres` (see [http://brew.sh/](http://brew.sh/)) but [other options are available](https://www.postgresql.org/download/macosx/)
3. [Node + NPM](https://nodejs.org/en/download/) for building front-end. 

## Installation
Because 'site' is not a descriptive project name ...

1. `cd` into your typical project directory; `~/sites/` or `~/code` or `~/projects` or what have you.
2. Clone this repo — `git clone git@github.com:Our-Revolution/site.git our-revolution`
3. `cd our-revolution`
4. Run `./setup-osx` (it will take a minute; it's making a number of installs HTTP requests)
5. It should prompt you to create a super user account. Enter your username, email and password.
6. `npm install` for build tools
7. ???
8. Profit!

## Usage

1. `workon ourrevolution` or `source ~/.virtualenvs/ourrevolution/bin/activate`
2. `./manage.py runserver` then pull up http://localhost:8000/ and you're off to the races.

## GULP and the Front End
We use [gulp](http://gulpjs.com/) to automate building and minifying of production files.

The default gulp task runs with `./manage.py runserver` with the help of [django-gulp](https://pypi.python.org/pypi/django-gulp/2.0.0). It does the following:
1. Compiles, minifies, auto-prefixes, and gzips SASS from `ourrevolution/pages/src/scss/main.scss`.
2. Builds and minifies JS from `ourrevolution/pages/src/js/app.js` with the help of [browserify](http://browserify.org/).
3. Watches project files to recompile SASS, JS, optimize images, and live reload the browser on the fly.

__Note__: For live reloading, install the [Live Reload Chrome extension](https://chrome.google.com/webstore/detail/livereload/jnihajbhpnppcggbcgedagnkighmdlei).
