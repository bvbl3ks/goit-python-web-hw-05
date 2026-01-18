import aiohttp
import asyncio
from datetime import datetime, timedelta
import sys

class PrivatBankAPI:
    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

    async def get_exchange(self, session, date_str: str):
        url = f"{self.BASE_URL}{date_str}"
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return {"error": f"Status {resp.status} for {date_str}"}
                data = await resp.json()
                return self._filter_currency(data)
        except aiohttp.ClientError as e:
            return {"error": str(e)}

    def _filter_currency(self, data):
        result = {}
        for item in data.get("exchangeRate", []):
            if item.get("currency") in ["USD", "EUR"]:
                result[item["currency"]] = {
                    "sale": item.get("saleRate", item.get("sale")),
                    "purchase": item.get("purchaseRate", item.get("purchase"))
                }
        return result

async def fetch_last_days(n_days: int):
    if n_days > 10:
        n_days = 10
    api = PrivatBankAPI()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(n_days):
            day = datetime.now() - timedelta(days=i)
            date_str = day.strftime("%d.%m.%Y")
            tasks.append(api.get_exchange(session, date_str))
        results = await asyncio.gather(*tasks)
        output = []
        for i, day in enumerate(results):
            output.append({(datetime.now() - timedelta(days=i)).strftime("%d.%m.%Y"): day})
        return output

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <number_of_days>")
        sys.exit(1)
    try:
        n_days = int(sys.argv[1])
    except ValueError:
        print("Please enter a valid integer for number of days.")
        sys.exit(1)

    result = asyncio.run(fetch_last_days(n_days))
    print(result)

if __name__ == "__main__":
    main()
