from pyrogram import filters

from FallenRobot import pbot
from FallenRobot.utils.errors import capture_err
from FallenRobot.utils.functions import make_carbon


@pbot.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message):
    if not message.reply_to_message:
        return await message.reply_text("ʀᴇsᴘᴏɴᴅᴇ ᴀ ᴜɴ ᴛᴇxᴛᴏ ᴘᴀʀᴀ ɢᴇɴᴇʀᴀʀ ᴄᴀʀʙᴏɴ.")
    if not message.reply_to_message.text:
        return await message.reply_text("ʀᴇsᴘᴏɴᴅᴇ ᴀ ᴜɴ ᴛᴇxᴛᴏ ᴘᴀʀᴀ ɢᴇɴᴇʀᴀʀ ᴄᴀʀʙᴏɴ.")
    m = await message.reply_text("ɢᴇɴᴇʀᴀɴᴅᴏ ᴄᴀʀʙᴏɴ...")
    carbon = await make_carbon(message.reply_to_message.text)
    await m.edit_text("ᴄᴀʀɢᴀɴᴅᴏ ᴄᴀʀʙᴏɴ ɢᴇɴᴇʀᴀᴅᴏ...")
    await pbot.send_photo(message.chat.id, carbon)
    await m.delete()
    carbon.close()


__mod_name__ = "Cᴀʀʙᴏɴ"

__help__ = """
Hace carbon del texto dado y te lo envia.

❍ /carbon *:* Hace carbon si respondes a un texto.
 """
