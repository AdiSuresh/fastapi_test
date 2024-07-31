import pytz
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from utils import dt

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=dt.utcnow)
    user = relationship("User", back_populates="tokens")

    def hasExpired(self):
        return pytz.utc.localize(self.expires_at) < dt.utcnow()