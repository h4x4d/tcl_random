from io import BytesIO

import vkbottle.api.api
from vkbottle import PhotoToAlbumUploader
import requests


async def create_album(api: vkbottle.api.api.API, text):
    album = await api.photos.create_album(
        title=text,
        group_id=229013563
    )
    return album.id


async def upload_pack(api: vkbottle.api.api.API, album_id, cards_list):
    url = (await api.photos.get_upload_server(group_id=229013563, album_id=album_id)).upload_url
    files = {
        f"file{i + 1}": (f"{i}.jpg", BytesIO(requests.get(cards_list[i]).content), "image/jpeg")
        for i in range(len(cards_list))
    }
    r = requests.post(url, files=files).json()

    return await api.photos.save(
        album_id=album_id,
        group_id=229013563,
        photos_list=r['photos_list'],
        hash=r['hash'],
        server=r['server'],
    )
