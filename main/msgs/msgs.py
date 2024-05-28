def useroutput(record):
    return f'''
Id: {record.id}

Имя: {record.name}

ByBit Api key: {record.bybitapi}

ByBit Secret key: {record.bybitsecret}'''