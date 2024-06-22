import asyncio
import os
import json


allowed_users = [348691698, 540862463, 925216062]


async def newreports(bot):
    while True:
        await asyncio.sleep(1)
        reports = os.listdir('./main/tgmsgs/')
        for report in reports:
            d = {}
            with open('./main/tgmsgs/' + report, 'rt') as f:
                d = json.loads(f.read())
            for u in allowed_users:
                try:
                    await bot.send_message(str(u), str(d))
                except:
                    pass
            os.remove('./main/tgmsgs/' + report)
            