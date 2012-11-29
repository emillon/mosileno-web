# ⠋ More Signal - Less Noise ⣠ [![Build Status](https://secure.travis-ci.org/emillon/mosileno-web.png)](http://travis-ci.org/emillon/mosileno-web)

## Installation

First, you'll need the following depencies installed on your OS :

  - python (+ dev package)
  - libxml2 (+ dev package)
  - libxslt (+ dev package)
  - rabbitmq

To setup mosileno :

Clone this

    git clone https://github.com/emillon/mosileno-web.git

Create a virtualenv

    virtualenv ~/.virtualenvs/mosileno

Activate it

    . ~/.virtualenvs/mosileno/bin/activate

Install the dependencies

    pip install -r requirements.txt

Download the topic model file (s.a. hn.ldamodel or hn\_lemmatized.ldamodel):

    mkdir topic-model
    curl -O https://dl.dropbox.com/u/14035465/hn_lemmatized.ldamodel
    mv *.ldamodel topic-model/

Install the package

    python setup.py develop

Configure rabbitmq (as root)

    rabbitmqctl add_user mosileno mosileno
    rabbitmqctl add_vhost mosilenovhost
    rabbitmqctl set_permissions -p mosilenovhost mosileno ".*" ".*" ".*"

Populate the database

    initialize_mosileno_db development.ini

Boot celery workers

    pceleryd development.ini --autoreload

Run the dev server

    pserve --reload development.ini

That's it ! The app should be live at <http://localhost:6543/>.

## Monitoring

You can monitor the state of queues with [Celery flower]. To do that, just
install it in your virtualenv :

    pip install flower

And run it with :

    celery flower

It will be accessible at <http://localhost:5555/>.

It's also possible to monitor the queues using the builtin [celeryev] ncurses
monitor :

    pceleryev development.ini

[Celery Flower]: https://github.com/mher/flower
[celeryev]:      https://celery.readthedocs.org/en/release21-maint/_images/celeryevshotsm.jpg

## Dev guide

The dev process is heavily inspired from [Github flow], ie :

  - `master` is always deployable
  - do feature branches

So, when developing a new feature :

  - branch off `master`
  - hack
  - commit often (in logical commits)
  - it's ok if you push a feature branch where tests break
  - when you're ready to merge, merge `master` INTO the branch and push
  - when Travis is OK, you're ready to merge :
      - ensure that you're up to date (git fetch)
      - `git checkout master`
      - `git merge --ff $FEATURE`
      - `git push origin master :$FEATURE` (`:branch` deletes the remote branch)
      - `git branch -d $FEATURE`
  - if the push is rejected because someone pushed in the meantime, don't merge
    directly on master. Reset the feature branch, merge master into it and push
    to travis

Ideally, the merge is done after a pull request for code review.

[Github flow]: http://scottchacon.com/2011/08/31/github-flow.html

## Rules of thumb

  - Travis is always right.
  - `pep8` is often right.
    - except with SQLAlchemy. Add `--ignore E711` to disable checking
      comparisons to `None`.
  - tests are your friends.
  - If you don't write tests, you're making Travis lie to you.
  - If you love Travis (you should), you should feel bad not writing tests.

## Howto setup a DB migration

You'll need `alembic` (in requirements.txt). Its
[tutorial](http://alembic.readthedocs.org/en/latest/tutorial.html) is great.

### Yes, there are two paths you can go by

Two migration types are possible : non-automatic and automatic ones. In
non-automatic ones, you have to manually define the `upgrade` and `downgrade`
functions.

But for simple cases (mostly {table, column} {addition, removal} - see
tutorial), `alembic` can automatically detect changes to the model and generate
a script.

### Non-automatic migrations

    alembic revision -m $description

And edit `scripts/versions/$id_$description`.

You also have to edit `models.py`, but it's an independent step.

### Automatic migrations

Begin by editing `models.py`.

    alembic revision --autogenerate -m $description

What `alembic` will do is compare the models to the live DB, and generate a
script. Verify it and you're done.

### Running migrations

    alembic upgrade head

## Documentation

  - [pyramid](http://pyramid.rtfd.org)
  - [celery](http://celery.rtfd.org)
  - [colander](http://colander.rtfd.org)
  - [deform](http://deform.rtfd.org)
  - [pyramid_deform](http://pyramid_deform.rtfd.org)
  - [alembic](http://alembic.rtfd.org)
