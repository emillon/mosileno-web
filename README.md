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

Install the package

    python setup.py develop

Configure rabbitmq (as root)

    rabbitmqctl add_user mosileno mosileno
    rabbitmqctl add_vhost mosilenovhost
    rabbitmqctl set_permissions -p mosilenovhost mosileno ".*" ".*" ".*"

Populate the database

    initialize_mosileno_db development.ini

Boot celery workers

    pceleryd development.ini

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

[Celery Flower]: https://github.com/mher/flower

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

## Rules of thumb

  - Travis is always right.
  - `pep8` is often right.
  - tests are your friends.
  - If you don't write tests, you're making Travis lie to you.
  - If you love Travis (you should), you should feel bad not writing tests.

[Github flow]: http://scottchacon.com/2011/08/31/github-flow.html
