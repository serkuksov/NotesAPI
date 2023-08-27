from sqlalchemy import ForeignKey, String, Column, DateTime, func, Integer
from sqlalchemy.orm import relationship

from db import Base


class Note(Base):
    __tablename__ = 'note'

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    title = Column(String(60), nullable=False)
    content = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship('User', overlaps="notes")

    def __repr__(self):
        return f'Заметка - {self.title}'
