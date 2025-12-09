from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TypeEnum(str, Enum):
    FLOAT = "float"
    INTEGER = "int"
    STRING = "str"
    DATETIME = "datetime"
    BOOLEAN = "bool"
    TIME = "time"


class AppConfig(Base):
    __tablename__ = "app_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    unique_name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    type_: Mapped[TypeEnum] = mapped_column(
        String(16), nullable=False, default=TypeEnum.STRING
    )
    sub_data: Mapped[str | None] = mapped_column(String(64), nullable=True)

    def get_value(self) -> Any:
        if self.value is None:
            return None

        if self.type_ == TypeEnum.STRING:
            return self.value
        elif self.type_ == TypeEnum.INTEGER:
            return int(self.value)
        elif self.type_ == TypeEnum.FLOAT:
            return float(self.value)
        elif self.type_ == TypeEnum.DATETIME:
            return datetime.strptime(self.value, self.sub_data or "%Y-%m-%d %H:%M:%S")
        elif self.type_ == TypeEnum.TIME:
            return datetime.strptime(self.value, self.sub_data or "%H:%M:%S").time()
        elif self.type_ == TypeEnum.BOOLEAN:
            return self.value.lower() in ("true", "1", "yes", "y")
        return None


class TextItem(Base):
    __tablename__ = "text_items"
    __table_args__ = (
        Index(
            "idx_text_items_unique_lang", "unique_name", "language_code", unique=True
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    unique_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="ru")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    symbol: Mapped[str] = mapped_column(
        String(10), nullable=False, unique=True, index=True
    )
    rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PaymentCategory(Base):
    __tablename__ = "payment_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    unique_name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=False)
    language: Mapped[str] = mapped_column(
        String(10), nullable=False, default="ru", index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
