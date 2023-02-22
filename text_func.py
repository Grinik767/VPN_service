def split_message(message):
    if len(message) > 4095:
        c = message.count('\n')
        message_s = message.split('\n')
        res = []
        ln, i = 0, 0
        mes = []
        while i < len(message_s):
            if (ln + len(message_s[i])) <= (4095 - c):
                ln += len(message_s[i])
                mes.append(message_s[i])
                i += 1
            else:
                res.append('\n'.join(mes).strip())
                mes = []
                ln = 0

        if len(mes) > 0:
            res.append('\n'.join(mes).strip())
    else:
        res = [message]
    return res


def send_split_message(bot, chat_id, splitted_message: list):
    for i in range(len(splitted_message)):
        bot.send_message(chat_id, splitted_message[i])
