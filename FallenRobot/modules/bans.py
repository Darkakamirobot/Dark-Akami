import html

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, run_async
from telegram.utils.helpers import mention_html

from FallenRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    LOGGER,
    OWNER_ID,
    TIGERS,
    WOLVES,
    dispatcher,
)
from FallenRobot.modules.disable import DisableAbleCommandHandler
from FallenRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_delete,
    can_restrict,
    connection_status,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
    user_admin,
    user_can_ban,
)
from FallenRobot.modules.helper_funcs.extraction import extract_user_and_text
from FallenRobot.modules.helper_funcs.string_handling import extract_time
from FallenRobot.modules.log_channel import gloggable, loggable


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot = context.bot
    args = context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dudo que sea un usuario.")
        return log_message
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "Usuario no encontrado":
            raise
        message.reply_text("Parece que no puedo encontrar a esta persona.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Oh yeah, ban a mi, noob!")
        return log_message

    if is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
        if user_id == OWNER_ID:
            message.reply_text("Tratando de ponerme en contra de un desastre a nivel de Dios, ¿Eh?")
        elif user_id in DEV_USERS:
            message.reply_text("No puedo actuar contra nuestro dueño.")
        elif user_id in DRAGONS:
            message.reply_text(
                "Luchar contra este Dragón aquí pondrá en peligro la vida de civiles.."
            )
        elif user_id in DEMONS:
            message.reply_text(
                "Trae una orden de la Asociación de Héroes para luchar contra un desastre Demoníaco."
            )
        elif user_id in TIGERS:
            message.reply_text(
                "Trae una orden de la Asociación de Héroes para luchar contra un desastre de Tigre.."
            )
        elif user_id in WOLVES:
            message.reply_text("Las habilidades de los lobos los hacen inmunes a la prohibición.!")
        else:
            message.reply_text("Este usuario tiene inmunidad y no puede ser prohibido.")
        return log_message
    if message.text.startswith("/s"):
        silent = True
        if not can_delete(chat, context.bot.id):
            return ""
    else:
        silent = False
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#{'S' if silent else ''}ʙᴀɴᴇᴀᴅᴏ\n"
        f"<b>ʙᴀɴᴇᴀᴅᴏ ᴘᴏʀ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴜᴀʀɪᴏ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += "\n<b>ʀᴀᴢᴏɴ:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)

        if silent:
            if message.reply_to_message:
                message.reply_to_message.delete()
            message.delete()
            return log

        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        reply = (
            f"<code>❕</code><b>ʙᴀɴ ᴇᴠᴇɴᴛ</b>\n"
            f"<code> </code><b>•  ʙᴀɴᴇᴀᴅᴏ ᴘᴏʀ:</b> {mention_html(user.id, user.first_name)}\n"
            f"<code> </code><b>•  ᴜsᴜᴀʀɪᴏ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            reply += f"\n<code> </code><b>•  ʀᴀᴢᴏɴ:</b> \n{html.escape(reason)}"
        bot.sendMessage(chat.id, reply, parse_mode=ParseMode.HTML, quote=False)
        return log

    except BadRequest as excp:
        if excp.message == "Mensaje de respuesta no encontrado":
            # Do not reply
            if silent:
                return log
            message.reply_text("ʙᴀɴᴇᴀᴅᴏ !", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR al prohibir al usuario %s en el chat %s (%s) debido a %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Uhm... eso no funcionó...")

    return log_message


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def temp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dudo que sea un usuario.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "Usuario no encontrado":
            raise
        message.reply_text("Parece que no puedo encontrar a este usuario.")
        return log_message
    if user_id == bot.id:
        message.reply_text("No me voy a BANEAR, ¿Estás loco?")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("no tengo ganas.")
        return log_message

    if not reason:
        message.reply_text("No has especificado un tiempo para prohibir a este usuario.!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "ᴛᴇᴍᴩ ʙᴀɴ\n"
        f"<b>ʙᴀɴᴇᴀᴅᴏ ᴘᴏʀ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴜᴀʀɪᴏ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>ᴛɪᴇᴍᴘᴏ:</b> {time_val}"
    )
    if reason:
        log += "\n<b>ʀᴀᴢᴏɴ:</b> {}".format(reason)

    try:
        chat.kick_member(user_id, until_date=bantime)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"ʙᴀɴᴇᴀᴅᴏ! ᴜsᴜᴀʀɪᴏ {mention_html(member.user.id, html.escape(member.user.first_name))} "
            f"ᴀʜᴏʀᴀ ᴇsᴛᴀ ʙᴀɴᴇᴀᴅᴏ ᴘᴏʀ {time_val}.",
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Mensaje de respuesta no encontrado":
            # Do not reply
            message.reply_text(
                f"Baneado! El usuario será baneado por {time_val}.", quote=False
            )
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR al prohibir al usuario %s en el chat %s (%s) debido a %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Bueno maldita sea, no puedo prohibir a ese usuario.")

    return log_message


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def kick(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dudo que sea un usuario.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "Usuario no encontrado":
            raise

        message.reply_text("Parece que no puedo encontrar a este usuario.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Yeahhh no voy a hacer eso.")
        return log_message

    if is_user_ban_protected(chat, user_id):
        message.reply_text("Realmente desearía poder patear a este usuario....")
        return log_message

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"One Kicked! {mention_html(member.user.id, html.escape(member.user.first_name))}.",
            parse_mode=ParseMode.HTML,
        )
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"ᴘᴀᴛᴇᴀᴅᴏ\n"
            f"<b>ᴘᴀᴛᴇᴀᴅᴏ ᴘᴏʀ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>ᴜsᴜᴀʀɪᴏ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {reason}"

        return log

    else:
        message.reply_text("Bueno maldita sea, no puedo patear a ese usuario.")

    return log_message


@run_async
@bot_admin
@can_restrict
def kickme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("Desearía poder ... pero eres un administrador.")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("*Te saca del grupo*")
    else:
        update.effective_message.reply_text("¿Eh? No puedo :/")


@run_async
@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def unban(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dudo que sea un usuario.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "Usuario no encontrado":
            raise
        message.reply_text("Parece que no puedo encontrar a este usuario.")
        return log_message
    if user_id == bot.id:
        message.reply_text("¿Cómo me desbanearía si no estuviera aquí...?")
        return log_message

    if is_user_in_chat(chat, user_id):
        message.reply_text("¿No está esta persona ya aquí???")
        return log_message

    chat.unban_member(user_id)
    message.reply_text("Yep, este usuario puede unirse!")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"ᴅᴇsʙᴀɴᴇᴀᴅᴏ\n"
        f"<b>ᴅᴇsʙᴀɴᴇᴀᴅᴏ ᴘᴏʀ :</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴜᴀʀɪᴏ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += f"\n<b>ʀᴀᴢᴏɴ:</b> {reason}"

    return log


@run_async
@connection_status
@bot_admin
@can_restrict
@gloggable
def selfunban(context: CallbackContext, update: Update) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in DRAGONS or user.id not in TIGERS:
        return

    try:
        chat_id = int(args[0])
    except:
        message.reply_text("Proporcione una ID de chat válida.")
        return

    chat = bot.getChat(chat_id)

    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "Usuario no encontrado":
            message.reply_text("Parece que no puedo encontrar a este usuario.")
            return
        else:
            raise

    if is_user_in_chat(chat, user.id):
        message.reply_text("¿No estás ya en el chat?")
        return

    chat.unban_member(user.id)
    message.reply_text("Yep, te he desbaneado.")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"ᴅᴇsʙᴀɴᴇᴀᴅᴏ\n"
        f"<b>ᴅᴇsʙᴀɴᴇᴀᴅᴏ ᴘᴏʀ:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜsᴜᴀʀɪᴏ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )

    return log


__help__ = """
 ❍ /kickme*:* Patea al usuario que emitió el comando.

*Solo administradores:*
 ❍ /ban <userhandle>*:* Prohíbe a un usuario. (a través de identificador o respuesta)
 ❍ /sban <userhandle>*:* Prohibe silenciosamente a un usuario. Borra el comando, respondiendo al mensaje y no respondiendo. (a través de identificador o respuesta).
 ❍ /tban <userhandle> x(m/h/d)*:* Banea a un usuario por `x` tiempo. (a través de identificador o respuesta). `m` = `minutos`, `h` = `horas`, `d` = `días`.
 ❍ /unban <userhandle>*:* Desbanea a un usuario. (a través de identificador o respuesta).
 ❍ /kick <userhandle>*:* Expulsa a un usuario del grupo (mediante identificador o respuesta).
"""

BAN_HANDLER = CommandHandler(["ban", "sban"], ban)
TEMPBAN_HANDLER = CommandHandler(["tban"], temp_ban)
KICK_HANDLER = CommandHandler("kick", kick)
UNBAN_HANDLER = CommandHandler("unban", unban)
ROAR_HANDLER = CommandHandler("roar", selfunban)
KICKME_HANDLER = DisableAbleCommandHandler("kickme", kickme, filters=Filters.group)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(ROAR_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)

__mod_name__ = "Bᴀɴs​"
__handlers__ = [
    BAN_HANDLER,
    TEMPBAN_HANDLER,
    KICK_HANDLER,
    UNBAN_HANDLER,
    ROAR_HANDLER,
    KICKME_HANDLER,
]
