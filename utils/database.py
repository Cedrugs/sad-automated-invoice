from aiosqlite import connect as aioconnect, __version__


path = './database/database.db'
db_version = '0.5a'
aiosqlite = __version__


class Database:

    @staticmethod
    async def record(commands, *values, db_path=path):
        async with aioconnect(db_path) as db:
            items = await db.execute(commands, tuple(values))

            return await items.fetchone()

    @staticmethod
    async def recordall(commands, *values, db_path=path):
        async with aioconnect(db_path) as db:
            items = await db.execute(commands, tuple(values))

            return await items.fetchall()

    @staticmethod
    async def field(commands, *values, db_path=path):
        async with aioconnect(db_path) as db:
            items = await db.execute(commands, tuple(values))

            if (fetch := await items.fetchone()) is not None:
                return fetch[0]

    @staticmethod
    async def execute(commands, *values, db_path=path):
        async with aioconnect(db_path) as db:
            await db.execute(commands, tuple(values))

    @staticmethod
    async def autoexecute(commands, *values, db_path=path):
        async with aioconnect(db_path) as db:
            await db.execute(commands, tuple(values))
            await db.commit()

    @staticmethod
    async def column(commands, *values, db_path=path):
        async with aioconnect(db_path) as db:
            items = await db.execute(commands, tuple(values))

            return [item[0] for item in await items.fetchall()]

    @staticmethod
    async def commit(db_path=path):
        async with aioconnect(db_path) as db:
            await db.commit()