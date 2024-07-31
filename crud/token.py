from sqlalchemy.orm import Session
from models.token import Token
from datetime import datetime
from utils import dt

def store_token(db: Session, access_token: str, user_id: int, expires_in: datetime):
    db_token = Token(access_token=access_token, user_id=user_id, expires_at=expires_in)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_token(db: Session, access_token: str):
    return db.query(Token).filter(Token.access_token == access_token).first()

def delete_user_tokens(db: Session, user_id: int):
    db.query(Token).filter(Token.user_id == user_id).delete()
    db.commit()

def delete_expired_tokens(db: Session):
    now = dt.utcnow()
    db.query(Token).filter(Token.expires_at < now).delete()
    db.commit()
