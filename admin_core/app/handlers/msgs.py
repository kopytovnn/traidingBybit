def UserInfoMsg(id, tgelegram_id, end_date):
    return f'''
            Пользователь: {id}
telegram: {tgelegram_id}
Дата окончания действия подписки: {end_date}'''