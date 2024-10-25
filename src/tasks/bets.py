from src.bets.models import BetType, Currency
from src.bot.handlers.system import bet_message
from src.unit_of_work import UnitOfWork

async def pay(event_id: int):
    async with UnitOfWork() as uow:
        event = await uow.event.get_event_by_id(event_id)
        bets = event.bets
        if not bets:
            return
        won = event.won
        won_first_map = event.won_first_map
        won_second_map = event.won_second_map
        dry_bill = event.dry_bill
        knife = event.knife
        teams = {team.id: team for team in event.teams}
        team_one = event.teams[0].team.name
        team_two = event.teams[1].team.name
        score_one = event.teams[0].score
        score_two = event.teams[1].score

        teams_bets: dict[int, dict[str, int]] = {team.team.id: {
            "won_usdt": 0,
            "won_coin": 0,
            "won_first_map_usdt": 0,
            "won_first_map_coin": 0,
            "won_second_map_usdt": 0,
            "won_second_map_coin": 0,
        } for team in event.teams}

        won_total_usdt, won_total_coin = 0, 0
        won_first_map_total_usdt, won_first_map_total_coin = 0, 0
        won_second_map_total_usdt, won_second_map_total_coin = 0, 0
        dry_bill_win_usdt, dry_bill_loss_usdt, dry_bill_win_coin, dry_bill_loss_coin = 0, 0, 0, 0
        knife_win_usdt, knife_loss_usdt, knife_win_coin, knife_loss_coin = 0, 0, 0, 0
        for bet in bets:
            bet_type = bet.bet_type
            if bet_type == BetType.win:
                event_team = teams[bet.event_team_id]
                if bet.currency == Currency.usdt:
                    won_total_usdt += bet.amount
                    teams_bets[event_team.team.id]["won_usdt"] += bet.amount
                else:
                    won_total_coin += bet.amount
                    teams_bets[event_team.team.id]["won_coin"] += bet.amount
            elif bet_type == BetType.winner_first_card:
                event_team = teams[bet.event_team_id]
                if bet.currency == Currency.usdt:
                    won_first_map_total_usdt += bet.amount
                    teams_bets[event_team.team.id]["won_first_map_usdt"] += bet.amount
                else:
                    won_first_map_total_coin += bet.amount
                    teams_bets[event_team.team.id]["won_first_map_coin"] += bet.amount
            elif bet_type == BetType.winner_second_card:
                event_team = teams[bet.event_team_id]
                if bet.currency == Currency.usdt:
                    won_second_map_total_usdt += bet.amount
                    teams_bets[event_team.team.id]["won_second_map_usdt"] += bet.amount
                else:
                    won_second_map_total_coin += bet.amount
                    teams_bets[event_team.team.id]["won_second_map_coin"] += bet.amount
            elif bet_type == BetType.dry_bill:
                if bet.currency == Currency.usdt:
                    if bet.bet is True:
                        dry_bill_win_usdt += bet.amount
                    else:
                        dry_bill_loss_usdt += bet.amount
                else:
                    if bet.bet is True:
                        dry_bill_win_coin += bet.amount
                    else:
                        dry_bill_loss_coin += bet.amount
            else:
                if bet.currency == Currency.usdt:
                    if bet.bet is True:
                        knife_win_usdt += bet.amount
                    else:
                        knife_loss_usdt += bet.amount
                else:
                    if bet.bet is True:
                        knife_win_coin += bet.amount
                    else:
                        knife_loss_coin += bet.amount
        for bet in bets:
            bet_type = bet.bet_type
            if bet_type == BetType.win:
                if teams.get(bet.event_team_id).team.id == won:
                    # Ставка сыграла
                    if bet.currency == Currency.usdt:
                        price = int(bet.amount / teams_bets[won]["won_usdt"] * won_total_usdt)
                    else:
                        price = int(bet.amount / teams_bets[won]["won_coin"] * won_total_coin)
                    await uow.user.change_balance(user_id=bet.user_id, currency=bet.currency, value=price)
                    await bet_message(
                        user_id=bet.user_id,
                        win=True,
                        team_one=team_one,
                        team_two=team_two,
                        score_one=score_one,
                        score_two=score_two,
                        price=price,
                        currency=bet.currency
                    )
                else:
                    # Ставка проиграна
                    await bet_message(
                        user_id=bet.user_id,
                        win=False,
                        team_one=team_one,
                        team_two=team_two,
                        score_one=score_one,
                        score_two=score_two,
                    )
            elif bet_type == BetType.winner_first_card:
                if teams.get(bet.event_team_id).team.id == won_first_map:
                    # Ставка сыграла
                    if bet.currency == Currency.usdt:
                        price = int(bet.amount / teams_bets[won_first_map]["won_first_map_usdt"] * won_first_map_total_usdt)
                    else:
                        price = int(bet.amount / teams_bets[won_first_map]["won_first_map_coin"] * won_first_map_total_coin)
                    await uow.user.change_balance(user_id=bet.user_id, currency=bet.currency, value=price)
                    await bet_message(
                        user_id=bet.user_id,
                        win=True,
                        team_one=team_one,
                        team_two=team_two,
                        score_one=score_one,
                        score_two=score_two,
                        price=price,
                        currency=bet.currency
                    )
                else:
                    # Ставка проиграна
                    await bet_message(
                        user_id=bet.user_id,
                        win=False,
                        team_one=team_one,
                        team_two=team_two,
                        score_one=score_one,
                        score_two=score_two,
                    )
            elif bet_type == BetType.winner_second_card:
                if teams.get(bet.event_team_id).team.id == won_second_map:
                    # Ставка сыграла
                    if bet.currency == Currency.usdt:
                        price = int(bet.amount / teams_bets[won_second_map]["won_second_map_usdt"] * won_second_map_total_usdt)
                    else:
                        price = int(bet.amount / teams_bets[won_second_map]["won_second_map_coin"] * won_second_map_total_coin)
                    await uow.user.change_balance(user_id=bet.user_id, currency=bet.currency, value=price)
                    await bet_message(
                        user_id=bet.user_id,
                        win=True,
                        team_one=team_one,
                        team_two=team_two,
                        score_one=score_one,
                        score_two=score_two,
                        price=price,
                        currency=bet.currency
                    )
                else:
                    # Ставка проиграна
                    await bet_message(
                        user_id=bet.user_id,
                        win=False,
                        team_one=team_one,
                        team_two=team_two,
                        score_one=score_one,
                        score_two=score_two,
                    )
            elif bet_type == BetType.dry_bill:
                if bet.bet == dry_bill:
                    # Ставка сыграла
                    if bet.currency == Currency.usdt:
                        total_dry_bill = dry_bill_win_usdt + dry_bill_loss_usdt
                        if bet.bet is True:
                            price = int(bet.amount / dry_bill_win_usdt * total_dry_bill)
                        else:
                            price = int(bet.amount / dry_bill_loss_usdt * total_dry_bill)
                    else:
                        total_dry_bill = dry_bill_win_coin + dry_bill_loss_coin
                        if bet.bet is True:
                            price = int(bet.amount / dry_bill_win_coin * total_dry_bill)
                        else:
                            price = int(bet.amount / dry_bill_loss_coin * total_dry_bill)
                    await uow.user.change_balance(user_id=bet.user_id, currency=bet.currency, value=price)
                    await bet_message(
                        user_id=bet.user_id,
                        win=True,
                        team_one=team_one,
                        team_two=team_two,
                        score_one=score_one,
                        score_two=score_two,
                        price=price,
                        currency=bet.currency
                    )
                else:
                    # Ставка проиграна
                    await bet_message(
                        user_id=bet.user_id,
                        win=False,
                        team_one=team_one,
                        team_two=team_two,
                        score_one=score_one,
                        score_two=score_two,
                    )
            else:
                if bet.bet == knife:
                    # Ставка сыграла
                    if bet.currency == Currency.usdt:
                        total_knife = knife_win_usdt + knife_loss_usdt
                        if bet.bet is True:
                            price = int(bet.amount / knife_win_usdt * total_knife)
                        else:
                            price = int(bet.amount / knife_loss_usdt * total_knife)
                    else:
                        total_knife = knife_win_coin + knife_loss_coin
                        if bet.bet is True:
                            price = int(bet.amount / knife_win_coin * total_knife)
                        else:
                            price = int(bet.amount / knife_loss_coin * total_knife)
                    await uow.user.change_balance(user_id=bet.user_id, currency=bet.currency, value=price)
                    await bet_message(
                        user_id=bet.user_id,
                        win=True,
                        team_one=team_one,
                        team_two=team_two,
                        score_one=score_one,
                        score_two=score_two,
                        price=price,
                        currency=bet.currency
                    )
                else:
                    # Ставка проиграна
                    await bet_message(
                        user_id=bet.user_id,
                        win=False,
                        team_one=team_one,
                        team_two=team_two,
                        score_one=score_one,
                        score_two=score_two,
                    )
        await uow.commit()