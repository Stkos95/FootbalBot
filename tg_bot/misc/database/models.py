from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Integer, String, Column, Sequence, ForeignKey, DATETIME, TIMESTAMP, Boolean, Date, \
    ForeignKeyConstraint
import datetime

Base = declarative_base()





class Admins(Base):
    __tablename__ = 'admins'
    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False, primary_key=True )
    date = Column(TIMESTAMP, default=datetime.datetime.now())
    user = relationship('Users', back_populates='admin_users' )
    team = relationship('Teams', back_populates='admin_teams')




class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_full_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    permision_id = Column(Integer, ForeignKey('permisions.permision_id'))
    admin_users = relationship('Admins', back_populates='user')
    permision = relationship('Permisions')

class Tournaments(Base):
    __tablename__ = 'tournaments'
    tournament_id = Column(Integer, primary_key=True)
    round_id = Column(Integer, primary_key=True)
    name_tournament = Column(String, nullable=False)
    name_round = Column(String, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    # rangs = Column(Integer, nullable=False)
    # tourn = relationship('Teams', back_populates='tournament')

# class Rounds(Base):
#     __tablename__ = 'rounds'
#     round_id = Column(Integer, primary_key=True)
#     round_name = Column(String, nullable=False)
#     tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'))
#     tournament = relationship('Tournaments')


class Teams(Base):
    __tablename__ = 'teams'
    team_id = Column(Integer, primary_key=True)
    team_name = Column(String, nullable=False)
    # # tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'), nullable=False)
    # # tournament = relationship('Tournaments', back_populates='tourn')
    admin_teams = relationship('Admins', back_populates='team')

class Confirmation(Base):
    __tablename__ = 'confirmation'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String, nullable=False)
    user_full_name = Column(String, nullable=False)
    team_id = Column(Integer, nullable=False)

class TeamTournaments(Base):
    __tablename__ = 'teams_application'
    # team_id = Column(Integer, ForeignKey('teams.team_id'), primary_key=True)
    # tournament_id = Column(Integer, ForeignKey('tournaments.tournament_id'), primary_key=True)
    # round_id = Column(Integer, ForeignKey('tournaments.round_id'), primary_key=True, )
    team_id = Column(Integer,ForeignKey('teams.team_id'), primary_key=True)
    tournament_id = Column(Integer,  primary_key=True)
    round_id = Column(Integer,  primary_key=True, )
    __table_args__ = (
        ForeignKeyConstraint(
            ("tournament_id", "round_id"), ("tournaments.tournament_id", "tournaments.round_id")
        ),)
    tournament = relationship('Tournaments')
    team = relationship('Teams')
    # tournament = relationship('Tournaments')
    # team = relationship('Teams')


class Permisions(Base):
    __tablename__ = 'permisions'
    permision_id = Column(Integer, primary_key=True)
    description = Column(String(20))
