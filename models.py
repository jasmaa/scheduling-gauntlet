import bcrypt
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_verified = db.Column(db.Boolean(), nullable=False, default=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    code = db.Column(db.String(80))

    @staticmethod
    def create_user(username: str, email: str, password: str) -> "User":
        """Creates user
        """
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        )
        return User(username=username, email=email, password_hash=password_hash.decode('utf-8'))

    def validate(self, password: str) -> bool:
        """Validates candidate password
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def set_password(self, password: str):
        """Sets user password
        """
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        )
        self.password_hash = password_hash.decode('utf-8')
