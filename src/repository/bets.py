from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, update, insert
from sqlalchemy.orm import selectinload

from src.admin.schemas import ChangeEvent, CurrenStatisticsScheme, StatisticsValuesScheme
from src.bets.models import Bet, Event, EventTeam, Team
from src.bets.schemas import EventScheme, TeamScheme, EventFullScheme
from src.repository.repository import SQLAlchemyRepository


class BetRepository(SQLAlchemyRepository):
    model = Bet

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


class EventRepository(SQLAlchemyRepository):
    model = Event

    async def get_active_events(self) -> Optional[List[EventScheme]]:
        query = select(self.model).where(
            self.model.status == True
        ).options(selectinload(self.model.teams).selectinload(EventTeam.team))
        query_data = await self.session.execute(query)
        events = query_data.scalars().all()
        return [EventScheme.model_validate(event, from_attributes=True) for event in events] if events else None

    async def get_event_specific(self, event_id: int) -> Optional[EventScheme]:
        query = select(self.model).where(
            self.model.id == event_id
        ).options(selectinload(self.model.teams).selectinload(EventTeam.team))
        query_data = await self.session.execute(query)
        events = query_data.scalar()
        return EventScheme.model_validate(events, from_attributes=True) if events else None

    async def get_event_by_id(self, event_id: int) -> Optional[EventFullScheme]:
        query = select(self.model).where(
            self.model.id == event_id
        ).options(
            selectinload(self.model.teams).selectinload(EventTeam.team),
            selectinload(self.model.bets)
        )
        query_data = await self.session.execute(query)
        event = query_data.scalar()
        return EventFullScheme.model_validate(event, from_attributes=True) if event else None

    async def get_all_events(self, limit: int, offset: int) -> Optional[List[EventScheme]]:
        query = (
            select(self.model)
            .options(selectinload(self.model.teams).selectinload(EventTeam.team))
            .order_by(self.model.status.desc())
            .limit(limit)
            .offset(offset)
        )
        query_data = await self.session.execute(query)
        events = query_data.scalars().all()
        return [EventScheme.model_validate(event, from_attributes=True) for event in events] if events else None

    async def close_match(self, data: ChangeEvent) -> bool:
        stmt = update(self.model).where(self.model.id == data.event_id).values(
            status=False,
            won=data.won,
            won_first_map=data.won_first_map,
            won_second_map=data.won_second_map,
            dry_bill=data.dry_bill,
            knife=data.knife
        )
        try:
            await self.session.execute(stmt)
            return True
        except Exception:
            return False


class TeamRepository(SQLAlchemyRepository):
    model = Team

    async def get_all(self) -> List[TeamScheme]:
        query = select(self.model)
        query_data = await self.session.execute(query)
        teams = query_data.scalars().all()
        return [TeamScheme.model_validate(team, from_attributes=True) for team in teams]

    async def change_team(self, data: TeamScheme) -> None:
        stmt = update(self.model).where(self.model.id == data.id).values(name=data.name, logo_url=data.logo_url)
        await self.session.execute(stmt)


class EventTeamRepository(SQLAlchemyRepository):
    model = EventTeam

    async def change_score(self, event_team_id: int, score: int) -> None:
        stmt = update(self.model).where(self.model.id == event_team_id).values(score=score)
        await self.session.execute(stmt)
