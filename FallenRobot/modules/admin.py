import html
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, run_async
from telegram.utils.helpers import mention_html

from FallenRobot import DRAGONS, dispatcher
from FallenRobot.modules.disable import DisableAbleCommandHandler
from FallenRobot.modules.helper_funcs.admin_rights import user_can_changeinfo
from FallenRobot.modules.helper_funcs.alternate import send_message
from FallenRobot.modules.helper_funcs.chat_status import (
    ADMIN_CACHE,
    bot_admin,
    can_pin,
    can_promote,
    connection_status,
    user_admin,
)
from FallenRobot.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from FallenRobot.modules.log_channel import loggable


@run_async
@bot_admin
@user_admin
def set_sticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text(
            "» ɴᴏ ᴛɪᴇɴᴇs ᴘᴇʀᴍɪsᴏ ᴘᴀʀᴀ ᴄᴀᴍʙɪᴀʀ ʟᴀ ɪɴғᴏʀᴍᴀᴄɪᴏɴ ᴅᴇʟ ɢʀᴜᴘᴏ ʙᴇʙᴇ !"
        )

    if msg.reply_to_message:
        if not msg.reply_to_message.sticker:
            return msg.reply_text(
                "» ʀᴇsᴘᴏɴᴅᴇ ᴀ ᴜɴ sᴛɪᴄᴋᴇʀ ᴘᴀʀᴀ ᴇsᴛᴀʙʟᴇᴄᴇʀʟᴏ ᴄᴏᴍᴏ ᴘᴀǫᴜᴇᴛᴇ ᴅᴇ sᴛɪᴄᴋᴇʀs ɢʀᴜᴘᴀʟᴇs !"
            )
        stkr = msg.reply_to_message.sticker.set_name
        try:
            context.bot.set_chat_sticker_set(chat.id, stkr)
            msg.reply_text(f"» ᴇsᴛᴀʙʟᴇᴄɪᴅᴏ ᴄᴏɴ ᴇxɪᴛᴏ sᴛɪᴄɪᴋᴇʀs ᴅᴇ ɢʀᴜᴘᴏ ᴇɴ {chat.title}!")
        except BadRequest as excp:
            if excp.message == "Participants_too_few":
                return msg.reply_text(
                    "» sᴜ ɢʀᴜᴘᴏ ɴᴇᴄᴇsɪᴛᴀ ᴜɴ ᴍɪɴɪᴍᴏ ᴅᴇ 𝟷𝟶𝟶 ᴍɪᴇᴍʙʀᴏs ᴘᴀʀᴀ ᴄᴏɴғɪɢᴜʀᴀʀ ᴜɴ ᴘᴀǫᴜᴇᴛᴇ ᴅᴇ sᴛɪᴄᴋᴇʀs ᴄᴏᴍᴏ ᴘᴀǫᴜᴇᴛᴇ ᴅᴇ sᴛɪᴄᴋᴇʀs ɢʀᴜᴘᴀʟᴇs !"
                )
            msg.reply_text(f"ᴇʀʀᴏʀ ! {excp.message}.")
    else:
        msg.reply_text("» ʀᴇsᴘᴏɴᴅᴇ ᴀ ᴜɴ sᴛɪᴄᴋᴇʀ ᴘᴀʀᴀ ᴇsᴛᴀʙʟᴇᴄᴇʀʟᴏ ᴄᴏᴍᴏ ᴘᴀǫᴜᴇᴛᴇ ᴅᴇ sᴛɪᴄᴋᴇʀs ɢʀᴜᴘᴀʟᴇs !")


@run_async
@bot_admin
@user_admin
def setchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("» ɴᴏ ᴛɪᴇɴᴇs ᴘᴇʀᴍɪsᴏ ᴘᴀʀᴀ ᴄᴀᴍʙɪᴀʀ ʟᴀ ɪɴғᴏʀᴍᴀᴄɪᴏɴ ᴅᴇʟ ɢʀᴜᴘᴏ ʙᴇʙᴇ !")
        return

    if msg.reply_to_message:
        if msg.reply_to_message.photo:
            pic_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            pic_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("» sᴏʟᴏ ᴘᴜᴇᴅᴇs ᴄᴏɴғɪɢᴜʀᴀʀ ғᴏᴛᴏs ᴄᴏᴍᴏ ɢʀᴜᴘᴏ ғᴏᴛᴏs ᴅᴇ ᴘᴇʀғɪʟ !")
            return
        dlmsg = msg.reply_text("» ᴄᴀᴍʙɪᴀɴᴅᴏ ʟᴀ ғᴏᴛᴏ ᴅᴇ ᴘᴇʀғɪʟ ᴅᴇʟ ɢʀᴜᴘᴏ...")
        tpic = context.bot.get_file(pic_id)
        tpic.download("gpic.png")
        try:
            with open("gpic.png", "rb") as chatp:
                context.bot.set_chat_photo(int(chat.id), photo=chatp)
                msg.reply_text("» ᴇsᴛᴀʙʟᴇᴄɪᴅᴏ ᴄᴏɴ ᴇxɪᴛᴏ ʟᴀ ғᴏᴛᴏ ᴅᴇ ᴘᴇʀғɪʟ ᴅᴇʟ ɢʀᴜᴘᴏ !")
        except BadRequest as excp:
            msg.reply_text(f"ᴇʀʀᴏʀ ! {excp.message}")
        finally:
            dlmsg.delete()
            if os.path.isfile("gpic.png"):
                os.remove("gpic.png")
    else:
        msg.reply_text("» ʀᴇsᴘᴏɴᴅᴇ ᴀ ᴜɴᴀ ғᴏᴛᴏ ᴏ ᴀʀᴄʜɪᴠᴏ ᴘᴀʀᴀ ᴠᴇʀʟᴀ ᴄᴏᴍᴏ ғᴏᴛᴏ ᴅᴇ ᴘᴇʀғɪʟ ᴅᴇ ɢʀᴜᴘᴏ !")


@run_async
@bot_admin
@user_admin
def rmchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("» ɴᴏ ᴛɪᴇɴᴇs ᴘᴇʀᴍɪsᴏs ᴘᴀʀᴀ ᴄᴀᴍʙɪᴀʀ ʟᴀ ɪɴғᴏʀᴍᴀᴄɪᴏɴ ᴅᴇʟ ɢʀᴜᴘᴏ ʙᴇʙᴇ !")
        return
    try:
        context.bot.delete_chat_photo(int(chat.id))
        msg.reply_text("» ғᴏᴛᴏ ᴅᴇ ᴘᴇʀғɪʟ ᴘʀᴇᴅᴇᴛᴇʀᴍɪɴᴀᴅᴀ ᴅᴇʟ ɢʀᴜᴘᴏ ᴇʟɪᴍɪɴᴀᴅᴀ ᴄᴏɴ ᴇxɪᴛᴏ !")
    except BadRequest as excp:
        msg.reply_text(f"ᴇʀʀᴏʀ ! {excp.message}.")
        return


@run_async
@bot_admin
@user_admin
def set_desc(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text(
            "» ɴᴏ ᴛɪᴇɴᴇs ᴘᴇʀᴍɪsᴏ ᴘᴀʀᴀ ᴄᴀᴍʙɪᴀʀ ʟᴀ ɪɴғᴏʀᴍᴀᴄɪᴏɴ ᴅᴇʟ ɢʀᴜᴘᴏ ʙᴇʙᴇ !"
        )

    tesc = msg.text.split(None, 1)
    if len(tesc) >= 2:
        desc = tesc[1]
    else:
        return msg.reply_text("» ¿ǫᴜᴇ ᴄᴀʀᴀJᴏs? ǫᴜɪᴇʀᴇs ᴇsᴛᴀʙʟᴇᴄᴇʀ ᴜɴᴀ ᴅᴇsᴄʀɪᴘᴄɪᴏɴ ᴠᴀᴄɪᴀ !")
    try:
        if len(desc) > 255:
            return msg.reply_text(
                "» ʟᴀ ᴅᴇsᴄʀɪᴘᴄɪᴏɴ ᴅᴇʙᴇ ᴛᴇɴᴇʀ ᴍᴇɴᴏs ᴅᴇ 𝟸𝟻𝟻 ᴘᴀʟᴀʙʀᴀs ᴅᴇ ᴄᴀʀᴀᴄᴛᴇʀᴇs !"
            )
        context.bot.set_chat_description(chat.id, desc)
        msg.reply_text(f"» ᴅᴇsᴄʀɪᴘᴄɪᴏɴ ᴅᴇʟ ᴄʜᴀᴛ ᴀᴄᴛᴜᴀʟɪᴢᴀᴅᴀ ᴄᴏɴ ᴇxɪᴛᴏ ᴇɴ {chat.title}!")
    except BadRequest as excp:
        msg.reply_text(f"ᴇʀʀᴏʀ ! {excp.message}.")


@run_async
@bot_admin
@user_admin
def setchat_title(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    args = context.args

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("» ɴᴏ ᴛɪᴇɴᴇs ᴘᴇʀᴍɪsᴏs ᴘᴀʀᴀ ᴄᴀᴍʙɪᴀʀ ʟᴀ ɪɴғᴏʀᴍᴀᴄɪᴏɴ ᴅᴇʟ ɢʀᴜᴘᴏ ʙᴇʙᴇ !")
        return

    title = " ".join(args)
    if not title:
        msg.reply_text("» ɪɴɢʀᴇsᴇ ᴜɴ ᴛᴇxᴛᴏ ᴘᴀʀᴀ ᴇsᴛᴀʙʟᴇᴄᴇʀʟᴏ ᴄᴏᴍᴏ ɴᴜᴇᴠᴏ ᴛɪᴛᴜʟᴏ ᴅᴇ ᴄʜᴀᴛ !")
        return

    try:
        context.bot.set_chat_title(int(chat.id), str(title))
        msg.reply_text(
            f"» ᴇsᴛᴀʙʟᴇᴄɪᴅᴏ ᴄᴏʀʀᴇᴄᴛᴀᴍᴇɴᴛᴇ <b>{title}</b> ᴄᴏᴍᴏ ᴜɴ ɴᴜᴇᴠᴏ ᴛɪᴛᴜʟᴏ ᴅᴇ ᴄʜᴀᴛ !",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        msg.reply_text(f"ᴇʀʀᴏʀ ! {excp.message}.")
        return


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def promote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text("» ɴᴏ ᴛɪᴇɴᴇs ᴘᴇʀᴍɪsᴏs ᴘᴀʀᴀ ᴀɢʀᴇɢᴀʀ ɴᴜᴇᴠᴏs ᴀᴅᴍɪɴɪsᴛʀᴀᴅᴏʀᴇs ʙᴇʙᴇ !")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "» ɴᴏ sᴇ ǫᴜɪᴇɴ ᴇs ᴇsᴇ ᴜsᴜᴀʀɪᴏ, ɴᴜɴᴄᴀ ʟᴏ ᴠᴇᴏ ᴇɴ ɴɪɴɢᴜɴᴏ ᴅᴇ ʟᴏs ᴄʜᴀᴛs ᴅᴏɴᴅᴇ ᴇsᴛᴏʏ ᴘʀᴇsᴇɴᴛᴇ !",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ("administrator", "creator"):
        message.reply_text("» sᴇɢᴜɴ ʏᴏ ᴇsᴇ ᴜsᴜᴀʀɪᴏ ʏᴀ ᴇs ᴀᴅᴍɪɴɪsᴛʀᴀᴅᴏʀ ᴀǫᴜɪ !")
        return

    if user_id == bot.id:
        message.reply_text(
            "» ɴᴏ ᴘᴜᴇᴅᴏ ᴘʀᴏᴍᴏᴠᴇʀᴍᴇ, ᴍɪ ᴅᴜᴇñᴏ ɴᴏ ᴍᴇ ᴅɪJᴏ ǫᴜᴇ ʟᴏ ʜɪᴄɪᴇʀᴀ."
        )
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            # can_manage_voice_chats=bot_member.can_manage_voice_chats,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("» ᴄᴏᴍᴏ ᴘᴜᴇᴅᴏ ᴠᴇʀ ǫᴜᴇ ᴇʟ ᴜsᴜᴀʀɪᴏ ɴᴏ ᴇsᴛᴀ ᴘʀᴇsᴇɴᴛᴇ ᴀǫᴜɪ.")
        else:
            message.reply_text(
                "» ᴀʟɢᴏ sᴀʟɪᴏ ᴍᴀʟ, ᴛᴀʟ ᴠᴇᴢ ᴀʟɢᴜɪᴇɴ ᴘʀᴏᴍᴏᴠɪᴏ ᴀ ᴇsᴇ ᴜsᴜᴀʀɪᴏ ᴀɴᴛᴇs ǫᴜᴇ ʏᴏ."
            )
        return

    bot.sendMessage(
        chat.id,
        f"<b>» ᴘʀᴏᴍᴏᴠɪᴇɴᴅᴏ ᴀ ᴜɴ ᴜsᴜᴀʀɪᴏ ᴇɴ</b> {chat.title}\n\nᴘʀᴏᴍᴏᴠɪᴅᴏ : {mention_html(user_member.user.id, user_member.user.first_name)}\nᴩʀᴏᴍᴏᴛᴇʀ : {mention_html(user.id, user.first_name)}",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ᴘʀᴏᴍᴏᴠɪᴅᴏ\n"
        f"<b>ᴘʀᴏᴍᴏᴛᴏʀ :</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜsᴜᴀʀɪᴏ :</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def lowpromote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creador")
        and user.id not in DRAGONS
    ):
        message.reply_text("» ɴᴏ ᴛɪᴇɴᴇs ᴘᴇʀᴍɪsᴏs ᴘᴀʀᴀ ᴀɢʀᴇɢᴀʀ ɴᴜᴇᴠᴏs ᴀᴅᴍɪɴɪsᴛʀᴀᴅᴏʀᴇs ʙᴇʙᴇ !")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "» ɴᴏ sᴇ ǫᴜɪᴇɴ ᴇs ᴇsᴇ ᴜsᴜᴀʀɪᴏ, ɴᴜɴᴄᴀ ʟᴏ ᴠᴇᴏ ᴇɴ ɴɪɴɢᴜɴᴏ ᴅᴇ ʟᴏs ᴄʜᴀᴛs ᴅᴏɴᴅᴇ ᴇsᴛᴏʏ ᴘʀᴇsᴇɴᴛᴇ !",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ("administrador", "creador"):
        message.reply_text("» sᴇɢᴜɴ ʏᴏ ᴇsᴇ ᴜsᴜᴀʀɪᴏ ʏᴀ ᴇs ᴀᴅᴍɪɴɪsᴛʀᴀᴅᴏʀ ᴀǫᴜɪ !")
        return

    if user_id == bot.id:
        message.reply_text(
            "» ɴᴏ ᴘᴜᴇᴅᴏ ᴘʀᴏᴍᴏᴠᴇʀᴍᴇ, ᴍɪ ᴅᴜᴇñᴏ ɴᴏ ᴍᴇ ᴅɪJᴏ ǫᴜᴇ ʟᴏ ʜɪᴄɪᴇʀᴀ."
        )
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("» ᴄᴏᴍᴏ ᴘᴜᴇᴅᴏ ᴠᴇʀ ǫᴜᴇ ᴇʟ ᴜsᴜᴀʀɪᴏ ɴᴏ ᴇsᴛᴀ ᴘʀᴇsᴇɴᴛᴇ ᴀǫᴜɪ.")
        else:
            message.reply_text(
                "» ᴀʟɢᴏ sᴀʟɪᴏ ᴍᴀʟ, ᴛᴀʟ ᴠᴇᴢ ᴀʟɢᴜɪᴇɴ ᴘʀᴏᴍᴏᴠɪᴏ ᴀ ᴇsᴇ ᴜsᴜᴀʀɪᴏ ᴀɴᴛᴇs ǫᴜᴇ ʏᴏ."
            )
        return

    bot.sendMessage(
        chat.id,
        f"<b>» ʙᴀJᴀ ᴘʀᴏᴍᴏᴄɪᴏɴ ᴅᴇ ᴜɴ ᴜsᴜᴀʀɪᴏ ᴇɴ </b>{chat.title}\n\n<b>ᴘʀᴏᴍᴏᴠɪᴅᴏ :</b> {mention_html(user_member.user.id, user_member.user.first_name)}\nᴘʀᴏᴍᴏᴛᴏʀ : {mention_html(user.id, user.first_name)}",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ʟᴏᴡᴩʀᴏᴍᴏᴛᴇᴅ\n"
        f"<b>ᴘʀᴏᴍᴏᴛᴏʀ :</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜsᴜᴀʀɪᴏ :</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def fullpromote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text("» ɴᴏ ᴛɪᴇɴᴇs ᴘᴇʀᴍɪsᴏs ᴘᴀʀᴀ ᴀɢʀᴇɢᴀʀ ɴᴜᴇᴠᴏs ᴀᴅᴍɪɴɪsᴛʀᴀᴅᴏʀᴇs ʙᴇʙᴇ !")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "» ɴᴏ sᴇ ǫᴜɪᴇɴ ᴇs ᴇsᴇ ᴜsᴜᴀʀɪᴏ, ɴᴜɴᴄᴀ ʟᴏ ᴠᴇᴏ ᴇɴ ɴɪɴɢᴜɴᴏ ᴅᴇ ʟᴏs ᴄʜᴀᴛs ᴅᴏɴᴅᴇ ᴇsᴛᴏʏ ᴘʀᴇsᴇɴᴛᴇ !",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ("administrator", "creator"):
        message.reply_text("» sᴇɢᴜɴ ʏᴏ ᴇsᴇ ᴜsᴜᴀʀɪᴏ ʏᴀ ᴇs ᴀᴅᴍɪɴɪsᴛʀᴀᴅᴏʀ ᴀǫᴜɪ !")
        return

    if user_id == bot.id:
        message.reply_text(
            "» ɴᴏ ᴘᴜᴇᴅᴏ ᴘʀᴏᴍᴏᴠᴇʀᴍᴇ, ᴍɪ ᴅᴜᴇñᴏ ɴᴏ ᴍᴇ ᴅɪJᴏ ǫᴜᴇ ʟᴏ ʜɪᴄɪᴇʀᴀ."
        )
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            # can_manage_voice_chats=bot_member.can_manage_voice_chats,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("» ᴄᴏᴍᴏ ᴘᴜᴇᴅᴏ ᴠᴇʀ ǫᴜᴇ ᴇʟ ᴜsᴜᴀʀɪᴏ ɴᴏ ᴇsᴛᴀ ᴘʀᴇsᴇɴᴛᴇ ᴀǫᴜɪ.")
        else:
            message.reply_text(
                "» ᴀʟɢᴏ sᴀʟɪᴏ ᴍᴀʟ, ᴛᴀʟ ᴠᴇᴢ ᴀʟɢᴜɪᴇɴ ᴘʀᴏᴍᴏᴠɪᴏ ᴀ ᴇsᴇ ᴜsᴜᴀʀɪᴏ ᴀɴᴛᴇs ǫᴜᴇ ʏᴏ."
            )
        return

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "↻ ᴅᴇᴍᴏᴛᴇ ↺",
                    callback_data="demote_({})".format(user_member.user.id),
                )
            ]
        ]
    )

    bot.sendMessage(
        chat.id,
        f"» ᴘʀᴏᴍᴏᴄɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴀ ᴅᴇ ᴜɴ ᴜsᴜᴀʀɪᴏ ᴇɴ <b>{chat.title}</b>\n\n<b>ᴜsᴜᴀʀɪᴏ : {mention_html(user_member.user.id, user_member.user.first_name)}</b>\n<b>ᴩʀᴏᴍᴏᴛᴇʀ : {mention_html(user.id, user.first_name)}</b>",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ғᴜʟʟᴩʀᴏᴍᴏᴛᴇᴅ\n"
        f"<b>ᴘʀᴏᴍᴏᴛᴏʀ :</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜsᴜᴀʀɪᴏ :</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def demote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "» ɴᴏ sᴇ ǫᴜɪᴇɴ ᴇs ᴇsᴇ ᴜsᴜᴀʀɪᴏ, ɴᴜɴᴄᴀ ʟᴏ ᴠᴇᴏ ᴇɴ ɴɪɴɢᴜɴᴏ ᴅᴇ ʟᴏs ᴄʜᴀᴛs ᴅᴏɴᴅᴇ ᴇsᴛᴏʏ ᴘʀᴇsᴇɴᴛᴇ !",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "creador":
        message.reply_text(
            "» ᴇsᴇ ᴜsᴜᴀʀɪᴏ ᴇs ᴇʟ ᴅᴜᴇñᴏ ᴅᴇʟ ᴄʜᴀᴛ ʏ ɴᴏ ǫᴜɪᴇʀᴏ ᴘᴏɴᴇʀᴍᴇ ᴇɴ ᴘᴇʟɪɢʀᴏ."
        )
        return

    if not user_member.status == "administrador":
        message.reply_text("» sᴇɢᴜɴ ʏᴏ ᴇsᴇ ᴜsᴜᴀʀɪᴏ ʏᴀ ɴᴏ ᴇs ᴀᴅᴍɪɴɪsᴛʀᴀᴅᴏʀ ᴀǫᴜɪ !")
        return

    if user_id == bot.id:
        message.reply_text("» Nᴏ ᴘᴜᴇᴅᴏ ᴅᴇɢʀᴀᴅᴀʀᴍᴇ, ᴘᴇʀᴏ sɪ ǫᴜɪᴇʀᴇs ᴘᴜᴇᴅᴏ ɪʀᴍᴇ.")
        return

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_voice_chats=False,
        )

        bot.sendMessage(
            chat.id,
            f"» ᴅᴇɢʀᴀᴅᴏ ᴄᴏɴ ᴇxɪᴛᴏ ᴀ ᴜɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴅᴏʀ ᴇɴ <b>{chat.title}</b>\n\nᴅᴇɢʀᴀᴅᴏ : <b>{mention_html(user_member.user.id, user_member.user.first_name)}</b>\nᴅᴇᴍᴏᴛᴇʀ : {mention_html(user.id, user.first_name)}",
            parse_mode=ParseMode.HTML,
        )

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#ᴅᴇᴍᴏᴛᴇᴅ\n"
            f"<b>ᴅᴇɢʀᴀᴅᴀᴅᴏʀ :</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>ᴅᴇɢʀᴀᴅᴏ :</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        message.reply_text(
            "» ɴᴏ ᴘᴜᴅᴏ sᴇʀ ᴅᴇɢʀᴀᴅᴀᴅᴏ, ᴛᴀʟ ᴠᴇᴢ ɴᴏ sᴏʏ ᴀᴅᴍɪɴɪsᴛʀᴀᴅᴏʀ ᴏ ᴛᴀʟ ᴠᴇᴢ ᴀʟɢᴜɪᴇɴ ᴍás ᴘʀᴏᴍᴏᴠɪᴏ ᴀ ᴇsᴇ"
            " ᴜsᴜᴀʀɪᴏ !",
        )
        return


@run_async
@user_admin
def refresh_admin(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text("» ᴄᴀᴄʜᴇ ᴅᴇ ᴀᴅᴍɪɴɪsᴛʀᴀᴄɪᴏɴ ᴀᴄᴛᴜᴀʟɪᴢᴀᴅᴀ ᴄᴏɴ ᴇxɪᴛᴏ !")


@run_async
@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text(
            "»  ɴᴏ sᴇ ǫᴜɪᴇɴ ᴇs ᴇsᴇ ᴜsᴜᴀʀɪᴏ, ɴᴜɴᴄᴀ ʟᴏ ᴠᴇᴏ ᴇɴ ɴɪɴɢᴜɴᴏ ᴅᴇ ʟᴏs ᴄʜᴀᴛs ᴅᴏɴᴅᴇ ᴇsᴛᴏʏ ᴘʀᴇsᴇɴᴛᴇ !",
        )
        return

    if user_member.status == "creador":
        message.reply_text(
            "» ᴇsᴇ ᴜsᴜᴀʀɪᴏ ᴇs ᴇʟ ᴅᴜᴇñᴏ ᴅᴇʟ ᴄʜᴀᴛ ʏ ɴᴏ ǫᴜɪᴇʀᴏ ᴘᴏɴᴇʀᴍᴇ ᴇɴ ᴘᴇʟɪɢʀᴏ.",
        )
        return

    if user_member.status != "administrador":
        message.reply_text(
            "» sᴏʟᴏ ᴘᴜᴇᴅᴏ ᴇsᴛᴀʙʟᴇᴄᴇʀ ᴜɴ ᴛɪᴛᴜʟᴏ ᴘᴀʀᴀ ʟᴏs ᴀᴅᴍɪɴɪsᴛʀᴀᴅᴏʀᴇs !",
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "» Nᴏ ᴘᴜᴇᴅᴏ ᴇsᴛᴀʙʟᴇᴄᴇʀ ᴇʟ ᴛíᴛᴜʟᴏ ᴘᴀʀᴀ ᴍí, ᴍɪ ᴅᴜᴇñᴏ ɴᴏ ᴍᴇ ᴅɪJᴏ ǫᴜᴇ ʟᴏ ʜɪᴄɪᴇʀᴀ.",
        )
        return

    if not title:
        message.reply_text(
            "» ¿ᴄʀᴇᴇs ǫᴜᴇ ᴅᴇJᴀʀ ᴇʟ ᴛɪᴛᴜʟᴏ ᴇɴ ʙʟᴀɴᴄᴏ ᴄᴀᴍʙɪᴀʀᴀ ᴀʟɢᴏ ?"
        )
        return

    if len(title) > 16:
        message.reply_text(
            "» ʟᴀ ʟᴏɴɢɪᴛᴜᴅ ᴅᴇʟ ᴛɪᴛᴜʟᴏ ᴛɪᴇɴᴇ ᴍᴀs ᴅᴇ 𝟷𝟼 ᴘᴀʟᴀʙʀᴀs ᴏ ᴄᴀʀᴀᴄᴛᴇʀᴇs, ᴘᴏʀ ʟᴏ ǫᴜᴇ sᴇ ᴅᴇʙᴇ ᴛʀᴜɴᴄᴀʀ ᴀ 𝟷𝟼 ᴘᴀʟᴀʙʀᴀs.",
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text(
            "» ᴛᴀʟ ᴠᴇᴢ ᴇsᴇ ᴜsᴜᴀʀɪᴏ ɴᴏ ғᴜᴇ ᴘʀᴏᴍᴏᴠɪᴅᴏ ᴘᴏʀ ᴍɪ ᴏ ᴛᴀʟ ᴠᴇᴢ ᴇɴᴠɪᴀsᴛᴇ ᴀʟɢᴏ ǫᴜᴇ ɴᴏ sᴇ ᴘᴜᴇᴅᴇ ᴇsᴛᴀʙʟᴇᴄᴇʀ ᴄᴏᴍᴏ ᴛɪᴛᴜʟᴏ."
        )
        return

    bot.sendMessage(
        chat.id,
        f"» ᴇsᴛᴀʙʟᴇᴄɪᴅᴏ ᴄᴏʀʀᴇᴄᴛᴀᴍᴇɴᴛᴇ ᴇʟ ᴛɪᴛᴜʟᴏ ᴘᴀʀᴀ <code>{user_member.user.first_name or user_id}</code> "
        f"ᴛᴏ <code>{html.escape(title[:16])}</code>!",
        parse_mode=ParseMode.HTML,
    )


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def pin(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    user = update.effective_user
    chat = update.effective_chat
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message is None:
        msg.reply_text("» ʀᴇsᴘᴏɴᴅᴇ ᴀ ᴜɴ ᴍᴇɴsᴀJᴇ ᴘᴀʀᴀ ғɪJᴀʀʟᴏ !")
        return

    is_silent = True
    if len(args) >= 1:
        is_silent = (
            args[0].lower() != "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
            msg.reply_text(
                f"» ғɪJᴏ ᴄᴏɴ ᴇxɪᴛᴏ ᴇsᴇ ᴍᴇɴsᴀJᴇ.\nʜᴀɢᴀ ᴄʟɪᴄ ᴇɴ ᴇʟ ʙᴏᴛᴏɴ ᴅᴇ ᴀʙᴀJᴏ ᴘᴀʀᴀ ᴠᴇʀ ᴇʟ ᴍᴇɴsᴀJᴇ.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("ᴍᴇssᴀɢᴇ", url=f"{message_link}")]]
                ),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"ᴀɴᴄʟᴏ ᴜɴ ᴍᴇɴsᴀJᴇ\n"
            f"<b>ᴀɴᴄʟᴀᴅᴏ ᴘᴏʀ :</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def unpin(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id
    unpinner = chat.get_member(user.id)

    if (
        not (unpinner.can_pin_messages or unpinner.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text(
            "»  ɴᴏ ᴛɪᴇɴᴇs ᴘᴇʀᴍɪsᴏs ᴘᴀʀᴀ ᴩɪɴ/ᴜɴᴩɪɴ ᴍᴇɴsᴀJᴇs ᴇɴ ᴇsᴛᴇ ᴄʜᴀᴛ !"
        )
        return

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message and is_group:
        try:
            context.bot.unpinChatMessage(chat.id, prev_message.message_id)
            msg.reply_text(
                f"» ᴅᴇsᴀɴᴄʟᴀᴅᴏ ᴄᴏɴ ᴇxɪᴛᴏ <a href='{message_link}'> ᴇsᴛᴇ ᴍᴇɴsᴀJᴇ ᴀɴᴄʟᴀᴅᴏ</a>.",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

    if not prev_message and is_group:
        try:
            context.bot.unpinChatMessage(chat.id)
            msg.reply_text("» ᴅᴇsᴀɴᴄʟᴏ ᴄᴏɴ ᴇxɪᴛᴏ ᴇʟ ᴜʟᴛɪᴍᴏ ᴍᴇɴsᴀJᴇ ᴀɴᴄʟᴀᴅᴏ.")
        except BadRequest as excp:
            if excp.message == "Mensaje para desanclar no encontrado":
                msg.reply_text(
                    "» ɴᴏ ᴘᴜᴇᴅᴏ ᴅᴇsᴀɴᴄʟᴀʀ ᴇʟ ᴍᴇɴsᴀJᴇ, ᴛᴀʟ ᴠᴇᴢ ᴇsᴇ ᴍᴇɴsᴀJᴇ ᴇs ᴅᴇᴍᴀsɪᴀᴅᴏ ᴀɴᴛɪɢᴜᴏ ᴏ ᴛᴀʟ ᴠᴇᴢ ᴀʟɢᴜɪᴇɴ ʏᴀ ʟᴏ ᴅᴇsᴀɴᴄʟᴏ."
                )
            else:
                raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"ᴅᴇsᴀɴᴄʟᴏ ᴜɴ ᴍᴇɴsᴀJ\n"
        f"<b>ᴅᴇsᴀɴᴄʟᴀᴅᴏ ᴘᴏʀ :</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log_message


@run_async
@bot_admin
def pinned(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    msg = update.effective_message
    msg_id = (
        update.effective_message.reply_to_message.message_id
        if update.effective_message.reply_to_message
        else update.effective_message.message_id
    )

    chat = bot.getChat(chat_id=msg.chat.id)
    if chat.pinned_message:
        pinned_id = chat.pinned_message.message_id
        if msg.chat.username:
            link_chat_id = msg.chat.username
            message_link = f"https://t.me/{link_chat_id}/{pinned_id}"
        elif (str(msg.chat.id)).startswith("-100"):
            link_chat_id = (str(msg.chat.id)).replace("-100", "")
            message_link = f"https://t.me/c/{link_chat_id}/{pinned_id}"

        msg.reply_text(
            f"ᴀɴᴄʟᴀᴅᴏ ᴇɴ {html.escape(chat.title)}.",
            reply_to_message_id=msg_id,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴍᴇɴsᴀJᴇ",
                            url=f"https://t.me/{link_chat_id}/{pinned_id}",
                        )
                    ]
                ]
            ),
        )

    else:
        msg.reply_text(
            f"» ɴᴏ ʜᴀʏ ɴɪɴɢᴜɴ ᴍᴇɴsᴀJᴇ ᴀɴᴄʟᴀᴅᴏ ᴇɴ <b>{html.escape(chat.title)}!</b>",
            parse_mode=ParseMode.HTML,
        )


@run_async
@bot_admin
@user_admin
@connection_status
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type in [chat.SUPERGROUP, chat.CHANNEL]:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(
                "» ɴᴏ ᴛᴇɴɢᴏ ᴘᴇʀᴍɪsᴏs ᴘᴀʀᴀ ᴀᴄᴄᴇᴅᴇʀ ᴀ ʟᴏs ᴇɴʟᴀᴄᴇs ᴅᴇ ɪɴᴠɪᴛᴀᴄɪᴏɴ !",
            )
    else:
        update.effective_message.reply_text(
            "» sᴏʟᴏ ᴘᴜᴇᴅᴏ ᴅᴀʀ ᴇɴʟᴀᴄᴇs ᴅᴇ ɪɴᴠɪᴛᴀᴄɪᴏɴ ᴘᴀʀᴀ ɢʀᴜᴘᴏs ʏ ᴄᴀɴᴀʟᴇs !",
        )


@run_async
@connection_status
def adminlist(update, context):
    chat = update.effective_chat  # type: Optional[Chat] -> unused variable
    user = update.effective_user  # type: Optional[User]
    args = context.args  # -> unused variable
    bot = context.bot

    if update.effective_message.chat.type == "private":
        send_message(
            update.effective_message,
            "» ᴇsᴛᴇ ᴄᴏᴍᴀɴᴅᴏ sᴏʟᴏ sᴇ ᴘᴜᴇᴅᴇ ᴜsᴀʀ ᴇɴ ɢʀᴜᴘᴏs ɴᴏ ᴇɴ ᴘʀɪᴠᴀᴅᴏ.",
        )
        return

    update.effective_chat
    chat_id = update.effective_chat.id
    chat_name = update.effective_message.chat.title  # -> unused variable

    try:
        msg = update.effective_message.reply_text(
            "» ᴏʙᴛᴇɴɪᴇɴᴅᴏ ʟᴀ ʟɪsᴛᴀ ᴅᴇ ᴀᴅᴍɪɴɪsᴛʀᴀᴅᴏʀᴇs...",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest:
        msg = update.effective_message.reply_text(
            "» ᴏʙᴛᴇɴɪᴇɴᴅᴏ ʟᴀ ʟɪsᴛᴀ ᴅᴇ ᴀᴅᴍɪɴɪsᴛʀᴀᴅᴏʀᴇs...",
            quote=False,
            parse_mode=ParseMode.HTML,
        )

    administrators = bot.getChatAdministrators(chat_id)
    text = "ᴀᴅᴍɪɴɪᴛʀᴀᴅᴏʀᴇs ᴇɴ <b>{}</b>:".format(html.escape(update.effective_chat.title))

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ ᴄᴜᴇɴᴛᴀ ᴇʟɪᴍɪɴᴀᴅᴀ"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " + (user.last_name or "")),
                ),
            )

        if user.is_bot:
            administrators.remove(admin)
            continue

        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "creador":
            text += "\n 🥀 ᴏᴡɴᴇʀ :"
            text += "\n<code> • </code>{}\n".format(name)

            if custom_title:
                text += f"<code> ┗━ {html.escape(custom_title)}</code>\n"

    text += "\n💫 ᴀᴅᴍɪɴs :"

    custom_admin_list = {}
    normal_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ ᴄᴜᴇɴᴛᴀ ᴇʟɪᴍɪɴᴀᴅᴀ"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " + (user.last_name or "")),
                ),
            )
        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "administrador":
            if custom_title:
                try:
                    custom_admin_list[custom_title].append(name)
                except KeyError:
                    custom_admin_list.update({custom_title: [name]})
            else:
                normal_admin_list.append(name)

    for admin in normal_admin_list:
        text += "\n<code> • </code>{}".format(admin)

    for admin_group in custom_admin_list.copy():
        if len(custom_admin_list[admin_group]) == 1:
            text += "\n<code> • </code>{} | <code>{}</code>".format(
                custom_admin_list[admin_group][0],
                html.escape(admin_group),
            )
            custom_admin_list.pop(admin_group)

    text += "\n"
    for admin_group, value in custom_admin_list.items():
        text += "\n🔮 <code>{}</code>".format(admin_group)
        for admin in value:
            text += "\n<code> • </code>{}".format(admin)
        text += "\n"

    try:
        msg.edit_text(text, parse_mode=ParseMode.HTML)
    except BadRequest:  # if original message is deleted
        return


@run_async
@bot_admin
@can_promote
@user_admin
@loggable
def button(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    bot: Optional[Bot] = context.bot
    match = re.match(r"demote_\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        member = chat.get_member(user_id)
        bot_member = chat.get_member(bot.id)
        bot_permissions = promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_voice_chats=bot_member.can_manage_voice_chats,
        )
        demoted = bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_voice_chats=False,
        )
        if demoted:
            update.effective_message.edit_text(
                f"ᴅᴇᴍᴏᴛᴇʀ : {mention_html(user.id, user.first_name)}\nᴜsᴇʀ : {mention_html(member.user.id, member.user.first_name)}!",
                parse_mode=ParseMode.HTML,
            )
            query.answer("ᴅᴇᴍᴏᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ !")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#DEGRADAR\n"
                f"<b>ᴅᴇɢʀᴀᴅᴀᴅᴏʀ :</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>ᴜsᴜᴀʀɪᴏ :</b> {mention_html(member.user.id, member.user.first_name)}"
            )
    else:
        update.effective_message.edit_text(
            "» ɴᴏ sᴇ ᴘᴜᴅᴏ ᴅᴇɢʀᴀᴅᴀʀ, ᴛᴀʟ ᴠᴇᴢ ᴇsᴇ ᴜsᴜᴀʀɪᴏ ɴᴏ ᴇs ᴜɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴅᴏʀ ᴏ ᴛᴀʟ ᴠᴇᴢ ᴀʙᴀɴᴅᴏɴᴏ ᴇʟ ɢʀᴜᴘᴏ !"
        )
        return ""


__help__ = """
*Comandos de usuario*:
» /admins*:* Lista de administradores en el chat.
» /pinned*:* Para obtener el mensaje anclado actual.

*Los siguientes comandos son solo para administradores:* 
» /pin*:* Fija silenciosamente el mensaje al que se respondió - agregue `'loud'` o `'notify'` para dar notificaciones a los usuarios.
» /unpin*:* Desancla el mensaje anclado actualmente.
» /invitelink*:* Recibe enlace de invitación.
» /promote*:* Promueve al usuario respondido.
» /lowpromote*:* Promueve al usuario respondido con medio derecho.
» /fullpromote*:* Promueve al usuario respondido con todos los derechos.
» /demote*:* Degrada al usuario respondió.
» /title <titulo aqui>*:* Establece un título personalizado para un administrador que el bot promovió.
» /admincache*:* fuerza la actualización de la lista de administradores.
» /del*:* Borra el mensaje que respondiste.
» /purge*:* Elimina todos los mensajes entre este y el mensaje respondido.
» /purge <entero X>*:* Elimina el mensaje respondido y X mensajes que lo siguen si se respondió a un mensaje.
» /setgtitle <texto>*:* Establece el título del grupo.
» /setgpic*:* Responde a una imagen para establecer como foto de grupo.
» /setdesc*:* Establece la descripción del grupo.
» /setsticker*:* Establece stickers de grupo.
"""

SET_DESC_HANDLER = CommandHandler("setdesc", set_desc)
SET_STICKER_HANDLER = CommandHandler("setsticker", set_sticker)
SETCHATPIC_HANDLER = CommandHandler("setgpic", setchatpic)
RMCHATPIC_HANDLER = CommandHandler("delgpic", rmchatpic)
SETCHAT_TITLE_HANDLER = CommandHandler("setgtitle", setchat_title)

ADMINLIST_HANDLER = DisableAbleCommandHandler(["admins", "staff"], adminlist)

PIN_HANDLER = CommandHandler("pin", pin)
UNPIN_HANDLER = CommandHandler("unpin", unpin)
PINNED_HANDLER = CommandHandler("pinned", pinned)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote)
FULLPROMOTE_HANDLER = DisableAbleCommandHandler("fullpromote", fullpromote)
LOW_PROMOTE_HANDLER = DisableAbleCommandHandler("lowpromote", lowpromote)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote)

SET_TITLE_HANDLER = CommandHandler("title", set_title)
ADMIN_REFRESH_HANDLER = CommandHandler(
    ["admincache", "reload", "refresh"],
    refresh_admin,
)

dispatcher.add_handler(SET_DESC_HANDLER)
dispatcher.add_handler(SET_STICKER_HANDLER)
dispatcher.add_handler(SETCHATPIC_HANDLER)
dispatcher.add_handler(RMCHATPIC_HANDLER)
dispatcher.add_handler(SETCHAT_TITLE_HANDLER)
dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(PINNED_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(FULLPROMOTE_HANDLER)
dispatcher.add_handler(LOW_PROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(ADMIN_REFRESH_HANDLER)

__mod_name__ = "Aᴅᴍɪɴs"
__command_list__ = [
    "setdesc" "setsticker" "setgpic" "delgpic" "setgtitle" "adminlist",
    "admins",
    "invitelink",
    "promote",
    "fullpromote",
    "lowpromote",
    "demote",
    "admincache",
]
__handlers__ = [
    SET_DESC_HANDLER,
    SET_STICKER_HANDLER,
    SETCHATPIC_HANDLER,
    RMCHATPIC_HANDLER,
    SETCHAT_TITLE_HANDLER,
    ADMINLIST_HANDLER,
    PIN_HANDLER,
    UNPIN_HANDLER,
    PINNED_HANDLER,
    INVITE_HANDLER,
    PROMOTE_HANDLER,
    FULLPROMOTE_HANDLER,
    LOW_PROMOTE_HANDLER,
    DEMOTE_HANDLER,
    SET_TITLE_HANDLER,
    ADMIN_REFRESH_HANDLER,
]
