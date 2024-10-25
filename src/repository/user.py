from datetime import datetime, UTC, timedelta
from typing import Union, Optional, List, Tuple

from sqlalchemy import select, update, func, delete
from sqlalchemy.orm import selectinload

from src.admin.schemas import PromoCodeScheme, CurrenStatisticsScheme, StatisticsValuesScheme
from src.bets.models import Bet, EventTeam, Event, Currency
from src.bets.schemas import BetSimpleScheme
from src.cases.models import TypePriceCase, CaseSkin
from src.repository.repository import SQLAlchemyRepository
from src.skins.schemas import SkinSimpleScheme
from src.user.models import User, UserSkin, UserCase, UserPromoCode, UserReceivingSkin, UserMoney
from src.user.schemas import UserSimpleGet, UserBannedResponse, UserAllGet, UserReferral, UserStatistics, UserGet, \
    UserFullInfoScheme, UserInfoReferral, UserCaseScheme, MoneyScheme, ReceivingSkinScheme, ReceivingScheme


class UserRepository(SQLAlchemyRepository):
    model = User

    async def get_main_info(self, user_id: int) -> UserSimpleGet | None:
        query = select(self.model).where(self.model.id == user_id)
        query_data = await self.session.execute(query)
        user = query_data.scalar_one_or_none()
        return UserSimpleGet.model_validate(user, from_attributes=True) if user else None

    async def update_username(self, user_id: int, username: str) -> None:
        stmt = update(self.model).values(username=username).where(user_id == self.model.id)
        await self.session.execute(stmt)

    async def update_firstname(self, user_id: int, firstname: str) -> None:
        stmt = update(self.model).values(name=firstname).where(user_id == self.model.id)
        await self.session.execute(stmt)

    async def check_user_banned(self, user_id: int) -> UserBannedResponse:
        query = select(self.model).where(self.model.id == user_id)
        query_data = await self.session.execute(query)
        user = query_data.scalar_one_or_none()
        return UserBannedResponse.model_validate(user, from_attributes=True) if user else None
        return UserBannedResponse.model_validate(user, from_attributes=True) if user else None

    async def get_full_info(self, user_id: int) -> UserAllGet:
        query = select(
            self.model
        ).where(
            self.model.id == user_id
        ).options(
            selectinload(self.model.skins).selectinload(UserSkin.skin),
            selectinload(self.model.bets).selectinload(Bet.event).selectinload(Event.teams).selectinload(EventTeam.team),
            selectinload(self.model.cases).selectinload(UserCase.case_skin)
        )
        query_data = await self.session.execute(query)
        user = query_data.scalar()
        total_bets, total_skins, total_referrals = 0, 0, 0

        skins = []
        if user.skins:
            for skin in user.skins:
                total_skins += 1
                skin_info = skin.skin
                skins.append(SkinSimpleScheme.model_validate(skin_info, from_attributes=True))
        else:
            skins = None

        bets = []
        if user.bets:
            for bet in user.bets:
                total_bets += 1
                bets.append(BetSimpleScheme.model_validate(bet, from_attributes=True))
        else:
            bets = None

        total_opened_cases = len(user.cases) if user.cases else 0
        total_days_on_platform = int((datetime.now(UTC).replace(tzinfo=None) - user.created_at).total_seconds() / 86400)

        query = select(self.model).where(self.model.referrer_id == user_id)
        query_data = await self.session.execute(query)
        referrals = query_data.scalars().all()

        referrals_photos = []
        if referrals:
            for referral in referrals:
                total_referrals += 1
                referrals_photos.append(UserReferral(photo_url=referral.photo_url))
        else:
            referrals_photos = None

        statistics = UserStatistics(
            total_bets=total_bets,
            total_skins=total_skins,
            total_referrals=total_referrals,
            total_opened_cases=total_opened_cases,
            total_days_on_platform=total_days_on_platform
        )
        return UserAllGet(statistics=statistics, referrals=referrals_photos, skins=skins, bets=bets)

    async def get_balance_user(self, user_id: int, currency: Currency) -> Union[int, float]:
        query = select(self.model).where(self.model.id == user_id)
        query_data = await self.session.execute(query)
        user = query_data.scalar()
        return user.balance_usdt if currency == Currency.usdt else user.balance_coin

    async def get_balance_user_full(self, user_id: int, currency: TypePriceCase) -> Union[int, float]:
        query = select(self.model).where(self.model.id == user_id)
        query_data = await self.session.execute(query)
        user = query_data.scalar()
        return user.balance_usdt if currency == TypePriceCase.usdt else user.balance_coin if currency == TypePriceCase.coin else user.balance_referrers

    async def change_balance(
            self, user_id: int, currency: Currency, value: Union[int, float], replace: bool = False
    ) -> None:
        if currency == Currency.usdt:
            new_balance = (self.model.balance_usdt + value) if not replace else value
            stmt = update(self.model).where(self.model.id == user_id).values(balance_usdt=new_balance)
        else:
            new_balance = (self.model.balance_coin + value) if not replace else value
            stmt = update(self.model).where(self.model.id == user_id).values(balance_coin=new_balance)
        await self.session.execute(stmt)

    async def get_trade_url(self, user_id: int) -> str | None:
        query = select(self.model.trade_url).where(self.model.id == user_id)
        query_data = await self.session.execute(query)
        return query_data.scalar()

    async def update_trade_url(self, user_id: int, trade_url: str) -> None:
        stmt = update(self.model).where(self.model.id == user_id).values(trade_url=trade_url)
        await self.session.execute(stmt)

    async def update_balance(self, user_id: int, balance_type: TypePriceCase, value: float | int, add: bool = False) -> None:
        if balance_type == TypePriceCase.coin:
            values = {"balance_coin": value if not add else self.model.balance_coin + value}
        elif balance_type == TypePriceCase.usdt:
            values = {"balance_usdt": value if not add else self.model.balance_usdt + value}
        else:
            values = {"balance_referrers": value if not add else self.model.balance_referrers + value}
        stmt = update(self.model).where(
            self.model.id == user_id
        ).values(**values)
        await self.session.execute(stmt)

    async def update_clip(self, user_id: int, minus: bool = True, value: int | None = None) -> None:
        stmt = update(self.model).where(self.model.id == user_id).values(
            count_clip=self.model.count_clip - (1 if not value else value) if minus else self.model.count_clip + (1 if not value else value)
        )
        await self.session.execute(stmt)

    async def last_open_case(self, user_id: int) -> Optional[datetime]:
        query = select(self.model.last_open_case).where(self.model.id == user_id)
        query_data = await self.session.execute(query)
        return query_data.scalar()

    async def update_last_open_case(self, user_id: int):
        stmt = update(self.model).where(self.model.id == user_id).values(last_open_case=datetime.now(UTC).replace(tzinfo=None))
        await self.session.execute(stmt)

    async def statistics(
            self, date_today: datetime, date_last_day: datetime, date_month: datetime, date_last_month: datetime
    ) -> CurrenStatisticsScheme:
        query = select(self.model.created_at)
        query_data = await self.session.execute(query)
        dates = query_data.scalars().all()
        day, last_day, month, last_month, all_time = 0, 0, 0, 0, 0
        for date in dates:
            all_time += 1
            if date >= date_today:
                day += 1
            if date_last_day >= date >= date_today:
                last_day += 2
            if date >= date_month:
                month += 1
            if date_last_month <= date <= date_month:
                date_last_month += 1
        try:
            day_percent = round(((day - last_day) / last_day * 100), 2)
        except ZeroDivisionError:
            day_percent = 0
        try:
            month_percent = round(((month - last_month) / last_month * 100), 2)
        except ZeroDivisionError:
            month_percent = 0
        day = StatisticsValuesScheme(value=day, last_value=last_day, percent=day_percent)
        month = StatisticsValuesScheme(value=month, last_value=last_month, percent=month_percent)
        return CurrenStatisticsScheme(day=day, month=month, all=all_time)


    async def get_all_users(self, limit: int, offset: int) -> List[UserGet]:
        query = select(self.model).limit(limit).offset(offset)
        query_data = await self.session.execute(query)
        users = query_data.scalars().all()
        return [UserGet.model_validate(user, from_attributes=True) for user in users]

    async def get_referrers(self, user_id: int) -> Tuple[List[UserInfoReferral], int]:
        query = select(self.model).where(self.model.referrer_id == user_id)
        query_data = await self.session.execute(query)
        referrals = query_data.scalars().all()
        total_referrers = 0
        referrers = []
        if referrals:
            for referral in referrals:
                total_referrers += 1
                referrers.append(UserInfoReferral(id=referral.id, photo_url=referral.photo_url, name=referral.name))
        else:
            referrers = []
        return referrers, total_referrers

    async def get_by_id(self, user_id: int) -> UserFullInfoScheme:
        query = select(self.model).where(self.model.id == user_id).options(
            selectinload(self.model.cases).selectinload(UserCase.case_skin).options(selectinload(CaseSkin.case), selectinload(CaseSkin.skin)),
            selectinload(self.model.moneys),
            selectinload(self.model.receiving_skin).selectinload(UserReceivingSkin.skin),
            selectinload(self.model.skins).selectinload(UserSkin.skin),
            selectinload(self.model.bets).selectinload(Bet.event).selectinload(Event.teams).selectinload(EventTeam.team)
        )
        query_data = await self.session.execute(query)
        user = query_data.scalar()
        total_bets, total_skins = 0, 0
        skins = []
        if user.skins:
            for skin in user.skins:
                total_skins += 1
                skin_info = skin.skin
                skins.append(SkinSimpleScheme.model_validate(skin_info, from_attributes=True))
        else:
            skins = []

        bets = []
        if user.bets:
            for bet in user.bets:
                total_bets += 1
                bets.append(BetSimpleScheme.model_validate(bet, from_attributes=True))
        else:
            bets = []

        total_opened_cases = len(user.cases) if user.cases else 0
        total_days_on_platform = int((datetime.now(UTC).replace(tzinfo=None) - user.created_at).total_seconds() / 86400)
        referrals, total_referrals = await self.get_referrers(user_id)
        statistics = UserStatistics(
            total_bets=total_bets,
            total_skins=total_skins,
            total_referrals=total_referrals,
            total_opened_cases=total_opened_cases,
            total_days_on_platform=total_days_on_platform
        )
        data = {
            **user.__dict__,
            "statistics": statistics,
            "skins": skins,
            "bets": bets,
            "cases": [UserCaseScheme.model_validate(case, from_attributes=True) for case in user.cases],
            "moneys": [MoneyScheme.model_validate(money, from_attributes=True) for money in user.moneys],
            "referrals": referrals,
            "receiving_skin": [ReceivingSkinScheme.model_validate(receiving, from_attributes=True) for receiving in user.receiving_skin],
        }
        return UserFullInfoScheme.model_validate(data, from_attributes=True)

    async def change_banned(self, user_id: int, value: bool):
        stmt = update(self.model).where(self.model.id == user_id).values(banned=value)
        await self.session.execute(stmt)


class UserCaseRepository(SQLAlchemyRepository):
    model = UserCase

    async def statistics(
            self, date_today: datetime, date_last_day: datetime, date_month: datetime, date_last_month: datetime
    ) -> CurrenStatisticsScheme:
        query = select(self.model.created_at)
        query_data = await self.session.execute(query)
        dates = query_data.scalars().all()
        day, last_day, month, last_month, all_time = 0, 0, 0, 0, 0
        for date in dates:
            all_time += 1
            if date >= date_today:
                day += 1
            if date_last_day >= date >= date_today:
                last_day += 2
            if date >= date_month:
                month += 1
            if date_last_month <= date <= date_month:
                date_last_month += 1
        try:
            day_percent = round(((day - last_day) / last_day * 100), 2)
        except ZeroDivisionError:
            day_percent = 0
        try:
            month_percent = round(((month - last_month) / last_month * 100), 2)
        except ZeroDivisionError:
            month_percent = 0
        day = StatisticsValuesScheme(value=day, last_value=last_day, percent=day_percent)
        month = StatisticsValuesScheme(value=month, last_value=last_month, percent=month_percent)
        return CurrenStatisticsScheme(day=day, month=month, all=all_time)

class UserSkinRepository(SQLAlchemyRepository):
    model = UserSkin

    async def statistics(
            self, date_today: datetime, date_last_day: datetime, date_month: datetime, date_last_month: datetime
    ) -> CurrenStatisticsScheme:
        query = select(self.model.created_at)
        query_data = await self.session.execute(query)
        dates = query_data.scalars().all()
        day, last_day, month, last_month, all_time = 0, 0, 0, 0, 0
        for date in dates:
            all_time += 1
            if date >= date_today:
                day += 1
            if date_last_day >= date >= date_today:
                last_day += 2
            if date >= date_month:
                month += 1
            if date_last_month <= date <= date_month:
                date_last_month += 1
        try:
            day_percent = round(((day - last_day) / last_day * 100), 2)
        except ZeroDivisionError:
            day_percent = 0
        try:
            month_percent = round(((month - last_month) / last_month * 100), 2)
        except ZeroDivisionError:
            month_percent = 0
        day = StatisticsValuesScheme(value=day, last_value=last_day, percent=day_percent)
        month = StatisticsValuesScheme(value=month, last_value=last_month, percent=month_percent)
        return CurrenStatisticsScheme(day=day, month=month, all=all_time)

    async def delete_skin(self, skin_id: int) -> None:
        stmt = delete(self.model).where(self.model.id == skin_id)
        await self.session.execute(stmt)

    async def get_skin(self, user_id: int, skin_id: int):
        query = select(self.model.id).where(self.model.skin_id == skin_id, self.model.user_id == user_id)
        query_data = await self.session.execute(query)
        return query_data.scalars().first()


class UserPromoCodeRepository(SQLAlchemyRepository):
    model = UserPromoCode

    async def check_used(self, user_id: int, promo_code_id: int) -> bool:
        query = select(self.model).where(self.model.user_id == user_id, self.model.promo_code_id == promo_code_id)
        query_data = await self.session.execute(query)
        used = query_data.scalar()
        return bool(used)

    async def get_all_used_promo_codes(self, user_id: int) -> Optional[List[PromoCodeScheme]]:
        query = select(self.model).where(self.model.user_id == user_id).options(
            selectinload(self.model.promo_code)
        )
        query_data = await self.session.execute(query)
        promo_codes = query_data.scalars().all()
        return [PromoCodeScheme.model_validate(promo_code.promo_code, from_attributes=True) for promo_code in promo_codes] if promo_codes else None


class UserMoneyRepository(SQLAlchemyRepository):
    model = UserMoney


class UserReceivingSkinRepository(SQLAlchemyRepository):
    model = UserReceivingSkin

    async def delete_receiving(self, receiving_id: int) -> None:
        stmt = delete(self.model).where(self.model.id == receiving_id)
        await self.session.execute(stmt)

    async def update_status(self, receiving_id: int, status: str) -> None:
        stmt = update(self.model).where(self.model.id == receiving_id).values(status=status)
        await self.session.execute(stmt)

    async def get_all(self) -> List[ReceivingScheme]:
        query = select(self.model)
        query_data = await self.session.execute(query)
        receiving = query_data.scalars().all()
        return [ReceivingScheme.model_validate(rec, from_attributes=True) for rec in receiving]

    async def get_by_id(self, rec_id: int) -> Optional[ReceivingScheme]:
        query = select(self.model).where(self.model.id == rec_id)
        query_data = await self.session.execute(query)
        rec = query_data.scalar()
        return ReceivingScheme.model_validate(rec, from_attributes=True) if rec else None

