from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Integer, String, Column, Sequence, ForeignKey, DATETIME, TIMESTAMP
import datetime

Base = declarative_base()





class Admins(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False, )
    # tournament_id = Column(Integer)
    date = Column(TIMESTAMP, default=datetime.datetime.now())
    team = relationship('Teams')
    # admin_rang = Column(Integer, not

    full_name = relationship('Users')



    def __repr__(self):
        return f'Admins({self.user_id}, name={self.full_name}, team={self.team})'



class Users(Base):
    __tablename__ = 'users'
    # id = Column(Integer, primary_key = True)
    # user_id = Column(Integer)
    user_id = Column(Integer, primary_key=True)
    user_full_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    is_admin = Column(String)




class Tournaments(Base):
    __tablename__ = 'tournaments'
    tournament_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    rangs = Column(Integer, nullable=False)
    tourn = relationship('Teams', back_populates='tournament')
    # admin = relationship('Admins')




class Teams(Base):
    __tablename__ = 'teams'

    team_id = Column(Integer, primary_key=True)
    team_name = Column(String, nullable=False)
    tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'), nullable=False)
    tournament = relationship('Tournaments', back_populates='tourn')
    # admin = relationship('Admins')


class Confirmation(Base):
    __tablename__ = 'confirmation'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    # user_id = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    user_full_name = Column(String, nullable=False)
    team_id = Column(Integer, nullable=False)



class TeamTournaments(Base):
    __tablename__ = 'teams_application'
    team_id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, primary_key=True)



