import asyncio
import aiohttp
from src.skins.schemas import StatusRes

# key = '2mCGzxa9U56vjct0QJQ07f1jEVV4At3'
# name = "P250 | Facility Draft (Factory New)"
# trade = "https://steamcommunity.com/tradeoffer/new/?partner=279067858&token=4v70Y47S"

async def search_skins(hash_name: str, key_market: str) -> list[dict[str, int]]:
    url = "https://market.csgo.com/api/v2/search-item-by-hash-name-specific"
    params = {
        "key": key_market,
        "hash_name": hash_name,
        "with_stickers": 1
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                res = await response.json()
                if res["success"] is False:
                    return []
                count, result = 0, []
                for i in res["data"]:
                    if count > 5:
                        break
                    result.append({"id": i["id"], "price": i["price"]})
                    count += 1
                return result
        except aiohttp.ClientError:
            return []


async def buy_skin(data: dict[str, int], partner: str | int, token: str, custom_id: str, key_market: str) -> StatusRes:
    url = "https://market.csgo.com/api/v2/buy-for"
    params = {
        "key": key_market,
        "id": data["id"],
        "price": data["price"],
        "partner": partner,
        "token": token,
        "custom_id": custom_id
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                res = await response.json()
                if res["success"] is False:
                    if res["error"] == 'Not money':
                        return StatusRes.no_money
                    elif res["error"] == 'need argument: token' or res["error"] == 'Неверная ссылка для обмена':
                        return StatusRes.no_validated_trade_url
                    else:
                        return StatusRes.didnt_buy
                return StatusRes.success
        except aiohttp.ClientError:
            return StatusRes.didnt_buy
        except Exception as e:
            print(e)
            return StatusRes.unknown_error


async def get_info(rec_id: str | int, key_market: str) -> str | bool:
    url = "https://market.csgo.com/api/v2/get-buy-info-by-custom-id"
    params = {"key": key_market, "custom_id": f"CS2LimitedBOT_{rec_id}"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                res = await response.json()
                if res["success"] is False:
                    return False
                return res["data"]["stage"]
        except aiohttp.ClientError:
            return False


async def main(key_market: str, hash_name: str, trade_url: str, receiving_id: int) -> StatusRes:
    try:
        skins = await search_skins(hash_name=hash_name, key_market=key_market)
        if not skins:
            return StatusRes.no_skins
        partner, token = [i.split("=")[-1] for i in trade_url.split("?")[-1].split("&")]
        custom_id = f"CS2LimitedBOT_{receiving_id}"
        last = StatusRes.unknown_error
        for skin in skins:
            buy = await buy_skin(skin, partner=partner, token=token, custom_id=custom_id, key_market=key_market)
            if buy == StatusRes.no_money or buy == StatusRes.no_validated_trade_url:
                return buy
            if buy == StatusRes.success:
                return buy
            last = buy
        return last
    except Exception as e:
        print(e)
        return StatusRes.unknown_error


#print(asyncio.run(main(key_market=key, hash_name=name, trade_url=trade, receiving_id=1)))
#print(asyncio.run(get_info(key_market=key, custom_id="CS2LimitedBOT_1")))
#print(asyncio.run(search_skins(hash_name=name, key_market=key)))
#print(asyncio.run(buy_skin(data={'id': 5840114182, 'price': 1}, partner=279067858, token="4v70Y47S", custom_id="CS2LimitedBOT6", key_market=key)))