from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Text, ForeignKey, Date
from db.database.database import Base
import datetime

class Tariff(Base):
    __tablename__ = 'tariffs'


    name: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[int]
    file_id: Mapped[str | None] = mapped_column(Text)
    type_of_tarrifs_id: Mapped[int] = mapped_column(ForeignKey('typoftariffs.id'))
    type_tariff: Mapped["Typoftariffs"] = relationship("Typoftariffs", back_populates="tariffs")
    purchases: Mapped[List['Purchase']] = relationship(
        "Purchase",
        back_populates="tariff",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Tarrif(id={self.id}, name='{self.name}', price={self.price})>"

class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None]
    active: Mapped[bool | None]
    fio: Mapped[str | None]
    data_birth: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    purchases: Mapped[List["Purchase"]] = relationship(
        "Purchase",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"
    
class Purchase(Base):
    __tablename__ = 'purchases'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    tariff_id: Mapped[int] = mapped_column(ForeignKey('tariffs.id'))
    price: Mapped[int]
    active: Mapped[bool]
    payment_id: Mapped[str] = mapped_column(unique=True)
    user: Mapped["User"] = relationship("User", back_populates="purchases")
    tariff: Mapped["Tariff"] = relationship("Tariff", back_populates="purchases")

    def __repr__(self):
        return f"<Purchase(id={self.id}, user_id={self.user_id}, product_id={self.tariff_id}, date={self.created_at})>"
    
    

class Typoftariffs(Base):
    __tablename__ = 'typoftariffs'

    type_tarif_name: Mapped[str] = mapped_column(Text, nullable=False)
    tariffs: Mapped[List["Tariff"]] = relationship(
        "Tariff",
        back_populates="type_tariff",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Typetarif(id={self.id}, Name='{self.type_tarif_name}')>"