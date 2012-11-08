import bcrypt

from sqlalchemy.orm.exc import NoResultFound
from .models import (
    DBSession,
    User
)


def auth_correct(login, password):
    try:
        user = DBSession.query(User).filter(User.name == login).one()
    except NoResultFound:
        return False
    db_hash = user.password
    hashed = bcrypt.hashpw(password, db_hash)
    return db_hash == hashed
