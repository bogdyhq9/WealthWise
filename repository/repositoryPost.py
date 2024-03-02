from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
from domain.errors.usererror import UserError
from domain.tables import UserTable, PostTable

engine = create_engine('sqlite:///blog.db')
Session = sessionmaker(bind=engine)
sessiondata = Session()


class RepositoryPost:

    def addPost(self, title, category, content, username):
        post = PostTable(title=title, category=category, content=content, username=username)
        sessiondata.add(post)
        sessiondata.commit()

    def deletePost(self, id):
        post = sessiondata.query(PostTable).filter(PostTable.id == id).first()
        sessiondata.delete(post)
        sessiondata.commit()

    def getById(self, id):
        return sessiondata.query(PostTable).filter(PostTable.id == id).first()

    def getAll(self):
        return sessiondata.query(PostTable).all()

    def getAllByUser(self,username):
        return sessiondata.query(PostTable).filter(PostTable.username == username).all()

    def update(self,newpost):
        post=self.getById(newpost.id)
        post.username=newpost.username
        post.title=newpost.title
        post.content=newpost.content
        post.category=newpost.category
        sessiondata.commit()
