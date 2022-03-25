from flask_login import UserMixin

class User(UserMixin):

    def __init__(self, id: str):
        self.id = id

        
    def __repr__(self):
        return "%d" % (self.id)