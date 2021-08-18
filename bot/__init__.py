import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import PickleStorage
import dotenv


# Load dotenv
dotenv.load_dotenv()

bot = Bot(token=os.getenv("API_TOKEN"))
storage = PickleStorage("db.pickle")
dp = Dispatcher(bot, storage=storage)
