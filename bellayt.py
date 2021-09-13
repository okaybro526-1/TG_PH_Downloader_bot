import os
import asyncio
from urllib.parse import urlparse
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from youtube_dl import YoutubeDL
from opencc import OpenCC
from config import Config


Bellayt = Client(
   "PH Videos Downloader",
   api_id=Config.APP_ID,
   api_hash=Config.API_HASH,
   bot_token=Config.TG_BOT_TOKEN,
)

YTDL_REGEX = (r"^((?:https?:)?\/\/)"
              r"?((?:www|m)\.)"
              r"?((?:|xvideos\.com|pornhub\.com"
              r"|xhamster\.com|xnxx\.com))"
              r"(\/)([-a-zA-Z0-9()@:%_\+.~#?&//=]*)([\w\-]+)(\S+)?$")
s2tw = OpenCC('s2tw.json').convert


# https://docs.pyrogram.org/start/examples/bot_keyboards
# Reply with inline keyboard

@Bellayt.on_message(filters.command("start"))
async def gstart(_, message: Message):
      await message.reply_text("""**PornHub Downloader Working as Fuck 💦 Send Link of Pornhub, Xvideos, Xhamster, XnXX ✅**""",
      reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "💦 All In One Porn Bot 💦", url="https://t.me/educationalvideos_bot")
                ]
            ]
        )
   )



@Bellayt.on_message(filters.text("^ytdl_video$"))
async def ytdl_video(_, ytdl_video):
    try:
        # url = callback_query.message.text
        url = callback_query.message.reply_to_message.text
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': '%(title)s - %(extractor)s-%(id)s.%(ext)s',
            'writethumbnail': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            message = callback_query.message
            await message.reply_chat_action("typing")
            info_dict = ydl.extract_info(url, download=False)
            # download
            await callback_query.edit_message_text("**Downloading video. Please wait...**")
            ydl.process_info(info_dict)
            # upload
            video_file = ydl.prepare_filename(info_dict)
            task = asyncio.create_task(send_video(message, info_dict,
                                                  video_file))
            while not task.done():
                await asyncio.sleep(3)
                await message.reply_chat_action("upload_document")
            await message.reply_chat_action("cancel")
            await message.delete()
    except Exception as e:
        await message.reply_text(e)
    await callback_query.message.reply_to_message.delete()
    await callback_query.message.delete()


async def send_video(message: Message, info_dict, video_file):
    basename = video_file.rsplit(".", 1)[-2]
    # thumbnail
    thumbnail_url = info_dict['thumbnail']
    thumbnail_file = basename + "." + \
        get_file_extension_from_url(thumbnail_url)
    # info (s2tw)
    webpage_url = info_dict['webpage_url']
    title = '@educationalvideos_bot '+s2tw(info_dict['title'])
    caption = f"<b><a href=\"{webpage_url}\">{title}</a></b>"
    duration = int(float(info_dict['duration']))
    width, height = get_resolution(info_dict)
    await message.reply_video(
        video_file, caption=caption, duration=duration,
        width=width, height=height, parse_mode='HTML',
        thumb=thumbnail_file,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Save ✅",
                        callback_data="forward_video"
                    ),
                    InlineKeyboardButton(
                        "Contact 👤",
                        url="https://t.me/xtronsbot"
                    )
                ]
            ]
        ))
    os.remove(video_file)
    os.remove(thumbnail_file)


def get_file_extension_from_url(url):
    url_path = urlparse(url).path
    basename = os.path.basename(url_path)
    return basename.split(".")[-1]


def get_resolution(info_dict):
    if {"width", "height"} <= info_dict.keys():
        width = int(info_dict['width'])
        height = int(info_dict['height'])
    # https://support.google.com/youtube/answer/6375112
    elif info_dict['height'] == 1080:
        width = 1920
        height = 1080
    elif info_dict['height'] == 720:
        width = 1280
        height = 720
    elif info_dict['height'] == 480:
        width = 854
        height = 480
    elif info_dict['height'] == 360:
        width = 640
        height = 360
    elif info_dict['height'] == 240:
        width = 426
        height = 240
    return (width, height)


@Bellayt.on_callback_query(filters.regex("^forward_video$"))
async def callback_query_forward_video(_, callback_query):
    m_edited = await callback_query.message.edit_reply_markup(None)
    m_cp = await m_edited.copy(CHANNEL_FORWARD_TO,
                               disable_notification=True)
    await callback_query.answer("Saved!")
    await m_edited.reply(m_cp.link, quote=True)

print(
    """
Bot Started!
Visit @educationalvideos_bot
"""
)

Bellayt.run()
