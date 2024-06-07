from datetime import date, timezone
from typing import Optional
import sqlalchemy as s_alch
import sqlalchemy.orm as s_orm
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class User(UserMixin, db.Model):
    id: s_orm.Mapped[int] = s_orm.mapped_column(primary_key=True)
    username: s_orm.Mapped[str] = s_orm.mapped_column(s_alch.String(32), index=True, unique=True)
    email: s_orm.Mapped[str] = s_orm.mapped_column(s_alch.String(120), index=True, unique=True)
    password_hash: s_orm.Mapped[Optional[str]] = s_orm.mapped_column(s_alch.String(256))
    books: s_orm.WriteOnlyMapped['Book'] = s_orm.relationship(back_populates='owner')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_owned_books(self):
        # Returns all the books belonging to the user
        return s_alch.select(Book).where(Book.owner_id == self.id)

class Book(db.Model):
    id: s_orm.Mapped[int] = s_orm.mapped_column(primary_key=True)
    title: s_orm.Mapped[str] = s_orm.mapped_column(s_alch.String(64))
    author: s_orm.Mapped[str] = s_orm.mapped_column(s_alch.String(64))
    date_of_purchase: s_orm.Mapped[date] = s_orm.mapped_column(index=True)
    notes: s_orm.Mapped[str] = s_orm.mapped_column(s_alch.String(512))
    owner_id: s_orm.Mapped[int] = s_orm.mapped_column(s_alch.ForeignKey(User.id), index=True)
    owner: s_orm.Mapped[User] = s_orm.relationship(back_populates='books')

    def __repr__(self):
        return '{} - {}'.format(self.title, self.author)
