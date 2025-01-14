import pickle
import sys

from loguru import logger
from vkbottle import API, PhotoToAlbumUploader
from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules.base import CommandRule

from albums import create_album, upload_pack
from bundle import Bundle
from data import TOKEN, USER_TOKEN, ADMINS

bot = Bot(TOKEN)

api = API(USER_TOKEN)
uploader = PhotoToAlbumUploader(api)

logger.remove()
logger.add(sys.stderr, level="ERROR")

add_rule = CommandRule("добавить", ["!", "/"], 7, "\n")


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
        "Команда выглядит так: каждый аргумент на новой строке, в таком порядке: название пака (1 слово!!!!), "
        "добавлять ли открытия в коллекцию (0 или 1, 0 - нет, 1 - да)"
        "ссылка на альбом, номер первой коммонки, первой рарки, первого эпика, первой леги.\n\n"
        "Пример:\n"
        "/добавить\n"
        "волк\n"
        "1\n"
        "https://vk.com/album-202775388_305247094\n"
        "3\n"
        "19\n"
        "31\n"
        "39"
    )


@bot.on.message(add_rule)
async def add_handler(message: Message):
    with open("bundles.pickle", "rb") as f:
        bundles = pickle.load(f)
    if message.peer_id > 2000000000 or message.peer_id not in ADMINS:
        return
    data = (await add_rule.check(message))['args']
    name = data[0]
    album = data[2][20:].split('_')
    numbers = [int(i) - 1 for i in data[3:]]
    photo_objects = (await api.photos.get(owner_id=album[0], album_id=album[1], count=1000)).items
    photos = [
        (f'photo{i.owner_id}_{i.id}', i.orig_photo.url) for i in photo_objects
    ]

    bundle = Bundle(
        photos[numbers[0]:numbers[1]],
        photos[numbers[1]:numbers[2]],
        photos[numbers[2]:numbers[3]],
        photos[numbers[3]:],
        bool(int(data[1]))
    )
    bundles[name] = bundle
    with open("bundles.pickle", "wb") as f:
        pickle.dump(bundles, f)
    await message.answer(f"Пак с названием '{name}' добавлен и может быть открыт")


@bot.on.message(CommandRule("удалить", ["!", "/"], 1))
async def delete_handler(message: Message):
    with open("bundles.pickle", "rb") as f:
        bundles = pickle.load(f)
    if message.peer_id > 2000000000 or message.peer_id not in ADMINS:
        return
    name = message.text.split(' ')[1]
    del bundles[name]

    with open("bundles.pickle", "wb") as f:
        pickle.dump(bundles, f)

    await message.answer(f"Пак с названием '{name}' удален")


@bot.on.message(CommandRule("альбом", ["!", "/"], 1))
async def album_handler(message: Message):
    with open("albums.pickle", "rb") as f:
        albums = pickle.load(f)
    albums[message.from_id] = message.text.split(' ')[1]
    with open("albums.pickle", "wb") as f:
        pickle.dump(albums, f)


@bot.on.message(CommandRule("открыть", ["!", "/"], 1))
async def open_handler(message: Message):
    with open("bundles.pickle", "rb") as f:
        bundles = pickle.load(f)
    name = message.text.split(' ')[1]
    if not bundles.get(name):
        return "Такой пак не найден"

    cards = bundles[name].open()
    await message.answer("Открытие пака:", attachment=[card[0] for card in cards])

    if bundles[name].save:
        with open("albums.pickle", "rb") as f:
            albums = pickle.load(f)
        if albums.get(message.from_id) is None:
            user = (await bot.api.users.get(user_ids=[message.from_id]))[0]
            albums[message.from_id] = await create_album(api, f"{user.first_name} {user.last_name}")
        await upload_pack(api, albums[message.from_id], [card[1] for card in cards])
        with open("albums.pickle", "wb") as f:
            pickle.dump(albums, f)



bot.run_forever()
