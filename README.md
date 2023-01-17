# Тестовое задание: Webtronics 1

Распишите пример(ы) unit тестов на эту фнкцию:

    async def logs(cont, name):
        conn = aiohttp.UnixConnector(path="/var/run/docker.sock")
        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.get(f"http://xx/containers/{cont}/logs?follow=1&stdout=1") as resp:
                async for line in resp.content:
                    print(name, line)
