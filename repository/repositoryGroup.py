from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
from domain.errors.usererror import UserError
from domain.tables import UserTable, PostTable, GroupTable

engine = create_engine('sqlite:///blog.db')
Session = sessionmaker(bind=engine)
sessiondata = Session()

class RepositoryGroup:

    def addGroup(self,name,description,permission,number_of_members,creator_id):
        group=GroupTable(name=name,description=description,permission=permission,number_of_members=number_of_members,
                         creator_id=creator_id)
        sessiondata.add(group)
        sessiondata.commit()

    def deleteGroup(self, id):
        group=sessiondata.query(GroupTable).filter(GroupTable.id == id).first()
        sessiondata.delete(group)
        sessiondata.commit()

    def getById(self, id):
        return sessiondata.query(GroupTable).filter(GroupTable.id == id).first()

    def getAll(self):
        return sessiondata.query(GroupTable).all()
