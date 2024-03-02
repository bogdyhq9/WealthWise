from werkzeug.security import check_password_hash, generate_password_hash

from domain.errors.usererror import UserError
from repository.repositoryGroup import RepositoryGroup
from repository.repositoryPost import RepositoryPost
from repository.repositoryUser import RepositoryUser


class Service:
    def __init__(self, repoUser:RepositoryUser, repoPost:RepositoryPost, repoGroup:RepositoryGroup):
        self.__repoUser = repoUser
        self.__repoPost = repoPost
        self.__repoGroup = repoGroup

    def addUser(self,email,username,hash,realname):
        self.__repoUser.addUser(email, username,hash, realname)

    def loginUser(self,username,password):

        user = self.__repoUser.getByUsername(username)

        if len(user) != 1:
            raise UserError("The username is invalid")
        if not check_password_hash(user[0].hash, password):
            raise UserError("The password is invalid")
        return user

    def getUserByID(self, id):
        return self.__repoUser.getById(id)

    def changePassword(self,username, email, id, newpass, confirmpass):
        user=self.__repoUser.getById(id)
        if user.username == username and user.email == email:
            if newpass == confirmpass:
                hash = generate_password_hash(newpass)
                user.hash= hash
                self.__repoUser.update(user)
            else:
                raise UserError("Passwords don't match")
        else:
            raise UserError("Invalid information")

    def editprofile(self,newusername,newrealname,newdescription,user_id):
        user=self.__repoUser.getById(user_id)
        username=user.username
        user.username=newusername
        user.realname=newrealname
        user.description=newdescription
        self.__repoUser.update(user)
        posts=self.__repoPost.getAllByUser(username)

        for post in posts:
            post.username=newusername
            self.__repoPost.update(post)

    def addPost(self,title,category,content,username):
        self.__repoPost.addPost(title,category,content,username)

    def getAllPost(self):
        return self.__repoPost.getAll()

    def getAllGroups(self):
        return self.__repoGroup.getAll()

    def getGroupById(self,id):
        return self.__repoGroup.getById(id)
