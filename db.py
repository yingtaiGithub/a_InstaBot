import os
from datetime import date, timedelta, datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

cur_dir = os.path.dirname(__file__)
db_path = os.path.join(cur_dir, 'instabot.db')
Base = declarative_base()
engine = create_engine('sqlite:///%s' % db_path)


def check_existing(table, key):
    attributes = [i for i in table.__dict__.keys() if i[:1] != '_']

    sql_client = Sql_Client()

    return sql_client.session.query(table).filter(getattr(table, attributes[0]) == key).first()


def get_first_row(table):
    sql_client = Sql_Client()

    return sql_client.session.query(table).first()


def get_firstRow_by_primaryKey(table, key):
    attributes = [i for i in table.__dict__.keys() if i[:1] != '_']

    sql_client = Sql_Client()

    return sql_client.session.query(table).filter(getattr(table, attributes[0]) == key).first()


def delete_row(row_object):
    sql_client = Sql_Client()
    sql_client.session.delete(row_object)
    sql_client.session.commit()


def expired_followings(days):
    taken_at = date.today() - timedelta(days=days)
    sql_client = Sql_Client()
    objects = sql_client.session.query(Following).filter(Following.taken_at <= taken_at, Following.checked == 0).all()

    # username_s = [object.userId for object in objects]

    return objects


def friends_for_am():
    sql_client = Sql_Client()
    responses = sql_client.session.query(Response).filter(Response.message_moment < datetime.now()).all()

    return responses


def add_row(table, data):
    sql_client = Sql_Client()
    attributes = [i for i in table.__dict__.keys() if i[:1] != '_']
    row = sql_client.session.query(table).filter_by(username=data[0]).first()

    if row:
        for attribute, value in zip(attributes, data):
            setattr(row, attribute, value)

        sql_client.session.commit()

    else:
        obj = table()
        for attribute, value in zip(attributes, data):
            setattr(obj, attribute, value)

        sql_client.session.add(obj)
        sql_client.session.commit()


def noResponse_checking(username):
    sql_client = Sql_Client()
    object = sql_client.session.query(NoResponse).filter(NoResponse.username == username).first()

    return object


class Sql_Client():
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()


class Following(Base):
    __tablename__ = 'following'
    username = Column(String(250), primary_key=True)
    userId = Column(Integer, nullable=False)
    taken_at = Column(Date, nullable=False)
    checked = Column(Boolean, nullable=False)


class Response(Base):
    __tablename__ = 'response'
    username = Column(String(250), primary_key=True)
    userId = Column(Integer, nullable=False)
    message_moment = Column(DateTime, nullable=False)


class NoResponse(Base):
    __tablename__ = 'no_response'
    username = Column(String(250), primary_key=True)


# class Profile(Base):
#     __tablename__ = 'checked_profile'
#     profile_name = Column(String(250), primary_key=True)
#     profile_id = Column(Integer, nullable=False)
#     max_id = Column(String(250))


if __name__ == "__main__":
    pass

    Base.metadata.create_all(engine)

    # today = date.today()
    # add_row(Following, ['aaa', '111', today-timedelta(days=2), 0])

    # print(get_first_user(Following))

    # print (expired_followings(2)[1].userId)
    # print(type(expired_followings(2)[1].userId))

    # add_row(Response, ['aaaa', '111', datetime.now()])

    # response_row = friends_for_am()[0]
    # delete_row(response_row)

    # add_row(NoResponse, ['aaaaa'])

    # if noResponse_checking('aaaaa'):
    #     print ('Exist')
    # else:
    #     print ('No Exist')

    # now = datetime.now()
    # add_row(Response, ['bbb', now])

    # print(check_existing(Following, 'kyliejenner').username)

    # print(len(expired_followings(0)))

    # user = get_firstRow_by_primaryKey(Following, 'k')
    # print(user)
    # print(user.userId)