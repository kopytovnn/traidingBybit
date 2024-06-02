def useroutput(record):
    return f'''
№: {record.id}\t{record.name}'''

def userbigouput(record, ti):
    return f'''
Параметры пользователя {record.name}#{record.id}
Актуальный баланс: {round(ti.balance, 2)}USDT

Торговый депозит {record.symbol}USDT: {record.deposit} USDT

Api ключи: {ti.apiStatus}

Мониторинг:
{ti.monitoring()}'''