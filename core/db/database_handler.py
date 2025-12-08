from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional, Sequence, List, Dict

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from core.db.base import Base
from core.db.tables import (
    User,
    TextItem,
    AppConfig,
    Currency,
)
from core.templates.texts import predefined_texts


class DatabaseHandler:
    """
    Async database handler for managing shop operations.
    """

    def __init__(self, url: str):
        self.url = url
        self.engine = create_async_engine(self.url, echo=False)
        self.sessionmaker = async_sessionmaker(
            self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    async def init(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await self._create_predefined_texts()
        await self._create_predefined_currencies()

    async def _create_predefined_texts(self) -> None:
        """Создает в базе данных предопределенные тексты, если их нет"""
        async with self.sessionmaker() as session:
            for unique_name, translations in predefined_texts.items():
                for lang_code, content in translations.items():
                    existing = await session.scalar(
                        select(TextItem).where(
                            TextItem.unique_name == unique_name,
                            TextItem.language_code == lang_code,
                        )
                    )
                    if not existing:
                        session.add(
                            TextItem(
                                unique_name=unique_name,
                                language_code=lang_code,
                                content=content,
                            )
                        )
            await session.commit()

    async def _create_predefined_currencies(self) -> None:
        """Создает в базе данных предопределенные валюты, если их нет"""
        async with self.sessionmaker() as session:
            predefined_currencies = {
                "kzt": "🇰🇿 KZT",
                "rub": "🇷🇺 RUB",
            }
            for symbol, name in predefined_currencies.items():
                existing = await session.scalar(
                    select(Currency).where(
                        Currency.symbol == symbol,
                    )
                )
                if not existing:
                    session.add(
                        Currency(
                            symbol=symbol,
                            name=name,
                            rate=Decimal("1.0"),
                            is_active=True,
                        )
                    )
            await session.commit()

    async def close(self) -> None:
        await self.engine.dispose()

    # ==================== USER OPERATIONS ====================

    async def create_or_get_user(
        self,
        user_tg_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        language: Optional[str] = "ru",
    ) -> User:
        async with self.sessionmaker() as session:
            result = await session.execute(
                select(User).where(User.user_tg_id == user_tg_id)
            )
            user = result.scalar_one_or_none()

            if user:
                # Обновляем данные если изменились
                if username and user.username != username:
                    user.username = username
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                if last_name and user.last_name != last_name:
                    user.last_name = last_name
                await session.commit()
                return user

            # Создаем нового пользователя
            user = User(
                user_tg_id=user_tg_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                language=language,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def get_user(self, user_tg_id: int) -> Optional[User]:
        async with self.sessionmaker() as session:
            result = await session.execute(
                select(User).where(User.user_tg_id == user_tg_id)
            )
            return result.scalar_one_or_none()

    async def update_user(self, user_tg_id: int, **kwargs: Any) -> Optional[User]:
        async with self.sessionmaker() as session:
            async with session.begin():
                result = await session.execute(
                    select(User).where(User.user_tg_id == user_tg_id)
                )
                user = result.scalar_one_or_none()
                if not user:
                    return None

                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)

            return user

    async def delete_user(self, user_tg_id: int) -> bool:
        async with self.sessionmaker() as session:
            async with session.begin():
                result = await session.execute(
                    delete(User).where(User.user_tg_id == user_tg_id)
                )
                return True

    async def ban_user(self, user_tg_id: int) -> bool:
        return await self.update_user(user_tg_id, is_banned=True) is not None

    async def unban_user(self, user_tg_id: int) -> bool:
        return await self.update_user(user_tg_id, is_banned=False) is not None

    async def get_all_users(
        self, limit: int = 100, offset: int = 0, is_banned: Optional[bool] = None
    ) -> Sequence[User]:
        async with self.sessionmaker() as session:
            stmt = select(User)
            if is_banned is not None:
                stmt = stmt.where(User.is_banned == is_banned)
            stmt = stmt.limit(limit).offset(offset).order_by(User.created_at.desc())
            result = await session.execute(stmt)
            return result.scalars().all()

    # ==================== TEXT ITEMS OPERATIONS ====================

    async def get_text_items_by_name(
        self, unique_names: List[str], language_code: str = "ru"
    ) -> Dict[str, str]:
        async with self.sessionmaker() as session:
            result = await session.execute(
                select(TextItem).where(
                    TextItem.unique_name.in_(unique_names),
                    TextItem.language_code == language_code,
                )
            )
            text_items = result.scalars().all()
            return {item.unique_name: item.content for item in text_items}

    async def set_text_item(
        self, unique_name: str, language_code: str, content: str
    ) -> TextItem:
        async with self.sessionmaker() as session:
            async with session.begin():
                result = await session.execute(
                    select(TextItem).where(
                        TextItem.unique_name == unique_name,
                        TextItem.language_code == language_code,
                    )
                )
                text_item = result.scalar_one_or_none()

                if text_item:
                    text_item.content = content
                else:
                    text_item = TextItem(
                        unique_name=unique_name,
                        language_code=language_code,
                        content=content,
                    )
                    session.add(text_item)

                await session.commit()
                await session.refresh(text_item)
                return text_item

    # ==================== APP CONFIG OPERATIONS ====================

    async def get_config(self, unique_name: str) -> Optional[Any]:
        async with self.sessionmaker() as session:
            result = await session.execute(
                select(AppConfig).where(AppConfig.unique_name == unique_name)
            )
            config = result.scalar_one_or_none()
            return config.get_value() if config else None

    async def set_config(
        self,
        unique_name: str,
        value: str,
        type_: str = "str",
        description: Optional[str] = None,
        description_en: Optional[str] = None,
        sub_data: Optional[str] = None,
    ) -> AppConfig:
        async with self.sessionmaker() as session:
            async with session.begin():
                result = await session.execute(
                    select(AppConfig).where(AppConfig.unique_name == unique_name)
                )
                config = result.scalar_one_or_none()

                if config:
                    config.value = value
                    config.type_ = type_
                    if description:
                        config.description = description
                    if description_en:
                        config.description_en = description_en
                    if sub_data:
                        config.sub_data = sub_data
                else:
                    config = AppConfig(
                        unique_name=unique_name,
                        value=value,
                        type_=type_,
                        description=description,
                        description_en=description_en,
                        sub_data=sub_data,
                    )
                    session.add(config)

                await session.commit()
                await session.refresh(config)
                return config

    # ==================== CURRENCY OPERATIONS ====================
    async def get_currencies(self) -> List[Currency]:
        async with self.sessionmaker() as session:
            result = await session.execute(select(Currency))
            return result.scalars().all()

    async def get_currency_by_symbol(self, symbol: str) -> Optional[Currency]:
        async with self.sessionmaker() as session:
            result = await session.execute(
                select(Currency).where(Currency.symbol == symbol)
            )
            return result.scalar_one_or_none()
