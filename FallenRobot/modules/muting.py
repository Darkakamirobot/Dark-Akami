import html
from typing import Optional

from telegram import Bot, Chat, ChatPermissions, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, run_async
from telegram.utils.helpers import mention_html

from FallenRobot import LOGGER, TIGERS, dispatcher
from FallenRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    connection_status,
    is_user_admin,
    user_admin,
)
from FallenRobot.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from FallenRobot.modules.helper_funcs.string_handling import extract_time
from FallenRobot.modules.log_channel import loggable


def check_user(user_id: int, bot: Bot, chat: Chat) -> Optional[str]:
    if not user_id:
        reply = "Parece que no te refieres a un usuario o el ID especificado es incorrecto.."
        return reply

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "Usuario no encontrado":
            reply = "Parece que no puedo encontrar a este usuario"
            return reply
        else:
            raise

    if user_id == bot.id:
        reply = "No me voy a enmudecer, ¿Qué tan alto estás?"
        return reply

    if is_user_admin(chat, user_id, member) or user_id in TIGERS:
        reply = "No puedo. Encuentra a alguien más para silenciar pero no a este."
        return reply

    return None


@run_async
@connection_status
@bot_admin
@user_admin
@loggable
def mute(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = extract_user_and_text(message, args)
    reply = check_user(user_id, bot, chat)

    if reply:
        message.reply_text(reply)
        return ""

    member = chat.get_member(user_id)

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#MUTE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Usuario:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    if reason:
        log += f"\n<b>Razón:</b> {reason}"

    if member.can_send_messages is None or member.can_send_messages:
        chat_permissions = ChatPermissions(can_send_messages=False)
        bot.restrict_chat_member(chat.id, user_id, chat_permissions)
        bot.sendMessage(
            chat.id,
            f"Silenciado <b>{html.escape(member.user.first_name)}</b> sin fecha de caducidad!",
            parse_mode=ParseMode.HTML,
        )
        return log

    else:
        message.reply_text("Este usuario ya está silenciado!")

    return ""


@run_async
@connection_status
@bot_admin
@user_admin
@loggable
def unmute(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "Tendrás que darme un nombre de usuario para dejar de silenciar, o responda a alguien para que no esté silenciado."
        )
        return ""

    member = chat.get_member(int(user_id))

    if member.status != "kicked" and member.status != "left":
        if (
            member.can_send_messages
            and member.can_send_media_messages
            and member.can_send_other_messages
            and member.can_add_web_page_previews
        ):
            message.reply_text("Este usuario ya tiene derecho a hablar.")
        else:
            chat_permissions = ChatPermissions(
                can_send_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
            try:
                bot.restrict_chat_member(chat.id, int(user_id), chat_permissions)
            except BadRequest:
                pass
            bot.sendMessage(
                chat.id,
                f"Permitiré que <b>{html.escape(member.user.first_name)}</b> envíe mensajes de texto!",
                parse_mode=ParseMode.HTML,
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#UNMUTE\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>Usuario:</b> {mention_html(member.user.id, member.user.first_name)}"
            )
    else:
        message.reply_text(
            "Este usuario ni siquiera está en el chat, desactivar el silencio no hará que hable más de lo que "
            "ya lo hacen!"
        )

    return ""


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
def temp_mute(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = extract_user_and_text(message, args)
    reply = check_user(user_id, bot, chat)

    if reply:
        message.reply_text(reply)
        return ""

    member = chat.get_member(user_id)

    if not reason:
        message.reply_text("No has especificado el tiempo para silenciar a este usuario!")
        return ""

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    mutetime = extract_time(message, time_val)

    if not mutetime:
        return ""

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#TEMP MUTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Usuario:</b> {mention_html(member.user.id, member.user.first_name)}\n"
        f"<b>Tiempo:</b> {time_val}"
    )
    if reason:
        log += f"\n<b>Razón:</b> {reason}"

    try:
        if member.can_send_messages is None or member.can_send_messages:
            chat_permissions = ChatPermissions(can_send_messages=False)
            bot.restrict_chat_member(
                chat.id, user_id, chat_permissions, until_date=mutetime
            )
            bot.sendMessage(
                chat.id,
                f"Silenciado <b>{html.escape(member.user.first_name)}</b> por {time_val}!",
                parse_mode=ParseMode.HTML,
            )
            return log
        else:
            message.reply_text("Este usuario ya está silenciado.")

    except BadRequest as excp:
        if excp.message == "Mensaje de respuesta no encontrado":
            # Do not reply
            message.reply_text(f"Silenciado por {time_val}!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR al silenciar al usuario %s en el chat %s (%s) debido a %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Bueno maldita sea, no puedo silenciar a ese usuario.")

    return ""


__help__ = """
*Sólo administradores:*
 ❍ /mute <id>*:* Silencia a un usuario. También se puede usar como respuesta, silenciando al usuario respondido.
 ❍ /tmute <id> x(m/h/d)*:* Silencia a un usuario por x tiempo. (via id, o en respuesta). `m` = `minutos`, `h` = `horas`, `d` = `dias`.
 ❍ /unmute <id>*:* Desmutea al usuario. También se puede usar como respuesta, silenciando al usuario respondido..
"""

MUTE_HANDLER = CommandHandler("mute", mute)
UNMUTE_HANDLER = CommandHandler("unmute", unmute)
TEMPMUTE_HANDLER = CommandHandler(["tmute", "tempmute"], temp_mute)

dispatcher.add_handler(MUTE_HANDLER)
dispatcher.add_handler(UNMUTE_HANDLER)
dispatcher.add_handler(TEMPMUTE_HANDLER)

__mod_name__ = "Mᴜᴛᴇ​"
__handlers__ = [MUTE_HANDLER, UNMUTE_HANDLER, TEMPMUTE_HANDLER]
