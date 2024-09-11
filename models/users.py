from models.hist import Base, Mapped, mapped_column, String
from managers import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(Base, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(300))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

