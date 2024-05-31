def useroutput(record):
    return f'''
№: {record.id}\t{record.name}'''

def userbigouput(record):
    return f'''
Параметры пользователя {record.name}#{record.id}
Актуальный баланс: NOT AVALIABLE RIGHT NOW

Торговый депозит {record.symbol}USDT: {record.deposit} USDT

Api ключи: NOT AVALIABLE RIGHT NOW

Мониторинг: NOT AVALIABLE RIGHT NOW'''