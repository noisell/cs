from typing import List, Optional, Union

from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload

from src.admin.schemas import CurrenStatisticsScheme
from src.repository.repository import SQLAlchemyRepository
from src.skins.models import Skin, SkinQuality, RaritySkin, Gun
from src.skins.schemas import SkinSimpleScheme, Sorting, GunsScheme, GunGetScheme, SkinFullScheme, GunsFullScheme


class SkinRepository(SQLAlchemyRepository):
    model = Skin

    async def get_all(
            self,
            limit: int,
            offset: int,
            sorting: Sorting,
            name: str | None = None,
            gun_id: int | None = None,
            quality: SkinQuality | None = None,
            rarity: RaritySkin | None = None,
    ) -> Optional[List[SkinSimpleScheme]]:
        query = select(self.model).where(self.model.active == True)
        if name:
            query = query.where(func.lower(self.model.name).like(f"%{name.lower()}%"))
        else:
            query = query.where(self.model.gun_id == gun_id) if gun_id else query
            query = query.where(self.model.quality == quality.value) if quality else query
            query = query.where(self.model.rarity == rarity.value) if rarity else query
        if sorting == Sorting.cheaper:
            query = query.order_by(self.model.price.asc())
        elif sorting == Sorting.dearly:
            query = query.order_by(self.model.price.desc())

        query = query.limit(limit).offset(offset)
        query_data = await self.session.execute(query)
        skins = query_data.scalars().all()
        if not skins:
            return None
        return [SkinSimpleScheme.model_validate(skin, from_attributes=True) for skin in skins]

    async def get_all_full(
            self,
            limit: int,
            offset: int,
            sorting: Sorting,
            name: str | None = None,
            gun_id: int | None = None,
            quality: SkinQuality | None = None,
            rarity: RaritySkin | None = None,
    ) -> Optional[List[SkinSimpleScheme]]:
        query = select(self.model).order_by(self.model.active.desc())
        if name:
            query = query.where(func.lower(self.model.name).like(f"%{name.lower()}%"))
        else:
            query = query.where(self.model.gun_id == gun_id) if gun_id else query
            query = query.where(self.model.quality == quality.value) if quality else query
            query = query.where(self.model.rarity == rarity.value) if rarity else query
        if sorting == Sorting.cheaper:
            query = query.order_by(self.model.price.asc())
        elif sorting == Sorting.dearly:
            query = query.order_by(self.model.price.desc())

        query = query.limit(limit).offset(offset)
        query_data = await self.session.execute(query)
        skins = query_data.scalars().all()
        if not skins:
            return None
        return [SkinFullScheme.model_validate(skin, from_attributes=True) for skin in skins]

    async def get_all_names_skins(self):
        query = select(self.model).where(self.model.active == True)
        query_data = await self.session.execute(query)
        skins = query_data.scalars().all()
        result = {}
        for skin in skins:
            name = skin.name
            if name not in result.values():
                result[skin.id] = name
        return result

    async def get_skin_by_id(self, skin_id: int) -> SkinSimpleScheme:
        query = select(self.model).where(self.model.id == skin_id)
        query_data = await self.session.execute(query)
        skin = query_data.scalar()
        return SkinSimpleScheme.model_validate(skin, from_attributes=True)

    async def change_skin(self, data: SkinFullScheme) -> None:
        stmt = update(self.model).where(self.model.id == data.id).values(
            name=data.name,
            price=data.price,
            gun_id=data.gun_id,
            quality=data.quality,
            rarity=data.rarity,
            image_url=data.image_url,
            active=data.active,
        )
        await self.session.execute(stmt)


class GunRepository(SQLAlchemyRepository):
    model = Gun

    async def get_all_guns(self, parent: bool = False) -> Union[List[GunsScheme], List[GunsFullScheme]]:
        query = select(self.model).options(selectinload(self.model.children))
        query_data = await self.session.execute(query)
        data = query_data.scalars().all()
        guns = {gun.id: gun for gun in data}
        def build_tree(gun_id: int):
            gun = guns.get(gun_id)
            if gun:
                return {
                    "id": gun.id,
                    "name": gun.name,
                    "children": [build_tree(child.id) for child in gun.children]
                } if not parent else {
                    "id": gun.id,
                    "name": gun.name,
                    "parent_id": gun.parent_id,
                    "children": [build_tree(child.id) for child in gun.children]
                }
            return None

        root_guns = [i for i in data if i.parent_id is None]
        normalized_guns = [build_tree(i.id) for i in root_guns]
        return [GunsScheme.model_validate(gun, from_attributes=True) for gun in normalized_guns] if not parent else \
            [GunsFullScheme.model_validate(gun, from_attributes=True) for gun in normalized_guns]


    async def change_gun(self, data: GunGetScheme) -> None:
        stmt = update(self.model).where(self.model.id == data.id).values(name=data.name, parent_id=data.parent_id)
        await self.session.execute(stmt)