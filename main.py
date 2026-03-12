from telethon import TelegramClient, events
import sqlite3
import time

API_ID = 33002243
API_HASH = "9b6ed9a656fb7c58dd091c097fa9dc5e"

SEND_CHAT = -1003848748642

client = TelegramClient("session", API_ID, API_HASH)

conn = sqlite3.connect("data.db")
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS chats (chat TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS users (id TEXT, time INTEGER)")
conn.commit()


def add_chat(chat):
    cur.execute("INSERT INTO chats VALUES (?)", (chat,))
    conn.commit()


def del_chat(chat):
    cur.execute("DELETE FROM chats WHERE chat=?", (chat,))
    conn.commit()


def get_chats():
    cur.execute("SELECT chat FROM chats")
    return [x[0] for x in cur.fetchall()]


def check_user(uid):

    cur.execute("SELECT time FROM users WHERE id=?", (uid,))
    row = cur.fetchone()

    now = int(time.time())

    if not row:
        cur.execute("INSERT INTO users VALUES (?,?)", (uid, now))
        conn.commit()
        return True

    if now - row[0] > 259200:
        cur.execute("UPDATE users SET time=? WHERE id=?", (now, uid))
        conn.commit()
        return True

    return False


@client.on(events.NewMessage(pattern="/add"))
async def add(event):

    try:
        chat = event.raw_text.split(" ", 1)[1]
    except:
        await event.reply("используй: /add @chat")
        return

    add_chat(chat)

    await event.reply("чат добавлен")


@client.on(events.NewMessage(pattern="/del"))
async def delete(event):

    try:
        chat = event.raw_text.split(" ", 1)[1]
    except:
        await event.reply("используй: /del @chat")
        return

    del_chat(chat)

    await event.reply("чат удален")


@client.on(events.NewMessage(pattern="/list"))
async def list_chats(event):

    chats = get_chats()

    if not chats:
        await event.reply("чаты не добавлены")
        return

    text = "Мониторинг:\n"

    for c in chats:
        text += f"{c}\n"

    await event.reply(text)


@client.on(events.NewMessage)
async def parser(event):

    chats = get_chats()

    chat_id = str(event.chat_id)
    chat_username = event.chat.username

    if chat_id not in chats and chat_username not in chats:
        return

    user = await event.get_sender()

    if not user:
        return

    if not check_user(str(user.id)):
        return

    username = user.username if user.username else "нет"
    link = f"https://t.me/{username}" if username != "нет" else "нет"

    text = f"""👤 Пользователь найден:
├ ID: {user.id}
├ Username: @{username}
└ Ссылка: {link}"""

    await client.send_message(SEND_CHAT, text)


client.start()
print("Бот запущен")
client.run_until_disconnected()
