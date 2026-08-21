"""
Ponte síncrona para o aiograpi (fork assíncrono do instagrapi).

O InstaFlow é um aplicativo majoritariamente síncrono (usa threads,
ThreadPoolExecutor e APScheduler BackgroundScheduler). O aiograpi, por outro
lado, expõe todos os métodos de rede como corrotinas ``async``.

Para migrar para o aiograpi sem reescrever toda a base de código para
async/await, este módulo fornece ``Client``: um invólucro fino que executa um
event loop asyncio dedicado em uma thread de fundo e converte automaticamente
qualquer método corrotina do cliente aiograpi em uma chamada bloqueante
comum.

Assim, todo o restante do projeto continua chamando ``cl.login(...)``,
``cl.clip_upload(...)``, ``cl.user_info(...)`` etc. exatamente como fazia com o
instagrapi — mas por baixo dos panos quem executa é o aiograpi.
"""
from __future__ import annotations

import asyncio
import inspect
import threading
from typing import Any, Optional

from aiograpi import Client as AioClient

__all__ = ["Client"]


class Client:
    """Invólucro síncrono ao redor de :class:`aiograpi.Client`.

    Qualquer atributo/método que não pertença a esta ponte é delegado ao
    cliente aiograpi subjacente. Métodos corrotina são executados no event loop
    de fundo e o resultado é retornado de forma bloqueante, imitando a API
    síncrona do instagrapi.
    """

    # Atributos que pertencem à própria ponte (não são delegados ao aiograpi).
    _BRIDGE_ATTRS = frozenset({"_loop", "_thread", "_client"})

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        loop = asyncio.new_event_loop()
        thread = threading.Thread(
            target=loop.run_forever,
            name="aiograpi-loop",
            daemon=True,
        )
        thread.start()
        object.__setattr__(self, "_loop", loop)
        object.__setattr__(self, "_thread", thread)

        # A criação do AioClient em si não é uma corrotina, mas fazemos isso
        # dentro do loop para garantir que qualquer estado atrelado ao loop
        # (ex.: locks asyncio) seja criado no loop correto.
        client = self._run(self._build_client(*args, **kwargs))
        object.__setattr__(self, "_client", client)

    @staticmethod
    async def _build_client(*args: Any, **kwargs: Any) -> AioClient:
        return AioClient(*args, **kwargs)

    def _run(self, coro):
        """Executa uma corrotina no loop de fundo e bloqueia até o resultado."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()

    # ------------------------------------------------------------------
    # Delegação de atributos
    # ------------------------------------------------------------------
    def __getattr__(self, name: str) -> Any:
        # __getattr__ só é chamado quando o atributo não existe na ponte,
        # então delegamos tudo ao cliente aiograpi.
        client = object.__getattribute__(self, "_client")
        attr = getattr(client, name)

        if inspect.iscoroutinefunction(attr):

            def _sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                return self._run(attr(*args, **kwargs))

            _sync_wrapper.__name__ = getattr(attr, "__name__", name)
            _sync_wrapper.__doc__ = getattr(attr, "__doc__", None)
            return _sync_wrapper

        return attr

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self._BRIDGE_ATTRS:
            object.__setattr__(self, name, value)
            return
        # Delega a escrita de atributos ao cliente aiograpi (ex.: settings,
        # authorization_data, username, challenge_code_handler).
        setattr(self._client, name, value)

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------
    def close(self) -> None:
        """Encerra o event loop de fundo de forma limpa."""
        loop = object.__getattribute__(self, "_loop")
        thread = object.__getattribute__(self, "_thread")
        try:
            loop.call_soon_threadsafe(loop.stop)
            thread.join(timeout=5)
        except Exception:
            pass

    def __del__(self) -> None:  # pragma: no cover - melhor esforço
        try:
            self.close()
        except Exception:
            pass


def as_async_handler(sync_fn):
    """Adapta um callable síncrono para o ``challenge_code_handler`` async.

    O aiograpi invoca ``await self.challenge_code_handler(username, choice)``,
    portanto o handler precisa ser uma corrotina. Este utilitário embrulha uma
    função síncrona (que pode bloquear aguardando o código 2FA/checkpoint)
    executando-a em um executor de thread para não travar o event loop.
    """

    async def _handler(username: str, choice: Optional[Any] = None, **kwargs: Any):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: sync_fn(username, choice))

    return _handler
