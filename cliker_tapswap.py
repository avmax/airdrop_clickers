import random
import pendulum

# import pika
from playwright.async_api import Page, TimeoutError, async_playwright, expect
import asyncio
from datetime import timedelta
import hashlib
import time

import logging
from getuseragent import UserAgent
import numpy as np

useragent = UserAgent("android")


class TelegramClickerTemplate:
    def __init__(self) -> None:
        self.loop = asyncio.get_event_loop()

    def provide_ref_url(self, project: str, ref_url: str, user_id = -1) -> None:
        print(f"provide_ref_url:{project}:{ref_url}")

    # СЮДА ВСТАВЛЯТЬ КОД
    async def handler_game(self, page: Page, params: dict, logger: logging.Logger):
        await page.goto(params["url"], timeout=60000)
        start = time.time()
        boosters_awailable = True
        # Game loop
        while True:
            balance_info = page.locator('css=[class*="balanceInfo"]')
            balance = int(
                (await balance_info.locator("h1").text_content()).replace(" ", "")
            )

            bottom_content = page.locator('css=[class*="bottomContent"]')
            current_energy = int(
                (await bottom_content.locator("h4").text_content())
                .replace(" ", "")
                .replace("/", "")
            )
            total_energy = int(
                (await bottom_content.locator("h6").text_content())
                .replace(" ", "")
                .replace("/", "")
            )
            print(f"[tapswap]:{current_energy}/{total_energy}|{balance}")

            if time.time() - start > 10:
                await asyncio.sleep(random.random() * 10 / 2.0)
                start = time.time()

            await asyncio.sleep(np.random.gamma(1, 0.012 / 2.0))

            main_button = page.locator('css=[class*="tapContent"]')
            for i in range(random.randint(1, 5)):
                await main_button.tap()

            if current_energy < 50:
                if boosters_awailable:
                    print("[tapswap]:boosters check")
                    await page.locator("button", has_text="Boost").tap()
                    # taping_guru = page.locator("button", has_text="Taping Guru")
                    full_tank = page.locator("button", has_text="Full Tank")
                    # if not (await taping_guru.is_disabled()):
                    #     print("[tapswap]:boosters:taping_guru")
                    #     await taping_guru.tap()
                    #     await page.locator("button", has_text="Get it!").tap()
                    #     continue
                    if not (await full_tank.is_disabled()):
                        print("[tapswap]:boosters:full_tank")
                        await full_tank.tap()
                        await page.locator("button", has_text="Get it!").tap()
                        continue
                    else:
                        await page.get_by_role(
                            "button", name="navigation button Tap"
                        ).tap()
                        boosters_awailable = False
                break
        # Shop loop
        await page.locator("button", has_text="Boost").click()
        await asyncio.sleep(5)
        while True:
            print("[tapswap]:shop_loop")
            balance = int(
                (
                    await page.locator(
                        'css=[class*="balanceBoxContainer"]',
                        has_text="Your Share balance",
                    )
                    .locator("h1")
                    .text_content()
                ).replace(" ", "")
            )
            items = await page.locator('css=[class*="listItem"]').all()
            item_purchased = False
            for item in items:
                name = await item.locator('css=[class*="name"]').text_content()
                price = int(
                    (
                        await item.locator('css=[class*="balance"]').text_content()
                    ).replace(" ", "")
                )
                print(f"[tapswap]:shop_loop:{name}-{price}|{balance}")
                if price < balance and price < 250000:
                    print(f"[tapswap]:shop_loop:buy {name}")
                    await asyncio.sleep(2)
                    await item.tap()
                    await asyncio.sleep(2)
                    await page.locator("button", has_text="Get it!").tap()
                    await asyncio.sleep(5)
                    item_purchased = True
                    break
            if item_purchased:
                continue
            break
        # Bonus loop
        await page.locator("button", has_text="Task").tap()

        await page.locator("button", has_text="Leagues").tap()
        for item in await page.locator('css=[class*="listItem"]').all():
            button = item.locator("button")
            if not await button.is_disabled():
                name = await item.locator('css=[class*="name"]').text_content()
                print(f"[tapswap]:bonus_loop:got bonus {name}")
                await button.tap()
                await asyncio.sleep(2)

        await page.locator("button", has_text="Ref Tasks").tap()
        for item in await page.locator('css=[class*="listItem"]').all():
            button = item.locator("button")
            if not await button.is_disabled():
                name = await item.locator('css=[class*="name"]').text_content()
                print(f"[tapswap]:bonus_loop:got bonus {name}")
                await button.tap()
                await asyncio.sleep(2)
        print("[tapswap]:done")

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
        "account_uuid":'565fd31a-bef2-495a-bf49-8016dd4ea722',
        "active": True,
        "url": "https://app.tapswap.club/?bot=app_bot_1#tgWebAppData=query_id%3DAAG_2RkkAwAAAL_ZGSQK-NEy%26user%3D%257B%2522id%2522%253A7048124863%252C%2522first_name%2522%253A%2522Lucas%2522%252C%2522last_name%2522%253A%2522Girard%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522allows_write_to_pm%2522%253Atrue%257D%26auth_date%3D1715110182%26hash%3Dd745ab69e79c15a07657344603533dd649864de2f0147841f4b10779b4690e8a&tgWebAppVersion=7.2&tgWebAppPlatform=android&tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23ffffff%22%2C%22section_bg_color%22%3A%22%23ffffff%22%2C%22secondary_bg_color%22%3A%22%23f0f0f0%22%2C%22text_color%22%3A%22%23222222%22%2C%22hint_color%22%3A%22%23a8a8a8%22%2C%22link_color%22%3A%22%232678b6%22%2C%22button_color%22%3A%22%2350a8eb%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22header_bg_color%22%3A%22%23527da3%22%2C%22accent_text_color%22%3A%22%231c93e3%22%2C%22section_header_text_color%22%3A%22%233a95d5%22%2C%22subtitle_text_color%22%3A%22%2382868a%22%2C%22destructive_text_color%22%3A%22%23cc2929%22%7D"
}
    clicker = TelegramClickerTemplate()
    await clicker.handler(params=params)


if __name__ == "__main__":
    asyncio.run(main())
