import random
import pendulum

# import pika
from playwright.async_api import Page, TimeoutError, async_playwright, expect, Locator
import asyncio
from datetime import timedelta
import hashlib
import time
import threading
from typing import List

import logging
from getuseragent import UserAgent
import numpy as np

useragent = UserAgent("android")


class TelegramClickerTemplate:
    def __init__(self) -> None:
        self.loop = asyncio.get_event_loop()

    def provide_ref_url(self, project: str, ref_url: str) -> None:
        print(f"provide_ref_url:{project}:{ref_url}")

    # КОД КЛИКЕРА (ПИШЕМ КОД НИЖЕ ЭТОЙ СТРОКИ)

    async def load_state(self, page: Page) -> None:
        await page.get_by_text("Earn").click() # Переходим на вкладку Earn
        await asyncio.sleep(2) # Ждем пока прогрузится страница
        await self.load_money_current_balance(page)
        await self.load_vault_current_capacity(page)
        await self.load_vault_current_filled_percent(page)
        await self.load_paper_current_balance(page)
        await self.load_paper_is_empty(page)
        await self.load_paper_current_limit(page)
        await self.load_paper_available_pack_offers(page)

    async def load_money_current_balance(self, page: Page) -> float:
        await page.get_by_text("Earn").click() # Переходим на вкладку Earn
        self.money_current_balance = float((await page.locator('[class*="_money_1"]').text_content()).split(" ")[0])
        print(f"[brrrrr]:money_current_balance: {self.money_current_balance}")
        return self.money_current_balance
    
    async def load_vault_current_capacity(self, page: Page) -> int:
        await page.get_by_text("Boosts").click() # Переходим на вкладку Boosts
        await asyncio.sleep(1) # Ждем пока прогрузится страница
        booster_available_locators = await page.locator('[class*="_booster_item"]').all()
        booster_expand_vault: Locator = booster_available_locators[1] #этот бустер 2ой в списке (1ый в массиве)
        self.vault_current_capacity = int((await booster_expand_vault.locator('[class*="_convert"]').text_content()).split('-')[0].split(' ')[0])
        print(f"[brrrrr]:vault_current_capacity: {self.vault_current_capacity}")
        await page.get_by_text("Earn").click() # Возвращаемся на вкладку Earn
        return self.vault_current_capacity
    
    async def load_vault_current_filled_percent(self, page: Page) -> int:
        await page.get_by_text("Earn").click() # Переходим на вкладку Earn
        self.vault_filled_percent = int((await page.locator('h3[class*="_progress"]').text_content()).replace("%", ""))
        self.vault_is_full = self.vault_filled_percent == 100
        print(f"[brrrrr]:vault_filled_percent: {self.vault_filled_percent}")
        print(f"[brrrrr]:vault_is_full: {self.vault_is_full}")
        return self.vault_filled_percent

    async def load_paper_current_balance(self, page: Page) -> float:
        await page.get_by_text("Earn").click() # Переходим на вкладку Earn
        self.paper_current_balance = float((await page.locator('[class^="_paper_wrap"] > h3').text_content()).split('/')[0].replace(",", ""))
        print(f"[brrrrr]:paper_current_balance: {self.paper_current_balance}")
        return self.paper_current_balance

    async def load_paper_is_empty(self, page: Page) -> bool:
        await page.get_by_text("Earn").click() # Переходим на вкладку Earn
        self.paper_is_empty = self.paper_current_balance == 0.00
        print(f"[brrrrr]:paper_is_empty: {self.paper_is_empty}")
        return self.paper_is_empty

    async def load_paper_current_limit(self, page: Page) -> int:
        await page.get_by_text("Earn").click() # Переходим на вкладку Earn
        self.paper_current_limit = int((await page.locator('[class^="_paper_wrap"] > h3').text_content()).split('/')[1].replace(",", ""))
        print(f"[brrrrr]:paper_current_limit: {self.paper_current_limit}")
        return self.paper_current_limit
    
    async def load_paper_available_pack_offers(self, page: Page) -> List[dict]:
        await page.get_by_text("Earn").click() # Переходим на вкладку Earn
        await page.get_by_text("Buy more").click() # Открываем модалку с офферами бумаг
        await asyncio.sleep(1) # Ждем пока прогрузится страница

        available_paper_pack_offer_locators = await page.locator('[class*="_paper_item"]').all()
        self.paper_available_pack_offers = []

        pack: Locator
        for pack in available_paper_pack_offer_locators:
            self.paper_available_pack_offers.append({
                "papers": int((await pack.locator('[class*=_item_subtitle]').text_content()).split(" ")[0].replace(",", "")),
                "price": int((await pack.locator('[class*=_item_value]').text_content()).split(" ")[0].replace(",", ""))
            })

        await page.get_by_text("Earn").click() # Закрываем модалку с офферами бумаг

        print(f"[brrrrr]:paper_available_pack_offers: offers loaded!")
        return self.paper_available_pack_offers

    async def action_buy_paper(self, page: Page) -> None:
        print("[brrrrr]: action buy paper!")
        paper_pack_offer_index = 0 # Номер оффера, который хотим купить. По умолчанию покупаем первый (самый дешевый) пакет

        for index, paper_pack_offer in enumerate(self.paper_available_pack_offers):  # Выбираем подходящий оффер
            if (
                self.money_current_balance < paper_pack_offer["price"]
                or (self.paper_current_balance + paper_pack_offer["price"] > self.paper_current_limit)
            ):
                paper_pack_offer_index = max(0, index - 1)
                print(f"self.money_current_balance: {self.money_current_balance} < {paper_pack_offer["price"]} paper_pack_offer[price]")
                print(f"if! break {paper_pack_offer_index}")
                break

        await page.get_by_text("Earn").click() # Переходим на вкладку Earn
        await page.get_by_text("Buy more").click() # Открываем вкладку с офферами бумаг
        await asyncio.sleep(1) # Ждем пока прогрузится страница
        available_paper_pack_offer_locators = await page.locator('[class*="_paper_item"]').all() # Загружаем локаторы офферов
        
        paper_pack_offer_to_buy: Locator = available_paper_pack_offer_locators[paper_pack_offer_index] # Выбираем нужный оффер
        paper_pack_offer_to_buy_text = await paper_pack_offer_to_buy.text_content() # Сохраняем текст оффера в переменную
        await paper_pack_offer_to_buy.click() # Кликаем на выбранный оффер для его покупки
        await asyncio.sleep(1) # Ждем пока откроется модалка
        await page.get_by_text("Confirm").click() # Подтверждаем покупку оффера
        await asyncio.sleep(1) # Ждем пока прогрузится следующая модалка
        await page.locator('[class*="_info_btn"]').click() # Закрываем появившиюся модалку (какая бы она ни была)

        print(f"[brrrrr]: bought paper pack: {paper_pack_offer_to_buy_text}")

    async def action_buy_booster_improve_vault_capacity(self, page: Page) -> None:
        print("[brrrrr]: action buy booster: improve vault capacity!")
        await page.get_by_text("Boosts").click() # Переходим на вкладку Boosts
        await asyncio.sleep(1) # Ждем пока прогрузится страница
        booster_available_locators = await page.locator('[class*="_booster_item"]').all()
        await booster_available_locators[1].click() # Кликаем на бустер про увеличение размера сейфа(он 2ой в списке (1ый в массиве))
        await asyncio.sleep(1) # Ждем пока откроется модалка
        await page.locator('[class*="_info_btn"]').click() # кликаем на модалку с подтверждением намерения
        await asyncio.sleep(1) # Ждем пока прогрузится следующая модалка
        await page.locator('[class*="_info_btn"]').click() # Закрываем появившиюся модалку (какая бы она ни была)
        await page.get_by_text("Earn").click() # Возвращаемся на главную вкладку (Earn)

    async def action_buy_booster_improve_paper_storage_capacity(self, page: Page) -> None:
        print("[brrrrr]: action buy booster: improve paper storage capacity!")
        #TODO: прописать логику покупки бустера

    async def action_buy_booster_improve_printer(self, page: Page) -> None:
        print("[brrrrr]: action buy booster: improve printer!")
        #TODO: прописать логику покупки бустера

    async def action_buy_booster_improve_printing_speed(self, page: Page) -> None:
        print("[brrrrr]: action buy booster: improve printing speed!")
        #TODO: прописать логику покупки бустера

    async def handler_game(self, page: Page, params: dict, logger: logging.Logger):
        await page.goto(params["url"], timeout=60000)

        try: await page.get_by_role("button", name="START PRINTING").click()
        except TimeoutError: pass

        self.time_start = time.time()

        while (True):
            await self.load_state(page)
            if (self.paper_is_empty):
                print("[brrrrr]: paper is empty!")
                await self.action_buy_paper(page) # если бумага кончилась — закупаем бумагу
            elif (self.vault_is_full):
                print("[brrrrr]: vault is full!")
                await self.action_buy_paper(page) # если сейф переполнился — закупаем бумагу (тем самым опустошаем сейф)
                await self.action_buy_booster_improve_vault_capacity(page) # если сейф заполнился — попробовать купить бустер на увеличение сейфа
                # await self.action_buy_boost_paper_capacity(page) #TODO: если деньги остались — попробовать купить бустер на увеличение лотка с бумагой
                # await self.action_buy_booster_improve_printer(page) #TODO: если деньги остались — попробовать купить бустер на повышение эффективности принтера
                # await self.action_buy_booster_improve_printing_speed(page) #TODO: если деньги остались — попробовать купить бустер на повышение скорости печати
                await self.action_buy_paper(page) # если остались деньги — пробуем докупить еще бумаги
            else:
                continue

    # И ТОЛЬКО СЮДА  ^^^

    async def handler(self, params: dict):
        logger = logging.getLogger().getChild("worker")
        uuid_proxy_idx = int(
            hashlib.sha1(params["account_uuid"].encode("utf-8")).hexdigest(), 16
        ) % (10**12)

        async with async_playwright() as playwright:
            iphone_13 = playwright.devices["Pixel 7"]
            browser = await playwright.chromium.launch(
                headless=False,
                # proxy={
                #     "server": f"http://{address}:{port}",
                #     "username": username,
                #     "password": password,
                # },
            )
            iphone_13["user_agent"] = str(
                useragent.list[uuid_proxy_idx % len(useragent.list)]
            )  # account["useragent"]
            browser_context = await browser.new_context(**iphone_13)
            browser_context.set_default_timeout(60000)
            await browser_context.grant_permissions(
                ["clipboard-read", "clipboard-write"]
            )

            tasks = []
            page = await browser_context.new_page()
            await self.handler_game(page, params, logger)


async def main():
    params = {
        "account_uuid":'0158bb3d-4881-4829-84dd-9f907f6075ac',
        "active": True,
        "join_url": "8a92065a-9e88-45f9-b551-c0bbf8579f43",
        "ref_url": "https://t.me/brrrrrgamebot?start=663a3703dab1e6a9594fd98f",
        "updated_at": "2024-05-07T18:13:41.733766+04:00",
        "url": "https://brrrrr-app.massan.club/#tgWebAppData=query_id%3DAAEltKAhAwAAACW0oCEK_xf9%26user%3D%257B%2522id%2522%253A7006630949%252C%2522first_name%2522%253A%2522Simon%2522%252C%2522last_name%2522%253A%2522Dufour%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522allows_write_to_pm%2522%253Atrue%257D%26auth_date%3D1715091211%26hash%3D19ff6d0e95c7047f845ff97b6e051cd30d4861b0d54430290f6555040abf7c08&tgWebAppVersion=7.2&tgWebAppPlatform=android&tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23ffffff%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22secondary_bg_color%22%3A%22%23f0f0f0%22%2C%22text_color%22%3A%22%23222222%22%2C%22hint_color%22%3A%22%23a8a8a8%22%2C%22link_color%22%3A%22%232678b6%22%2C%22button_color%22%3A%22%2350a8eb%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22header_bg_color%22%3A%22%23527da3%22%2C%22accent_text_color%22%3A%22%231c93e3%22%2C%22section_header_text_color%22%3A%22%233a95d5%22%2C%22subtitle_text_color%22%3A%22%2382868a%22%2C%22destructive_text_color%22%3A%22%23cc2929%22%7D",
    }
    clicker = TelegramClickerTemplate()
    await clicker.handler(params=params)


if __name__ == "__main__":
    asyncio.run(main())
