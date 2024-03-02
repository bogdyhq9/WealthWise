from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
from domain.errors.usererror import UserError
from domain.tables import UserTable

engine = create_engine('sqlite:///blog.db')
Session = sessionmaker(bind=engine)
sessiondata = Session()


class RepositoryUser:

    def addUser(self, email, username,hash, realname):
        self.valid(email, username)
        user = UserTable(email=email, username=username, hash=hash, realname=realname)
        sessiondata.add(user)
        sessiondata.commit()

    def valid(self, email, username):
        user = sessiondata.query(UserTable).filter(UserTable.email == email).all()
        if user:
            raise UserError("Email is already used")

        user1 = sessiondata.query(UserTable).filter(UserTable.username == username).all()
        if user1:
            raise UserError("Username is unvailable")

    def deleteUser(self, id):
        todelete = sessiondata.query(UserTable).filter(UserTable.id == id).all()
        sessiondata.delete(todelete)
        sessiondata.commit()

    def getById(self, id):
        return sessiondata.query(UserTable).filter(UserTable.id == id).first()

    def getByUsername(self, username):
        return sessiondata.query(UserTable).filter(UserTable.username == username).all()

    def getAll(self):
        return sessiondata.query(UserTable).all()

    def update(self, newuser):

        user = sessiondata.query(UserTable).filter(UserTable.id == newuser.id).first()
        user.username=newuser.username
        user.description=newuser.description
        user.realname=newuser.realname
        user.hash=newuser.hash
        sessiondata.commit()
