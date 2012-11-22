import bcrypt
import transaction

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


def update_password(login, oldpass, newpass):
    ok = auth_correct(login, oldpass)
    if ok:
        user = DBSession.query(User).filter(User.name == login).one()
        old_hash = user.password
        new_hash = bcrypt.hashpw(newpass, old_hash)
        user.password = new_hash
        transaction.commit()
    return ok
