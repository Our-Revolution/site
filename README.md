# Our Revolution

## Prerequisites

1. Pip https://pip.pypa.io/en/stable/installing/
2. Postgres — I recommend Homebrew: `brew install postgres` (see http://brew.sh/) but other options are available https://www.postgresql.org/download/macosx/

## Installation
Because 'site' is not a descriptive project name ...

1. `cd` into your typical project directory; `~/sites/` or `~/code` or `~/projects` or what have you.
2. Clone this repo — `git clone git@github.com:Our-Revolution/site.git our-revolution`
3. `cd our-revolution`
4. Run `./setup-osx` (it will take a minute; it's making a number of installs HTTP requests)
5. It should prompt you to create a super user account. Enter your username, email and password.
6. ???
7. Profit!

## Usage

1. `source ~/.virtualenvs/ourrevolution/bin/activate`
2. `./manage.py runserver` then pull up http://localhost:8000/ and you're off to the races.
