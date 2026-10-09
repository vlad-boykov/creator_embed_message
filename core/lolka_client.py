import asyncio
import threading

import lolka
from PyQt6.QtCore import QThread, pyqtSignal


class LolkaClient(lolka.Client):
    def __init__(self, worker: "LolkaWorker"):
        intents = lolka.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.worker = worker

    async def on_ready(self):
        guilds = []
        for guild in self.guilds:
            channels = []
            for channel in getattr(guild, "text_channels", []):
                channels.append({"id": str(channel.id), "name": channel.name})
            guilds.append({"id": str(guild.id), "name": guild.name, "channels": channels})
        self.worker.ready.emit(guilds)


class LolkaWorker(QThread):
    ready = pyqtSignal(object)
    connection_error = pyqtSignal(str)
    disconnected = pyqtSignal()
    publish_error = pyqtSignal(str)
    published = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.loop = None
        self.client = None
        self._lock = threading.Lock()
        self._pending_token = ""

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        if self._pending_token:
            self.loop.create_task(self._connect(self._pending_token))
            self._pending_token = ""
        self.loop.run_forever()
        pending = asyncio.all_tasks(self.loop)
        for task in pending:
            task.cancel()
        if pending:
            self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        self.loop.close()

    def _submit(self, coro):
        if self.loop is None:
            return None
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def connect_token(self, token: str):
        if not self.isRunning():
            self._pending_token = token
            self.start()
        else:
            self._submit(self._connect(token))

    async def _connect(self, token: str):
        try:
            if self.client is not None:
                await self.client.close()
            self.client = LolkaClient(self)
            asyncio.create_task(self.client.start(token))
            await asyncio.sleep(0.1)
        except Exception as exc:
            self.connection_error.emit(self._friendly_error(exc))

    def disconnect_client(self):
        if self.loop:
            self._submit(self._disconnect())

    async def _disconnect(self):
        if self.client:
            try:
                await self.client.close()
            except Exception:
                pass
        self.disconnected.emit()

    def publish(self, guild_id: str, channel_id: str, embeds):
        if self.loop is None or self.client is None:
            self.publish_error.emit("Сначала подключите бота.")
            return
        self._submit(self._publish(guild_id, channel_id, embeds))

    async def _publish(self, guild_id: str, channel_id: str, embeds):
        try:
            guild = self.client.get_guild(int(guild_id))
            if guild is None:
                raise RuntimeError("Сервер не найден или бот больше не имеет к нему доступа.")
            channel = guild.get_channel(int(channel_id))
            if channel is None:
                raise RuntimeError("Канал не найден.")
            await channel.send(embeds=embeds)
            self.published.emit()
        except Exception as exc:
            self.publish_error.emit(self._friendly_error(exc))

    @staticmethod
    def _friendly_error(exc: Exception) -> str:
        message = str(exc).strip()
        if not message:
            return exc.__class__.__name__
        return message[:400]

    def shutdown(self):
        if self.loop:
            self._submit(self._disconnect())
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.wait(3000)
