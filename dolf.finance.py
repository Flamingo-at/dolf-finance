import json
import asyncio
import aiohttp

from loguru import logger
from aiohttp import ClientSession
from random import choice, randint
from aiohttp_proxy import ProxyConnector
from pyuseragents import random as random_useragent


def random_tor_proxy():
    proxy_auth = str(randint(1, 0x7fffffff)) + ':' + \
        str(randint(1, 0x7fffffff))
    proxies = f'socks5://{proxy_auth}@localhost:' + str(choice(tor_ports))
    return(proxies)


def get_connector():
    connector = ProxyConnector.from_url(random_tor_proxy())
    return(connector)


async def create_email(client: ClientSession):
    try:
        response = await client.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
        email = (await response.json())[0]
        return email
    except:
        logger.error("Failed to create email")
        await asyncio.sleep(1)
        return(await create_email(client))


def dolf_id(count: int):
    return(''.join([choice('1234567890abcdef') for _ in range(count)]))


async def worker():
    while True:
        try:
            async with aiohttp.ClientSession(
                connector=get_connector(),
                headers={
                    'accept': 'application/json',
                    'x-dolf-request-id': f'{dolf_id(8)}-{dolf_id(4)}-{dolf_id(4)}-{dolf_id(4)}-{dolf_id(12)}',
                    'user-agent': random_useragent()
                }
            ) as client:

                email = await create_email(client)

                logger.info('Registration')
                response = await client.post('https://apiserver.dolf.finance/prod/referral',
                                             json={
                                                 "email": email,
                                                 "referralCode": ref
                                             })
                referral_code = (await response.json())['data']['referral_code']

        except Exception:
            logger.error("Error\n")
        else:   
            with open('registered.txt', 'a', encoding='utf-8') as file:
                file.write(f'{email}:{referral_code}\n')
            logger.success('Successfully\n')

        await asyncio.sleep(delay)


async def main():
    tasks = [asyncio.create_task(worker()) for _ in range(threads)]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    tor_ports = [9150]

    print("Bot Dolf finance @flamingoat\n")

    ref = 'UN9IJP'
    delay = 0
    threads = 1

    # ref = input('Referral code: ')
    # delay = int(input('Delay(sec): '))
    # threads = int(input('Threads: '))

    asyncio.run(main())
