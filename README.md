# ⠋ More Signal - Less Noise ⣠
[![Build Status](https://secure.travis-ci.org/emillon/mosileno-web.png)](http://travis-ci.org/emillon/mosileno-web)

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
