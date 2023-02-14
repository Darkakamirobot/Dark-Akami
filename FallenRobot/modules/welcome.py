import html
import random
import re
import time
from contextlib import suppress
from functools import partial

from telegram import (
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    run_async,
)
from telegram.utils.helpers import escape_markdown, mention_html, mention_markdown

import FallenRobot
import FallenRobot.modules.sql.welcome_sql as sql
from FallenRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    EVENT_LOGS,
    LOGGER,
    OWNER_ID,
    TIGERS,
    WOLVES,
    dispatcher,
)
from FallenRobot.modules.helper_funcs.chat_status import (
    is_user_ban_protected,
    user_admin,
)
from FallenRobot.modules.helper_funcs.misc import build_keyboard, revert_buttons
from FallenRobot.modules.helper_funcs.msg_types import get_welcome_type
from FallenRobot.modules.helper_funcs.string_handling import (
    escape_invalid_curly_brackets,
    markdown_parser,
)
from FallenRobot.modules.log_channel import loggable
from FallenRobot.modules.sql.global_bans_sql import is_user_gbanned

VALID_WELCOME_FORMATTERS = [
    "first",
    "last",
    "fullname",
    "username",
    "id",
    "count",
    "chatname",
    "mention",
]

ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: dispatcher.bot.send_message,
    sql.Types.BUTTON_TEXT.value: dispatcher.bot.send_message,
    sql.Types.STICKER.value: dispatcher.bot.send_sticker,
    sql.Types.DOCUMENT.value: dispatcher.bot.send_document,
    sql.Types.PHOTO.value: dispatcher.bot.send_photo,
    sql.Types.AUDIO.value: dispatcher.bot.send_audio,
    sql.Types.VOICE.value: dispatcher.bot.send_voice,
    sql.Types.VIDEO.value: dispatcher.bot.send_video,
}

VERIFIED_USER_WAITLIST = {}


# do not async
def send(update, message, keyboard, backup_message):
    chat = update.effective_chat
    cleanserv = sql.clean_service(chat.id)
    reply = update.message.message_id
    # Clean service welcome
    if cleanserv:
        try:
            dispatcher.bot.delete_message(chat.id, update.message.message_id)
        except BadRequest:
            pass
        reply = False
    try:
        msg = update.effective_message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
            reply_to_message_id=reply,
        )
    except BadRequest as excp:
        if excp.message == "Mensaje de respuesta no encontrado":
            msg = update.effective_message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
                quote=False,
            )
        elif excp.message == "Button_url_invalid":
            msg = update.effective_message.reply_text(
                markdown_parser(
                    backup_message + "\nNota: el mensaje actual tiene una URL no válida "
                    "en uno de sus botones. Por favor actualice."
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )
        elif excp.message == "Protocolo de URL no admitido":
            msg = update.effective_message.reply_text(
                markdown_parser(
                    backup_message + "\nNota: el mensaje actual tiene botones que "
                    "usar protocolos de URL que no son compatibles con "
                    "telegrama. Por favor actualice."
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )
        elif excp.message == "Host de URL incorrecto":
            msg = update.effective_message.reply_text(
                markdown_parser(
                    backup_message + "\nNota: el mensaje actual tiene algunas URL incorrectas. "
                    "Por favor actualice."
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )
            LOGGER.warning(message)
            LOGGER.warning(keyboard)
            LOGGER.exception("¡No se pudo analizar! obtuvo errores de host de URL no válidos")
        elif excp.message == "No tiene derechos para enviar un mensaje.":
            return
        else:
            msg = update.effective_message.reply_text(
                markdown_parser(
                    backup_message + "\nNota: Ocurrió un error al enviar el "
                    "mensaje personalizado. Por favor actualice."
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )
            LOGGER.exception()
    return msg


@run_async
@loggable
def new_member(update: Update, context: CallbackContext):
    bot, job_queue = context.bot, context.job_queue
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    should_welc, cust_welcome, cust_content, welc_type = sql.get_welc_pref(chat.id)
    welc_mutes = sql.welcome_mutes(chat.id)
    human_checks = sql.get_human_checks(user.id, chat.id)

    new_members = update.effective_message.new_chat_members

    for new_mem in new_members:
        welcome_log = None
        res = None
        sent = None
        should_mute = True
        welcome_bool = True
        media_wel = False

        if should_welc:
            reply = update.message.message_id
            cleanserv = sql.clean_service(chat.id)
            # Clean service welcome
            if cleanserv:
                try:
                    dispatcher.bot.delete_message(chat.id, update.message.message_id)
                except BadRequest:
                    pass
                reply = False

            # Give the owner a special welcome
            if new_mem.id == OWNER_ID:
                update.effective_message.reply_text(
                    "Oh, Genos? Hagamos que esto se mueva.", reply_to_message_id=reply
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"El propietario del bot acaba de unirse al grupo"
                )
                continue

            # Welcome Devs
            elif new_mem.id in DEV_USERS:
                update.effective_message.reply_text(
                    "¡Relájate! Un miembro de la Asociación de Héroes acaba de unirse.",
                    reply_to_message_id=reply,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"Un dev del bot acaba de unirse al grupo"
                )
                continue

            # Welcome Sudos
            elif new_mem.id in DRAGONS:
                update.effective_message.reply_text(
                    "Whoa! ¡Se acaba de unir un desastre de Dragon! Manténgase alerta!",
                    reply_to_message_id=reply,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"Un sudo del bot acaba de unirse al grupo"
                )
                continue

            # Welcome Support
            elif new_mem.id in DEMONS:
                update.effective_message.reply_text(
                    "Huh! Alguien con un nivel de desastre Demon acaba de unirse!",
                    reply_to_message_id=reply,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"Un soporte del bot acaba de unirse al grupo"
                )
                continue

            # Welcome Whitelisted
            elif new_mem.id in TIGERS:
                update.effective_message.reply_text(
                    "¡Rugido! Un desastre de Tiger acaba de unirse!", reply_to_message_id=reply
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"Un usuario de la lista blanca se unió al chat."
                )
                continue

            # Welcome Tigers
            elif new_mem.id in WOLVES:
                update.effective_message.reply_text(
                    "¡Awoo! Un desastre de Wolf acaba de unirse!", reply_to_message_id=reply
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"Un usuario de la lista blanca se unió al chat."
                )
                continue

            # Welcome yourself
            elif new_mem.id == bot.id:
                if not FallenRobot.ALLOW_CHATS:
                    with suppress(BadRequest):
                        update.effective_message.reply_text(
                            f"Los grupos están deshabilitados para {bot.first_name}, Me voy de aquí."
                        )
                    bot.leave_chat(update.effective_chat.id)
                    return
                bot.send_message(
                    EVENT_LOGS,
                    "#NEW_GROUP\n<b>Group name:</b> {}\n<b>ID:</b> <code>{}</code>".format(
                        html.escape(chat.title),
                        chat.id,
                    ),
                    parse_mode=ParseMode.HTML,
                )
                update.effective_message.reply_text(
                    "Watashi ga kita !", reply_to_message_id=reply
                )
                continue

            else:
                buttons = sql.get_welc_buttons(chat.id)
                keyb = build_keyboard(buttons)

                if welc_type not in (sql.Types.TEXT, sql.Types.BUTTON_TEXT):
                    media_wel = True

                first_name = (
                    new_mem.first_name or "PersonWithNoName"
                )  # edge case of empty name - occurs for some bugs.

                if cust_welcome:
                    if cust_welcome == sql.DEFAULT_WELCOME:
                        cust_welcome = random.choice(
                            sql.DEFAULT_WELCOME_MESSAGES
                        ).format(first=escape_markdown(first_name))

                    if new_mem.last_name:
                        fullname = escape_markdown(f"{first_name} {new_mem.last_name}")
                    else:
                        fullname = escape_markdown(first_name)
                    count = chat.get_members_count()
                    mention = mention_markdown(new_mem.id, escape_markdown(first_name))
                    if new_mem.username:
                        username = "@" + escape_markdown(new_mem.username)
                    else:
                        username = mention

                    valid_format = escape_invalid_curly_brackets(
                        cust_welcome, VALID_WELCOME_FORMATTERS
                    )
                    res = valid_format.format(
                        first=escape_markdown(first_name),
                        last=escape_markdown(new_mem.last_name or first_name),
                        fullname=escape_markdown(fullname),
                        username=username,
                        mention=mention,
                        count=count,
                        chatname=escape_markdown(chat.title),
                        id=new_mem.id,
                    )

                else:
                    res = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                        first=escape_markdown(first_name)
                    )
                    keyb = []

                backup_message = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                    first=escape_markdown(first_name)
                )
                keyboard = InlineKeyboardMarkup(keyb)

        else:
            welcome_bool = False
            res = None
            keyboard = None
            backup_message = None
            reply = None

        # User exceptions from welcomemutes
        if (
            is_user_ban_protected(chat, new_mem.id, chat.get_member(new_mem.id))
            or human_checks
        ):
            should_mute = False
        # Join welcome: soft mute
        if new_mem.is_bot:
            should_mute = False

        if user.id == new_mem.id:
            if should_mute:
                if welc_mutes == "soft":
                    bot.restrict_chat_member(
                        chat.id,
                        new_mem.id,
                        permissions=ChatPermissions(
                            can_send_messages=True,
                            can_send_media_messages=False,
                            can_send_other_messages=False,
                            can_invite_users=False,
                            can_pin_messages=False,
                            can_send_polls=False,
                            can_change_info=False,
                            can_add_web_page_previews=False,
                        ),
                        until_date=(int(time.time() + 24 * 60 * 60)),
                    )
                if welc_mutes == "strong":
                    welcome_bool = False
                    if not media_wel:
                        VERIFIED_USER_WAITLIST.update(
                            {
                                new_mem.id: {
                                    "should_welc": should_welc,
                                    "media_wel": False,
                                    "status": False,
                                    "update": update,
                                    "res": res,
                                    "keyboard": keyboard,
                                    "backup_message": backup_message,
                                }
                            }
                        )
                    else:
                        VERIFIED_USER_WAITLIST.update(
                            {
                                new_mem.id: {
                                    "should_welc": should_welc,
                                    "chat_id": chat.id,
                                    "status": False,
                                    "media_wel": True,
                                    "cust_content": cust_content,
                                    "welc_type": welc_type,
                                    "res": res,
                                    "keyboard": keyboard,
                                }
                            }
                        )
                    new_join_mem = f'<a href="tg://user?id={user.id}">{html.escape(new_mem.first_name)}</a>'
                    message = msg.reply_text(
                        f"{new_join_mem}, haz clic en el botón de abajo para demostrar que eres humano.\nTienes 120 segundos.",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                {
                                    InlineKeyboardButton(
                                        text="Si, soy humano.",
                                        callback_data=f"user_join_({new_mem.id})",
                                    )
                                }
                            ]
                        ),
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=reply,
                    )
                    bot.restrict_chat_member(
                        chat.id,
                        new_mem.id,
                        permissions=ChatPermissions(
                            can_send_messages=False,
                            can_invite_users=False,
                            can_pin_messages=False,
                            can_send_polls=False,
                            can_change_info=False,
                            can_send_media_messages=False,
                            can_send_other_messages=False,
                            can_add_web_page_previews=False,
                        ),
                    )
                    job_queue.run_once(
                        partial(check_not_bot, new_mem, chat.id, message.message_id),
                        120,
                        name="welcomemute",
                    )

        if welcome_bool:
            if media_wel:
                sent = ENUM_FUNC_MAP[welc_type](
                    chat.id,
                    cust_content,
                    caption=res,
                    reply_markup=keyboard,
                    reply_to_message_id=reply,
                    parse_mode="markdown",
                )
            else:
                sent = send(update, res, keyboard, backup_message)
            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

        if welcome_log:
            return welcome_log

        return (
            f"{html.escape(chat.title)}\n"
            f"#USER_JOINED\n"
            f"<b>User</b>: {mention_html(user.id, user.first_name)}\n"
            f"<b>ID</b>: <code>{user.id}</code>"
        )

    return ""


def check_not_bot(member, chat_id, message_id, context):
    bot = context.bot
    member_dict = VERIFIED_USER_WAITLIST.pop(member.id)
    member_status = member_dict.get("status")
    if not member_status:
        try:
            bot.unban_chat_member(chat_id, member.id)
        except:
            pass

        try:
            bot.edit_message_text(
                "*Usuario pateado*\nSiempre pueden volver a unirse y probar.",
                chat_id=chat_id,
                message_id=message_id,
            )
        except:
            pass


@run_async
def left_member(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    should_goodbye, cust_goodbye, goodbye_type = sql.get_gdbye_pref(chat.id)

    if user.id == bot.id:
        return

    if should_goodbye:
        reply = update.message.message_id
        cleanserv = sql.clean_service(chat.id)
        # Clean service welcome
        if cleanserv:
            try:
                dispatcher.bot.delete_message(chat.id, update.message.message_id)
            except BadRequest:
                pass
            reply = False

        left_mem = update.effective_message.left_chat_member
        if left_mem:
            # Dont say goodbyes to gbanned users
            if is_user_gbanned(left_mem.id):
                return

            # Ignore bot being kicked
            if left_mem.id == bot.id:
                return

            # if media goodbye, use appropriate function for it
            if goodbye_type != sql.Types.TEXT and goodbye_type != sql.Types.BUTTON_TEXT:
                ENUM_FUNC_MAP[goodbye_type](chat.id, cust_goodbye)
                return

            first_name = (
                left_mem.first_name or "PersonWithNoName"
            )  # edge case of empty name - occurs for some bugs.
            if cust_goodbye:
                if cust_goodbye == sql.DEFAULT_GOODBYE:
                    cust_goodbye = random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(
                        first=escape_markdown(first_name)
                    )
                if left_mem.last_name:
                    fullname = escape_markdown(f"{first_name} {left_mem.last_name}")
                else:
                    fullname = escape_markdown(first_name)
                count = chat.get_members_count()
                mention = mention_markdown(left_mem.id, first_name)
                if left_mem.username:
                    username = "@" + escape_markdown(left_mem.username)
                else:
                    username = mention

                valid_format = escape_invalid_curly_brackets(
                    cust_goodbye, VALID_WELCOME_FORMATTERS
                )
                res = valid_format.format(
                    first=escape_markdown(first_name),
                    last=escape_markdown(left_mem.last_name or first_name),
                    fullname=escape_markdown(fullname),
                    username=username,
                    mention=mention,
                    count=count,
                    chatname=escape_markdown(chat.title),
                    id=left_mem.id,
                )
                buttons = sql.get_gdbye_buttons(chat.id)
                keyb = build_keyboard(buttons)

            else:
                res = random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(
                    first=first_name
                )
                keyb = []

            keyboard = InlineKeyboardMarkup(keyb)

            send(
                update,
                res,
                keyboard,
                random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(first=first_name),
            )


@run_async
@user_admin
def welcome(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    # if no args, show current replies.
    if not args or args[0].lower() == "noformat":
        noformat = True
        pref, welcome_m, cust_content, welcome_type = sql.get_welc_pref(chat.id)
        update.effective_message.reply_text(
            f"Este chat tiene su configuración de bienvenida establecida en: `{pref}`.\n"
            f"*El mensaje de bienvenida (no llenar el {{}}) es:*",
            parse_mode=ParseMode.MARKDOWN,
        )

        if welcome_type == sql.Types.BUTTON_TEXT or welcome_type == sql.Types.TEXT:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                update.effective_message.reply_text(welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                send(update, welcome_m, keyboard, sql.DEFAULT_WELCOME)
        else:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                ENUM_FUNC_MAP[welcome_type](chat.id, cust_content, caption=welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)
                ENUM_FUNC_MAP[welcome_type](
                    chat.id,
                    cust_content,
                    caption=welcome_m,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_welc_preference(str(chat.id), True)
            update.effective_message.reply_text(
                "¡Bueno! Saludaré a los miembros cuando se unan."
            )

        elif args[0].lower() in ("off", "no"):
            sql.set_welc_preference(str(chat.id), False)
            update.effective_message.reply_text(
                "Voy a holgazanear y no dar la bienvenida a nadie entonces."
            )

        else:
            update.effective_message.reply_text(
                "Sólo entiendo 'on/yes' o 'off/no' vale!"
            )


@run_async
@user_admin
def goodbye(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat

    if not args or args[0] == "noformat":
        noformat = True
        pref, goodbye_m, goodbye_type = sql.get_gdbye_pref(chat.id)
        update.effective_message.reply_text(
            f"Este chat tiene su configuración de despedida establecida en: `{pref}`.\n"
            f"*el mensaje de despedida (no llenar el {{}}) es:*",
            parse_mode=ParseMode.MARKDOWN,
        )

        if goodbye_type == sql.Types.BUTTON_TEXT:
            buttons = sql.get_gdbye_buttons(chat.id)
            if noformat:
                goodbye_m += revert_buttons(buttons)
                update.effective_message.reply_text(goodbye_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                send(update, goodbye_m, keyboard, sql.DEFAULT_GOODBYE)

        else:
            if noformat:
                ENUM_FUNC_MAP[goodbye_type](chat.id, goodbye_m)

            else:
                ENUM_FUNC_MAP[goodbye_type](
                    chat.id, goodbye_m, parse_mode=ParseMode.MARKDOWN
                )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_gdbye_preference(str(chat.id), True)
            update.effective_message.reply_text("Ok!")

        elif args[0].lower() in ("off", "no"):
            sql.set_gdbye_preference(str(chat.id), False)
            update.effective_message.reply_text("Ok!")

        else:
            # idek what you're writing, say yes or no
            update.effective_message.reply_text(
                "Sólo entiendo 'on/yes' o 'off/no' vale!"
            )


@run_async
@user_admin
@loggable
def set_welcome(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        msg.reply_text("No especificaste con qué responder con!")
        return ""

    sql.set_custom_welcome(chat.id, content, text, data_type, buttons)
    msg.reply_text("Establecer con éxito el mensaje de bienvenida personalizado!")

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#SET_WELCOME\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Establecer el mensaje de bienvenida."
    )


@run_async
@user_admin
@loggable
def reset_welcome(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_welcome(chat.id, None, sql.DEFAULT_WELCOME, sql.Types.TEXT)
    update.effective_message.reply_text(
        "Restablecer con éxito el mensaje de bienvenida a los valores predeterminados!"
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RESET_WELCOME\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Restablecer el mensaje de bienvenida a los valores predeterminados."
    )


@run_async
@user_admin
@loggable
def set_goodbye(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        msg.reply_text("No especificaste con qué responder que!")
        return ""

    sql.set_custom_gdbye(chat.id, content or text, data_type, buttons)
    msg.reply_text("Establecer con éxito un mensaje de despedida personalizado!")
    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#SET_GOODBYE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Establecer el mensaje de despedida."
    )


@run_async
@user_admin
@loggable
def reset_goodbye(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_gdbye(chat.id, sql.DEFAULT_GOODBYE, sql.Types.TEXT)
    update.effective_message.reply_text(
        "Restablecer con éxito el mensaje de despedida a la configuración predeterminada!"
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RESET_GOODBYE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"Restablecer el mensaje de despedida."
    )


@run_async
@user_admin
@loggable
def welcomemute(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if len(args) >= 1:
        if args[0].lower() in ("off", "no"):
            sql.set_welcome_mutes(chat.id, False)
            msg.reply_text("Ya no silenciaré a las personas al unirse!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>• Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Ha cambiado el silencio de bienvenida a <b>OFF</b>."
            )
        elif args[0].lower() in ["soft"]:
            sql.set_welcome_mutes(chat.id, "soft")
            msg.reply_text(
                "Restringiré el permiso de los usuarios para enviar medios durante 24 horas."
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>• Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Ha cambiado el silencio de bienvenida a <b>SOFT</b>."
            )
        elif args[0].lower() in ["strong"]:
            sql.set_welcome_mutes(chat.id, "strong")
            msg.reply_text(
                "Ahora silenciaré a las personas cuando se unan hasta que demuestren que no son un bot.\nTendrán 120 segundos antes de que los expulsen."
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>• Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"Ha cambiado el silencio de bienvenida a <b>STRONG</b>."
            )
        else:
            msg.reply_text(
                "Por favor escribe <code>off</code>/<code>no</code>/<code>soft</code>/<code>strong</code>!",
                parse_mode=ParseMode.HTML,
            )
            return ""
    else:
        curr_setting = sql.welcome_mutes(chat.id)
        reply = (
            f"\n Dame un ajuste!\nElige sólo uno de: <code>off</code>/<code>no</code> o <code>soft</code> o <code>strong</code> vale! \n"
            f"Configuración actual: <code>{curr_setting}</code>"
        )
        msg.reply_text(reply, parse_mode=ParseMode.HTML)
        return ""


@run_async
@user_admin
@loggable
def clean_welcome(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user

    if not args:
        clean_pref = sql.get_clean_pref(chat.id)
        if clean_pref:
            update.effective_message.reply_text(
                "Debería eliminar los mensajes de bienvenida de hasta dos días de antigüedad."
            )
        else:
            update.effective_message.reply_text(
                "Actualmente no estoy eliminando los mensajes de bienvenida antiguos.!"
            )
        return ""

    if args[0].lower() in ("on", "yes"):
        sql.set_clean_welcome(str(chat.id), True)
        update.effective_message.reply_text("Intentaré eliminar los mensajes de bienvenida antiguos!")
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#CLEAN_WELCOME\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"Ha activado las bienvenidas limpias a <code>ON</code>."
        )
    elif args[0].lower() in ("off", "no"):
        sql.set_clean_welcome(str(chat.id), False)
        update.effective_message.reply_text("No eliminaré los mensajes de bienvenida antiguos.")
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#CLEAN_WELCOME\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"Ha activado las bienvenidas limpias a <code>OFF</code>."
        )
    else:
        update.effective_message.reply_text("Sólo entiendo 'on/yes' o 'off/no' vale!")
        return ""


@run_async
@user_admin
def cleanservice(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat  # type: Optional[Chat]
    if chat.type != chat.PRIVATE:
        if len(args) >= 1:
            var = args[0]
            if var in ("no", "off"):
                sql.set_clean_service(chat.id, False)
                update.effective_message.reply_text("El servicio de limpieza de bienvenida es : off")
            elif var in ("yes", "on"):
                sql.set_clean_service(chat.id, True)
                update.effective_message.reply_text("El servicio de limpieza de bienvenida es : on")
            else:
                update.effective_message.reply_text(
                    "Invalid option", parse_mode=ParseMode.HTML
                )
        else:
            update.effective_message.reply_text(
                "El uso es <code>on</code>/<code>yes</code> o <code>off</code>/<code>no</code>",
                parse_mode=ParseMode.HTML,
            )
    else:
        curr = sql.clean_service(chat.id)
        if curr:
            update.effective_message.reply_text(
                "El servicio de limpieza de bienvenida es : <code>on</code>", parse_mode=ParseMode.HTML
            )
        else:
            update.effective_message.reply_text(
                "El servicio de limpieza de bienvenida es : <code>off</code>", parse_mode=ParseMode.HTML
            )


@run_async
def user_button(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    query = update.callback_query
    bot = context.bot
    match = re.match(r"user_join_\((.+?)\)", query.data)
    message = update.effective_message
    join_user = int(match.group(1))

    if join_user == user.id:
        sql.set_human_checks(user.id, chat.id)
        member_dict = VERIFIED_USER_WAITLIST.pop(user.id)
        member_dict["status"] = True
        VERIFIED_USER_WAITLIST.update({user.id: member_dict})
        query.answer(text="Yeet! Eres un humano, unmuted!")
        bot.restrict_chat_member(
            chat.id,
            user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        try:
            bot.deleteMessage(chat.id, message.message_id)
        except:
            pass
        if member_dict["should_welc"]:
            if member_dict["media_wel"]:
                sent = ENUM_FUNC_MAP[member_dict["welc_type"]](
                    member_dict["chat_id"],
                    member_dict["cust_content"],
                    caption=member_dict["res"],
                    reply_markup=member_dict["keyboard"],
                    parse_mode="markdown",
                )
            else:
                sent = send(
                    member_dict["update"],
                    member_dict["res"],
                    member_dict["keyboard"],
                    member_dict["backup_message"],
                )

            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

    else:
        query.answer(text="No tienes permitido hacer esto!")


WELC_HELP_TXT = (
    "Los mensajes de welcome/goodbye de su grupo se pueden personalizar de varias maneras. Si quieres los mensajes"
    " para generarse individualmente, como el mensaje de bienvenida predeterminado, puede usar *estas* variables:\n"
    " • `{first}`*:* esto representa el *first* primer nombre del usuario\n"
    " • `{last}`*:* esto representa el *last* name del usuario. Por defecto es *first name* si el usuario no tiene "
    "last name.\n"
    " • `{fullname}`*:* esto representa el nombre *full* name. Por defecto es *first name* si el usuario no tiene "
    "last name.\n"
    " • `{username}`*:* esto representa el *username* del usuario. Por defecto es *mention* del usuario "
    "first name if has no username.\n"
    " • `{mention}`*:* esto simplemente  *mentions* a un usuario - etiquetándolo con su nombre.\n"
    " • `{id}`*:* esto representa el usuario *id*\n"
    " • `{count}`*:* esto representa el *member number* del usuario.\n"
    " • `{chatname}`*:* esto representa el  *current chat name*.\n"
    "\nCada variable DEBE estar rodeada por`{}` para ser reemplazada.\n"
    "Los mensajes de bienvenida también son compatibles con Markdown, por lo que puede hacer que cualquier elemento bold/italic/code/links. "
    "Los botones también son compatibles, por lo que puede hacer que sus bienvenidas se vean increíbles con una buena introducción "
    "botones.\n"
    f"Para crear un botón que se vincule a sus reglas, utilice este: `[Rules](buttonurl://t.me/{dispatcher.bot.username}?start=group_id)`. "
    "Simplemente reemplace `group_id` con la identificación de su grupo, que se puede obtener a través de /id, y eres bueno para "
    "ir. Tenga en cuenta que los ID de grupo suelen estar precedidos por `-` signo; esto es obligatorio, así que por favor no "
    "lo quites.\n"
    "Incluso puede configurar  imagenes/gifs/videos/mensajes de voz como mensaje de bienvenida al "
    "respondiendo a los medios deseados, y llamando `/setwelcome`."
)

WELC_MUTE_HELP_TXT = (
    "Puede hacer que el bot silencie a las personas nuevas que se unen a su grupo y, por lo tanto, evita que los robots de spam inunden su grupo. "
    "Las siguientes opciones son posibles:\n"
    "• `/welcomemute soft`*:* restringe a los nuevos miembros el envío de medios durante 24 horas.\n"
    "• `/welcomemute strong`*:* silencia a los nuevos miembros hasta que toquen un botón, verificando así que son humanos.\n"
    "• `/welcomemute off`*:* desactiva el silencio de bienvenida.\n"
    
    "*Nota:* El mode strong expulsa a un usuario del chat si no verifica en 120 segundos. Aunque siempre pueden volver a unirse"
)


@run_async
@user_admin
def welcome_help(update: Update, context: CallbackContext):
    update.effective_message.reply_text(WELC_HELP_TXT, parse_mode=ParseMode.MARKDOWN)


@run_async
@user_admin
def welcome_mute_help(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        WELC_MUTE_HELP_TXT, parse_mode=ParseMode.MARKDOWN
    )


# TODO: get welcome data from group butler snap
# def __import_data__(chat_id, data):
#     welcome = data.get('info', {}).get('rules')
#     welcome = welcome.replace('$username', '{username}')
#     welcome = welcome.replace('$name', '{fullname}')
#     welcome = welcome.replace('$id', '{id}')
#     welcome = welcome.replace('$title', '{chatname}')
#     welcome = welcome.replace('$surname', '{lastname}')
#     welcome = welcome.replace('$rules', '{rules}')
#     sql.set_custom_welcome(chat_id, welcome, sql.Types.TEXT)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    welcome_pref = sql.get_welc_pref(chat_id)[0]
    goodbye_pref = sql.get_gdbye_pref(chat_id)[0]
    return (
        "Este chat tiene su preferencia de bienvenida establecida en `{}`.\n"
        "Su preferencia de despedida es `{}`.".format(welcome_pref, goodbye_pref)
    )


__help__ = """
*Sólo administradores:*

 ❍ /welcome <on/off>*:* enable/disable mensajes de bienvenida.
 ❍ /welcome*:* Muestra la configuración de bienvenida actual.
 ❍ /welcome noformat*:* Muestra la configuración de bienvenida actual, sin el formato - útil para reciclar sus mensajes de bienvenida!
 ❍ /goodbye*:* Mismo uso y argumentos que `/welcome`.
 ❍ /setwelcome <sometext>*:* Establecer un mensaje de bienvenida personalizado. Si se usa respondiendo a los medios, usa esos medios.
 ❍ /setgoodbye <sometext>*:* Establecer un mensaje de despedida personalizado. Si se usa respondiendo a los medios, usa esos medios.
 ❍ /resetwelcome*:* Restablecer el mensaje de bienvenida predeterminado.
 ❍ /resetgoodbye*:* Restablecer el mensaje de despedida predeterminado.
 ❍ /cleanwelcome <on/off>*:* En el nuevo miembro, intente eliminar el mensaje de bienvenida anterior para evitar el spam en el chat.
 ❍ /welcomemutehelp*:* Da información sobre silencios de bienvenida.
 ❍ /cleanservice <on/off*:* Borra mensajes de servicio de bienvenida/dejado de telegramas. 
 *Ejemplo:*
 el usuario se unió al chat, el usuario abandonó el chat.

 *Welcome markdown:* 

 ❍ /welcomehelp*:* Muestra más información de formato para mensajes personalizados de bienvenida/despedida.
"""

NEW_MEM_HANDLER = MessageHandler(Filters.status_update.new_chat_members, new_member)
LEFT_MEM_HANDLER = MessageHandler(Filters.status_update.left_chat_member, left_member)
WELC_PREF_HANDLER = CommandHandler("welcome", welcome, filters=Filters.group)
GOODBYE_PREF_HANDLER = CommandHandler("goodbye", goodbye, filters=Filters.group)
SET_WELCOME = CommandHandler("setwelcome", set_welcome, filters=Filters.group)
SET_GOODBYE = CommandHandler("setgoodbye", set_goodbye, filters=Filters.group)
RESET_WELCOME = CommandHandler("resetwelcome", reset_welcome, filters=Filters.group)
RESET_GOODBYE = CommandHandler("resetgoodbye", reset_goodbye, filters=Filters.group)
WELCOMEMUTE_HANDLER = CommandHandler("welcomemute", welcomemute, filters=Filters.group)
CLEAN_SERVICE_HANDLER = CommandHandler(
    "cleanservice", cleanservice, filters=Filters.group
)
CLEAN_WELCOME = CommandHandler("cleanwelcome", clean_welcome, filters=Filters.group)
WELCOME_HELP = CommandHandler("welcomehelp", welcome_help)
WELCOME_MUTE_HELP = CommandHandler("welcomemutehelp", welcome_mute_help)
BUTTON_VERIFY_HANDLER = CallbackQueryHandler(user_button, pattern=r"user_join_")

dispatcher.add_handler(NEW_MEM_HANDLER)
dispatcher.add_handler(LEFT_MEM_HANDLER)
dispatcher.add_handler(WELC_PREF_HANDLER)
dispatcher.add_handler(GOODBYE_PREF_HANDLER)
dispatcher.add_handler(SET_WELCOME)
dispatcher.add_handler(SET_GOODBYE)
dispatcher.add_handler(RESET_WELCOME)
dispatcher.add_handler(RESET_GOODBYE)
dispatcher.add_handler(CLEAN_WELCOME)
dispatcher.add_handler(WELCOME_HELP)
dispatcher.add_handler(WELCOMEMUTE_HANDLER)
dispatcher.add_handler(CLEAN_SERVICE_HANDLER)
dispatcher.add_handler(BUTTON_VERIFY_HANDLER)
dispatcher.add_handler(WELCOME_MUTE_HELP)

__mod_name__ = "Wᴇʟᴄᴏᴍᴇ"
__command_list__ = []
__handlers__ = [
    NEW_MEM_HANDLER,
    LEFT_MEM_HANDLER,
    WELC_PREF_HANDLER,
    GOODBYE_PREF_HANDLER,
    SET_WELCOME,
    SET_GOODBYE,
    RESET_WELCOME,
    RESET_GOODBYE,
    CLEAN_WELCOME,
    WELCOME_HELP,
    WELCOMEMUTE_HANDLER,
    CLEAN_SERVICE_HANDLER,
    BUTTON_VERIFY_HANDLER,
    WELCOME_MUTE_HELP,
]
