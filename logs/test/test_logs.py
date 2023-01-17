import io
import re
import aiohttp
import pytest
from pathlib import Path
from contextlib import redirect_stdout
from logs.logs import logs


async def async_generator(values):
    for value in values:
        yield value


class AsyncMockPlug:
    def __init__(self):
        ...

    async def __aexit__(self, exc_type, exc, tb):
        ...

    async def __aenter__(self):
        return self


class AsyncMockResponse(AsyncMockPlug):
    _content = None

    def __init__(self):
        super().__init__()

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value


class AsyncMockSession(AsyncMockPlug):
    url = None

    def get(self, *args, **kwargs):
        self.__class__.url = args[0] if args else None
        return AsyncMockResponse()


class TestClass:
    testdata = [
        ('test', [str(value) for value in range(10)])
    ]

    async def _call_logs(self, mocker, cont = '', name = '', values = []):
        AsyncMockResponse.content = async_generator(values=values)
        conn = AsyncMockPlug()
        session = AsyncMockSession()

        async with (mocker.patch('aiohttp.UnixConnector', return_value=conn),
                    mocker.patch('aiohttp.ClientSession', return_value=session)):
            await logs(cont, name)


    @pytest.mark.asyncio
    @pytest.mark.parametrize("name, values", testdata)
    async def test_logs_output(self, name, values, mocker):
        with io.StringIO() as buf, redirect_stdout(buf):
            await self._call_logs(name=name, values=values, mocker=mocker)
            result_values = buf.getvalue().strip().split('\n')
            for idx, value in enumerate(result_values):
                assert value == f'{name} {values[idx]}'

    @pytest.mark.asyncio
    async def test_logs_connector_sock_exists(self, mocker):
        with io.StringIO() as buf, redirect_stdout(buf):
            await self._call_logs(mocker=mocker)
            call = str(aiohttp.UnixConnector.mock_calls[1])
            path = re.sub(r".*path='(\/.+)'.*", r'\g<1>', call)
            assert Path(path).exists()

    @pytest.mark.asyncio
    async def test_logs_cont_interpolated(self, mocker):
        cont = 'test_cont'
        url = f'http://xx/containers/{cont}/logs?follow=1&stdout=1'
        with io.StringIO() as buf, redirect_stdout(buf):
            await self._call_logs(mocker=mocker, cont=cont)
            assert AsyncMockSession.url == url
