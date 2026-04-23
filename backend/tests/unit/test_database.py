from sqlalchemy.orm import Session

from app.database import get_db


def test_get_db_yields_session():
    gen = get_db()
    db = next(gen)
    assert isinstance(db, Session)
    try:
        next(gen)
    except StopIteration:
        pass


def test_get_db_generator_is_exhausted_after_one_yield():
    gen = get_db()
    db = next(gen)
    assert db is not None
    exhausted = False
    try:
        next(gen)
    except StopIteration:
        exhausted = True
    assert exhausted
