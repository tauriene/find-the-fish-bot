import json

from redis.asyncio import Redis


class RedisRepo:
    def __init__(self, redis: Redis):
        self.redis = redis

    def _game_key(self, tg_id: int) -> str:
        return f"game:{tg_id}"

    async def save_game(self, tg_id: int, data: dict) -> None:
        data_json = json.dumps(data)
        await self.redis.set(self._game_key(tg_id), data_json, ex=300)

    async def get_game(self, tg_id: int) -> dict | None:
        game = await self.redis.get(self._game_key(tg_id))

        if game:
            game = json.loads(game)
        return game

    async def delete_game(self, tg_id: int) -> None:
        await self.redis.delete(self._game_key(tg_id))

    async def exists(self, tg_id: int) -> bool:
        return await self.redis.exists(self._game_key(tg_id))
