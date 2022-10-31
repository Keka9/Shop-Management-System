from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class UserRole(database.Model):
    __tablename__ = 'user_role'

    id_user = database.Column(database.Integer, database.ForeignKey('users.id'), primary_key=True)
    id_role = database.Column(database.Integer, database.ForeignKey('roles.id'), primary_key=True)


class User(database.Model):
    __tablename__ = 'users'

    id = database.Column(database.Integer, primary_key=True)
    forename = database.Column(database.String(256), nullable=False)
    surname = database.Column(database.String(256), nullable=False)
    email = database.Column(database.String(256), nullable=False, unique=True)
    password = database.Column(database.String(256), nullable=False)

    roles = database.relationship('Role', secondary=UserRole.__table__, back_populates='users')


class Role(database.Model):
    __tablename__ = 'roles'

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    users = database.relationship('User', secondary=UserRole.__table__, back_populates='roles')
