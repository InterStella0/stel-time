from dotenv import load_dotenv

from core.bot import StelTime

load_dotenv()
bot = StelTime()
bot.running()
