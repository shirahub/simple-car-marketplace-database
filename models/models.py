from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class City(Base):
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    location: Mapped[str]
    products: Mapped[Optional[List["Product"]]] = relationship()
    accounts: Mapped[Optional[List["Account"]]] = relationship()

    def __repr__(self) -> str:
        return f"City(id={self.id!r}, name={self.name!r}, location={self.location!r})"


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    account: Mapped["Account"] = relationship()
    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"))
    model: Mapped["Model"] = relationship()
    year: Mapped[int]
    price: Mapped[float]
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    city: Mapped["City"] = relationship(back_populates="products")
    created_at: Mapped[datetime]
    deleted_at: Mapped[datetime]
    bids: Mapped[Optional[List["Bid"]]] = relationship(back_populates="product")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


    def __repr__(self):
        return f"Product(id={self.id!r}, account={self.account!r}, city={self.city!r}, created_at={self.created_at!r})"


class Brand(Base):
    __tablename__ = "brands"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    models: Mapped[List["Model"]] = relationship(
        back_populates="brand"
    )

    def __repr__(self) -> str:
        return f"Brand(id={self.id!r}, name={self.name!r})"


class BodyType(Base):
    __tablename__ = "types"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    def __repr__(self) -> str:
        return f"BodyType(id={self.id!r}, name={self.name!r})"


class Model(Base):
    __tablename__ = "models"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"))
    brand: Mapped["Brand"] = relationship(back_populates="models")
    type_id: Mapped[int] = mapped_column(ForeignKey("types.id"))
    type: Mapped["BodyType"] = relationship()


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    phone_number: Mapped[str]
    address: Mapped[str]
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    city: Mapped["City"] = relationship(back_populates="accounts")
    created_at: Mapped[datetime]
    products: Mapped[Optional[List["Product"]]] = relationship(back_populates="account")
    bids: Mapped[Optional["Bid"]] = relationship()

    def __repr__(self) -> str:
        return f"Account(id={self.id!r}, name={self.name!r}, city={self.city!r})"


class Bid(Base):
    __tablename__ = "bids"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    account: Mapped["Account"] = relationship()
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped["Product"] = relationship()
    price: Mapped[float]
    status: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self) -> str:
        return f"Bid(id={self.id!r}, account_id={self.account_id!r}, product_id={self.product_id!r}, created_at={self.created_at!r})"