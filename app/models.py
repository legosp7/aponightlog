from typing import Optional
from datetime import datetime, timezone, date, time
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
#below to be removed?
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id: str) -> 'User':
    """Load a user by their ID."""
    return db.session.get(User, int(id))

class User(UserMixin,db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))  
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'
    
    def set_password(self, password: str) -> None:
        """Set the user's password hash."""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password: str) -> bool:
        """Check the user's password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),index=True)
    author: so.Mapped[User] = so.relationship(back_populates='posts')
    
    def __repr__(self) -> str:
        return f'<Post {self.body}>'
    
class Obslog(db.Model):
    dateprog: so.Mapped[str] = so.mapped_column(sa.String(12), primary_key=True, unique=True)
    obsdate: so.Mapped[date] = so.mapped_column(sa.Date)
    prog: so.Mapped[str] = so.mapped_column(sa.String(4))
    instrument: so.Mapped[str] = so.mapped_column(sa.String(20))
    PIObs: so.Mapped[str] = so.mapped_column(sa.String(64))
    Obs: so.Mapped[str] = so.mapped_column(sa.Text)
    starttime: so.Mapped[time] = so.mapped_column(sa.Time)
    endtime: so.Mapped[time] = so.mapped_column(sa.Time)

    def __repr__(self) -> str:
        return f'<Obslog {self.dateprog}>'
    
    def todays_obslog(cls, dateprog: str) -> 'Obslog':
        """Return the Obslog for today's date. to be implemented through webscraping"""
        pass

class Proglog(db.Model):
    dateprog: so.Mapped[str] = so.mapped_column(sa.ForeignKey(Obslog.dateprog), primary_key=True, index=True, unique=True)
    progid: so.Mapped[str] = so.mapped_column(sa.String(4), index=True)
    progloc: so.Mapped[str] = so.mapped_column(sa.String(1))
    progdtn: so.Mapped[str] = so.mapped_column(sa.String(1))
    schedstart: so.Mapped[time] = so.mapped_column(sa.Time)
    schedend: so.Mapped[time] = so.mapped_column(sa.Time)
    weatherd: so.Mapped[float] = so.mapped_column(sa.Float)
    weatherb: so.Mapped[float] = so.mapped_column(sa.Float)
    equipd: so.Mapped[float] = so.mapped_column(sa.Float)
    equipb: so.Mapped[float] = so.mapped_column(sa.Float)
    obsd: so.Mapped[float] = so.mapped_column(sa.Float)
    obsb: so.Mapped[float] = so.mapped_column(sa.Float)
    notusedd: so.Mapped[float] = so.mapped_column(sa.Float)
    notusedb: so.Mapped[float] = so.mapped_column(sa.Float)
    note: so.Mapped[str] = so.mapped_column(sa.Text)
    
    def __repr__(self) -> str:
        return f'<Proglog {self.dateprog}>'
    