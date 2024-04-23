from bybit_release import main as bybit
from bybit_release.config import *
import asyncio


asyncio.run(bybit.start(API_KEY, SECRET_KEY, float(10000)))