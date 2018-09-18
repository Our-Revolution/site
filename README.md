# Our Revolution

## Prerequisites

1. [Python 2.7](https://www.python.org/downloads/) and [Pip](https://pip.pypa.io/en/stable/installing/)
2. Postgres — I recommend Homebrew: `brew install postgres` (see [http://brew.sh/](http://brew.sh/)) but [other options are available](https://www.postgresql.org/download/macosx/)
3. [Node + NPM](https://nodejs.org/en/download/) for building front-end.
4. [gulp-cli](https://gulpjs.com/) installed globally: `npm install gulp-cli -g`
5. For features with asynchronous task handling, install [Redis](https://redis.io/) and start server `redis $ src/redis-server`

## Installation
Because 'site' is not a descriptive project name ...

1. `cd` into your typical project directory; `~/sites/` or `~/code` or `~/projects` or what have you.

2. Clone this repo — `git clone git@github.com:Our-Revolution/site.git our-revolution`

3. `cd our-revolution`

4. Run `./setup-osx` (it will take a minute; it's making a number of installs HTTP requests)

If db connection throws authentication error, try updating `.env` db url config
to be `postgres:///ourrevolution` [without host and port](https://www.peterbe.com/plog/connecting-with-psycopg2-without-a-username-and-password).

If `.env` keys are not generated correctly try updating script with something
like this:
```
echo "SECRET_KEY=lebowski" >> .env
echo "AUTH0_DOMAIN=lebowski" >> .env
echo "AUTH0_CLIENT_ID=lebowski" >> .env
echo "AUTH0_CLIENT_SECRET=lebowski" >> .env
echo "AUTH0_CANDIDATE_CALLBACK_URL=lebowski" >> .env
```

There is a known migration bug as of 2017-09-18.

5. It should prompt you to create a super user account. Enter your username, email and password.

6. `npm install` for build tools

7. ???

8. Profit!

## Usage

1. `workon ourrevolution` or `source ~/.virtualenvs/ourrevolution/bin/activate`
2. `./manage.py runserver` then pull up http://localhost:8000/ and you're off to the races.
3. For features with asynchronous task handling, start a [Celery](http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html#starting-the-worker-process) worker `(ourrevolution) $ celery -A ourrevolution worker -l info`
 - Locally does not work well with `.env` config pattern, might need to export variables some other way. Celery needs to be restarted to see app changes. If configs are not taking hold, make sure you are exporting them in the same scope that celery is being run in.


If pages don't load correctly you may need to update the `django_site` table:
```
INSERT INTO django_site (domain, name) VALUES ('localhost:8000', 'Our Rev Dev');
```

## GULP and the Front End
We use [gulp](http://gulpjs.com/) to automate building and minifying of production files.

The default gulp task runs with `gulp build --production`. It does the following:
1. Compiles, minifies, auto-prefixes, and gzips SASS from `ourrevolution/pages/src/scss/main.scss`.
2. Builds and minifies JS from `ourrevolution/pages/src/js/app.js` with the help of [browserify](http://browserify.org/).
3. Watches project files to recompile SASS, JS, optimize images, and live reload the browser on the fly.

__Note__: For live reloading, install the [Live Reload Chrome extension](https://chrome.google.com/webstore/detail/livereload/jnihajbhpnppcggbcgedagnkighmdlei).
