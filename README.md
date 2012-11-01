# ⠋⣠ More Signal. Less Noise.
[![Build Status](https://secure.travis-ci.org/emillon/mosileno-web.png)](http://travis-ci.org/emillon/mosileno-web)

## Installation

First, you'll need the following depencies installed on your OS :

  - python (+ dev package)
  - libxml2 (+ dev package)
  - libxslt (+ dev package)
  - rabbitmq

To setup mosileno :

  - clone this
  - create a virtualenv

    virtualenv ~/.virtualenvs/mosileno

  - activate it

    . ~/.virtualenvs/mosileno/bin/activate

  - install the dependencies

    pip install -r requirements.txt

  - configure rabbitmq (as root) :

    rabbitmqctl add_user mosileno mosileno
    rabbitmqctl add_vhost mosilenovhost
    rabbitmqctl set_permissions -p mosilenovhost mosileno ".*" ".*" ".*"

  - populate the database

    initialize_mosileno_db development.ini

  - boot celery workers

    pceleryd development.ini

  - run the dev server

    pserve --reload development.ini

That's it ! The app should be live at <http://localhost:6543/>.
