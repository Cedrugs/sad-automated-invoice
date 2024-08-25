from utils import Sheets, Checker

import logging
import contextlib
import asyncio

logger = logging.getLogger()

@contextlib.contextmanager
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    try:
        dt_fmt = '%Y/%m/%d %H:%M:%S'
        fmt = logging.Formatter('{asctime} {levelname:<7} {name}: {message}', dt_fmt, style='{')
        logging.getLogger("utils").setLevel(logging.INFO)

        file_hdlr = logging.FileHandler(
            filename='./logs/log.txt',
            encoding="utf-8",
            mode='w'
        )
        file_hdlr.setFormatter(fmt)
        logger.addHandler(file_hdlr)

        console_hdlr = logging.StreamHandler()
        console_hdlr.setFormatter(fmt)
        logger.addHandler(console_hdlr) 

        yield
    finally:
        handlers = logger.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            logger.removeHandler(hdlr)


async def main():
    logger.info("SAD Automated Invoice is running")
    
    try:
        insert_to_db = asyncio.create_task(Sheets(sheets_id='xx').insert_to_db())
        check_for_unsent = asyncio.create_task(Checker().check_for_unsent())

        await insert_to_db
        await check_for_unsent
    except Exception as exc:
        logger.critical(exc)


if __name__ == "__main__":
    with setup_logging():
        asyncio.run(main())