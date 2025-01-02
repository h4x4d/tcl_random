import pickle
import sys

from loguru import logger
from vkbottle import API
from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules.base import CommandRule

from bundle import Bundle
from data import TOKEN, USER_TOKEN, ADMINS

bot = Bot(TOKEN)
api = API(USER_TOKEN)

bundles = {}

logger.remove()
logger.add(sys.stderr, level="ERROR")

add_rule = CommandRule("добавить", ["!", "/"], 6, "\n")


@bot.on.message(CommandRule("док", ["!", "/"]))
async def doc_handler(message: Message):
    await message.answer(
        "Поддерживаются следующие команды:\n\n"
        "Для игроков:\n"
        "!открыть *название пака* - открывает пак\n\n"
        "Для администраторов:\n"
        "!добавить - добавляет новый пак (отдельная документация по команде !добавить без аргументов)\n"
        "!удалить *название пака* - удаляет пак"
    )


@bot.on.message(CommandRule("добавить", ["!", "/"]))
async def add_doc_handler(message: Message):
    await message.answer(
        "Команда выглядит так: каждый аргумент на новой строке, в таком порядке: название пака (1 слово!!!!),"
        "ссылка на альбом, номер первой коммонки, первой рарки, первого эпика, первой леги.\n\n"
        "Пример:\n"
        "/добавить\n"
        "волк\n"
        "https://vk.com/album-202775388_305247094\n"
        "3\n"
        "19\n"
        "31\n"
        "39"
    )


@bot.on.message(add_rule)
async def add_handler(message: Message):
    global bundles
    with open("bundles.pickle", "rb") as f:
        bundles = pickle.load(f)
    if message.peer_id > 2000000000 or message.peer_id not in ADMINS:
        return
    data = (await add_rule.check(message))['args']
    name = data[0]
    album = data[1][20:].split('_')
    numbers = [int(i) - 1 for i in data[2:]]
    photo_objects = (await api.photos.get(owner_id=album[0], album_id=album[1], count=1000)).items
    photos = [
        f'photo{i.owner_id}_{i.id}' for i in photo_objects
    ]

    bundle = Bundle(
        photos[numbers[0]:numbers[1]],
        photos[numbers[1]:numbers[2]],
        photos[numbers[2]:numbers[3]],
        photos[numbers[3]:],
    )
    bundles[name] = bundle
    with open("bundles.pickle", "wb") as f:
        pickle.dump(bundles, f)
    await message.answer(f"Пак с названием '{name}' добавлен и может быть открыт")


@bot.on.message(CommandRule("удалить", ["!", "/"], 1))
async def delete_handler(message: Message):
    global bundles
    with open("bundles.pickle", "rb") as f:
        bundles = pickle.load(f)
    if message.peer_id > 2000000000 or message.peer_id not in ADMINS:
        return
    name = message.text.split(' ')[1]
    del bundles[name]

    with open("bundles.pickle", "wb") as f:
        pickle.dump(bundles, f)

    await message.answer(f"Пак с названием '{name}' удален")


@bot.on.message(CommandRule("открыть", ["!", "/"], 1))
async def open_handler(message: Message):
    global bundles
    with open("bundles.pickle", "rb") as f:
        bundles = pickle.load(f)
    name = message.text.split(' ')[1]
    if not bundles.get(name):
        return "Такой пак не найден"

    cards = bundles[name].open()

    await message.answer("Открытие пака:", attachment=cards)


bot.run_forever()
