from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from models import Base, User
from utils import update_user_tracking_info

# db initialisation
engine = create_engine('sqlite:///sqlite.db', echo=True, future=True)
Base.metadata.create_all(engine)


def test_sql_db_update():
    start = (datetime.today() - timedelta(days=120))
    end = datetime.today()
    with Session(engine) as session:
        # Make if enry is already in db -> skip that
        user = User(name='testuser')
        session.add(user)
        session.commit()
        user = session.query(User).get(1)
        update_user_tracking_info(session, start, end, user)


def main():
    pass


if __name__ == '__main__':
    main()
