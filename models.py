import bcrypt
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    @staticmethod
    def create_user(username: str, password: str) -> "User":
        """Creates user
        """
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        )
        return User(username=username, password_hash=password_hash.decode('utf-8'))

    def validate(self, password: str) -> bool:
        """Validates candidate password
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
