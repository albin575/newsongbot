import os
import time

import requests
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from youtube_search import YoutubeSearch

from config import Config

ABS = "Developer"
OWNER = "Owner"
GITCLONE = "https://github.com/albin575/song-bot"
B2 = "https://telegram.dog/AB_Mediaw"
BUTTON1 = "ðŸ“œ Source Code ðŸ“œ"


def time_to_seconds(time_str):
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(str(time_str).split(':'))))


@Client.on_message(filters.command('start') & filters.private)
async def start(client, message):
    await message.reply_photo(
        photo=Config.START_IMG,
        caption=Config.START_MSG.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(BUTTON1, url=GITCLONE)
                ], [
                    InlineKeyboardButton(OWNER, url=f"https://telegram.dog/{Config.OWNER}"),
                    InlineKeyboardButton(ABS, url=B2)
                ]
            ]
        ),
        reply_to_message_id=message.id
    )


@Client.on_message(filters.command(['song']))
async def song(client, message):
    query = ' '.join(str(i) for i in message.command[1:])
    if not query.strip():
        await message.reply("**Enter Song Name with /song Command!**")
        return

    status = await message.reply('`Searching... Please Wait...`')

    results = []
    for attempt in range(6):
        if attempt > 0:
            time.sleep(1)
        results = YoutubeSearch(query, max_results=1).to_dict()
        if results:
            break

    if not results:
        await status.edit('**ðŸ‘Ž Nothing found Retry with another !**')
        return

    link = f"https://youtube.com{results[0]['url_suffix']}"
    title = results[0]["title"]
    thumbnail = results[0]["thumbnails"][0]
    duration = results[0]["duration"]

    # UNCOMMENT TO LIMIT DURATION (seconds). 1800 = 30 minutes.
    # if time_to_seconds(duration) >= 1800:
    #     await status.edit("Exceeded 30mins cap")
    #     return

    performer = "[@AB_Mediaw]"
    os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
    thumb_name = os.path.join(Config.DOWNLOAD_LOCATION, f'thumb{message.chat.id}_{message.id}.jpg')
    try:
        thumb = requests.get(thumbnail, allow_redirects=True, timeout=15)
        with open(thumb_name, 'wb') as f:
            f.write(thumb.content)
    except Exception as e:
        print(e)
        thumb_name = None

    await status.edit("`Bruh... Uploading... Please Wait...`")
    audio_file = None
    try:
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": os.path.join(Config.DOWNLOAD_LOCATION, f"{message.chat.id}_{message.id}.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)

        rep = f'ðŸŽ¶ <b>Title:</b> <a href="{link}">{title}</a>\nâŒš <b>Duration:</b> <code>{duration}</code>\nðŸ“» <b>Uploaded By:</b> <a href="https://t.me/AB_Mediaw">AB_Mediaw</a>'
        dur = 0
        try:
            secmul = 1
            for part in reversed(duration.split(':')):
                dur += int(part) * secmul
                secmul *= 60
        except ValueError:
            dur = 0

        await message.reply_audio(
            audio_file,
            caption=rep,
            parse_mode='HTML',
            quote=False,
            title=title,
            duration=dur,
            performer=performer,
            thumb=thumb_name
        )
        await status.delete()
    except Exception as e:
        await status.edit('**An internal Error Occured, Report This @redbullfed!!**')
        print(e)

    for path in (audio_file, thumb_name):
        if not path:
            continue
        try:
            os.remove(path)
        except Exception as e:
            print(e)
