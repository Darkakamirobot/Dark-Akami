import random
import re
from html import escape

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    DispatcherHandlerStop,
    Filters,
    MessageHandler,
    run_async,
)
from telegram.utils.helpers import escape_markdown, mention_html

from FallenRobot import DRAGONS, LOGGER, dispatcher
from FallenRobot.modules.connection import connected
from FallenRobot.modules.disable import DisableAbleCommandHandler
from FallenRobot.modules.helper_funcs.alternate import send_message, typing_action
from FallenRobot.modules.helper_funcs.chat_status import user_admin
from FallenRobot.modules.helper_funcs.extraction import extract_text
from FallenRobot.modules.helper_funcs.filters import CustomFilters
from FallenRobot.modules.helper_funcs.handlers import MessageHandlerChecker
from FallenRobot.modules.helper_funcs.misc import build_keyboard_parser
from FallenRobot.modules.helper_funcs.msg_types import get_filter_type
from FallenRobot.modules.helper_funcs.string_handling import (
    button_markdown_parser,
    escape_invalid_curly_brackets,
    markdown_to_html,
    split_quotes,
)
from FallenRobot.modules.sql import cust_filters_sql as sql

HANDLER_GROUP = 10

ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: dispatcher.bot.send_message,
    sql.Types.BUTTON_TEXT.value: dispatcher.bot.send_message,
    sql.Types.STICKER.value: dispatcher.bot.send_sticker,
    sql.Types.DOCUMENT.value: dispatcher.bot.send_document,
    sql.Types.PHOTO.value: dispatcher.bot.send_photo,
    sql.Types.AUDIO.value: dispatcher.bot.send_audio,
    sql.Types.VOICE.value: dispatcher.bot.send_voice,
    sql.Types.VIDEO.value: dispatcher.bot.send_video,
    # sql.Types.VIDEO_NOTE.value: dispatcher.bot.send_video_note
}


@run_async
@typing_action
def list_handlers(update, context):
    chat = update.effective_chat
    user = update.effective_user

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if not conn is False:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
        filter_list = "*Filters en {}:*\n"
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            chat_name = "filters locales"
            filter_list = "*filters locales:*\n"
        else:
            chat_name = chat.title
            filter_list = "*Filters en {}*:\n"

    all_handlers = sql.get_chat_triggers(chat_id)

    if not all_handlers:
        send_message(
            update.effective_message, "No hay filters guardados en {}!".format(chat_name)
        )
        return

    for keyword in all_handlers:
        entry = " • `{}`\n".format(escape_markdown(keyword))
        if len(entry) + len(filter_list) > telegram.MAX_MESSAGE_LENGTH:
            send_message(
                update.effective_message,
                filter_list.format(chat_name),
                parse_mode=telegram.ParseMode.MARKDOWN,
            )
            filter_list = entry
        else:
            filter_list += entry

    send_message(
        update.effective_message,
        filter_list.format(chat_name),
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


# NOT ASYNC BECAUSE DISPATCHER HANDLER RAISED
@user_admin
@typing_action
def filters(update, context):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    args = msg.text.split(
        None, 1
    )  # use python's maxsplit to separate Cmd, keyword, and reply_text

    conn = connected(context.bot, update, chat, user.id)
    if not conn is False:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            chat_name = "filters locales"
        else:
            chat_name = chat.title

    if not msg.reply_to_message and len(args) < 2:
        send_message(
            update.effective_message,
            "Proporcione la palabra clave para esta respuesta de filter con!",
        )
        return

    if msg.reply_to_message:
        if len(args) < 2:
            send_message(
                update.effective_message,
                "Proporcione la palabra clave para esta respuesta de filter con!",
            )
            return
        else:
            keyword = args[1]
    else:
        extracted = split_quotes(args[1])
        if len(extracted) < 1:
            return
        # set trigger -> lower, so as to avoid adding duplicate filters with different cases
        keyword = extracted[0].lower()

    # Add the filter
    # Note: perhaps handlers can be removed somehow using sql.get_chat_filters
    for handler in dispatcher.handlers.get(HANDLER_GROUP, []):
        if handler.filters == (keyword, chat_id):
            dispatcher.remove_handler(handler, HANDLER_GROUP)

    text, file_type, file_id = get_filter_type(msg)
    if not msg.reply_to_message and len(extracted) >= 2:
        offset = len(extracted[1]) - len(
            msg.text
        )  # set correct offset relative to command + notename
        text, buttons = button_markdown_parser(
            extracted[1], entities=msg.parse_entities(), offset=offset
        )
        text = text.strip()
        if not text:
            send_message(
                update.effective_message,
                "No hay mensaje de nota - no puede tener SOLO botones, necesita un mensaje que lo acompañe!",
            )
            return

    elif msg.reply_to_message and len(args) >= 2:
        if msg.reply_to_message.text:
            text_to_parsing = msg.reply_to_message.text
        elif msg.reply_to_message.caption:
            text_to_parsing = msg.reply_to_message.caption
        else:
            text_to_parsing = ""
        offset = len(
            text_to_parsing
        )  # set correct offset relative to command + notename
        text, buttons = button_markdown_parser(
            text_to_parsing, entities=msg.parse_entities(), offset=offset
        )
        text = text.strip()

    elif not text and not file_type:
        send_message(
            update.effective_message,
            "Proporcione la palabra clave para esta respuesta de filtro con!",
        )
        return

    elif msg.reply_to_message:
        if msg.reply_to_message.text:
            text_to_parsing = msg.reply_to_message.text
        elif msg.reply_to_message.caption:
            text_to_parsing = msg.reply_to_message.caption
        else:
            text_to_parsing = ""
        offset = len(
            text_to_parsing
        )  # set correct offset relative to command + notename
        text, buttons = button_markdown_parser(
            text_to_parsing, entities=msg.parse_entities(), offset=offset
        )
        text = text.strip()
        if (msg.reply_to_message.text or msg.reply_to_message.caption) and not text:
            send_message(
                update.effective_message,
                "No hay mensaje de nota - no puede tener SOLO botones, necesita un mensaje que lo acompañe!",
            )
            return

    else:
        send_message(update.effective_message, "Filter inválido!")
        return

    add = addnew_filter(update, chat_id, keyword, text, file_type, file_id, buttons)
    # This is an old method
    # sql.add_filter(chat_id, keyword, content, is_sticker, is_document, is_image, is_audio, is_voice, is_video, buttons)

    if add is True:
        send_message(
            update.effective_message,
            "Filter guardado '{}' en *{}*!".format(keyword, chat_name),
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
    raise DispatcherHandlerStop


# NOT ASYNC BECAUSE DISPATCHER HANDLER RAISED
@user_admin
@typing_action
def stop_filter(update, context):
    chat = update.effective_chat
    user = update.effective_user
    args = update.effective_message.text.split(None, 1)

    conn = connected(context.bot, update, chat, user.id)
    if not conn is False:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            chat_name = "Filters locales"
        else:
            chat_name = chat.title

    if len(args) < 2:
        send_message(update.effective_message, "¿Qué debo detener?")
        return

    chat_filters = sql.get_chat_triggers(chat_id)

    if not chat_filters:
        send_message(update.effective_message, "No hay filters activos aquí!")
        return

    for keyword in chat_filters:
        if keyword == args[1]:
            sql.remove_filter(chat_id, args[1])
            send_message(
                update.effective_message,
                "De acuerdo, dejaré de responder a ese filter en *{}*.".format(chat_name),
                parse_mode=telegram.ParseMode.MARKDOWN,
            )
            raise DispatcherHandlerStop

    send_message(
        update.effective_message,
        "Eso no es un filter - Haga clic en: /filters para obtener los filters actualmente activos.",
    )


@run_async
def reply_filter(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]

    if not update.effective_user or update.effective_user.id == 777000:
        return
    to_match = extract_text(message)
    if not to_match:
        return

    chat_filters = sql.get_chat_triggers(chat.id)
    for keyword in chat_filters:
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            if MessageHandlerChecker.check_user(update.effective_user.id):
                return
            filt = sql.get_filter(chat.id, keyword)
            if filt.reply == "Debe haber una nueva respuesta":
                buttons = sql.get_buttons(chat.id, filt.keyword)
                keyb = build_keyboard_parser(context.bot, chat.id, buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                VALID_WELCOME_FORMATTERS = [
                    "first",
                    "last",
                    "fullname",
                    "username",
                    "id",
                    "chatname",
                    "mention",
                ]
                if filt.reply_text:
                    if "%%%" in filt.reply_text:
                        split = filt.reply_text.split("%%%")
                        if all(split):
                            text = random.choice(split)
                        else:
                            text = filt.reply_text
                    else:
                        text = filt.reply_text
                    if text.startswith("~!") and text.endswith("!~"):
                        sticker_id = text.replace("~!", "").replace("!~", "")
                        try:
                            context.bot.send_sticker(
                                chat.id,
                                sticker_id,
                                reply_to_message_id=message.message_id,
                            )
                            return
                        except BadRequest as excp:
                            if (
                                excp.message
                                == "Se especificó un identificador de archivo remoto incorrecto: relleno incorrecto en la cadena"
                            ):
                                context.bot.send_message(
                                    chat.id,
                                    "No se pudo enviar el mensaje. ¿Es válida la identificación del sticker?",
                                )
                                return
                            else:
                                LOGGER.exception("Error en filters: " + excp.message)
                                return
                    valid_format = escape_invalid_curly_brackets(
                        text, VALID_WELCOME_FORMATTERS
                    )
                    if valid_format:
                        filtext = valid_format.format(
                            first=escape(message.from_user.first_name),
                            last=escape(
                                message.from_user.last_name
                                or message.from_user.first_name
                            ),
                            fullname=" ".join(
                                [
                                    escape(message.from_user.first_name),
                                    escape(message.from_user.last_name),
                                ]
                                if message.from_user.last_name
                                else [escape(message.from_user.first_name)]
                            ),
                            username="@" + escape(message.from_user.username)
                            if message.from_user.username
                            else mention_html(
                                message.from_user.id, message.from_user.first_name
                            ),
                            mention=mention_html(
                                message.from_user.id, message.from_user.first_name
                            ),
                            chatname=escape(message.chat.title)
                            if message.chat.type != "private"
                            else escape(message.from_user.first_name),
                            id=message.from_user.id,
                        )
                    else:
                        filtext = ""
                else:
                    filtext = ""

                if filt.file_type in (sql.Types.BUTTON_TEXT, sql.Types.TEXT):
                    try:
                        context.bot.send_message(
                            chat.id,
                            markdown_to_html(filtext),
                            reply_to_message_id=message.message_id,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_markup=keyboard,
                        )
                    except BadRequest as excp:
                        error_catch = get_exception(excp, filt, chat)
                        if error_catch == "Ninguna respuesta":
                            try:
                                context.bot.send_message(
                                    chat.id,
                                    markdown_to_html(filtext),
                                    parse_mode=ParseMode.HTML,
                                    disable_web_page_preview=True,
                                    reply_markup=keyboard,
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Error en filters: " + excp.message)
                                send_message(
                                    update.effective_message,
                                    get_exception(excp, filt, chat),
                                )
                        else:
                            try:
                                send_message(
                                    update.effective_message,
                                    get_exception(excp, filt, chat),
                                )
                            except BadRequest as excp:
                                LOGGER.exception(
                                    "No se pudo enviar el mensaje: " + excp.message
                                )
                else:
                    try:
                        ENUM_FUNC_MAP[filt.file_type](
                            chat.id,
                            filt.file_id,
                            caption=markdown_to_html(filtext),
                            reply_to_message_id=message.message_id,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_markup=keyboard,
                        )
                    except BadRequest:
                        send_message(
                            message,
                            "No tengo permiso para enviar el contenido del filter.",
                        )
                break
            else:
                if filt.is_sticker:
                    message.reply_sticker(filt.reply)
                elif filt.is_document:
                    message.reply_document(filt.reply)
                elif filt.is_image:
                    message.reply_photo(filt.reply)
                elif filt.is_audio:
                    message.reply_audio(filt.reply)
                elif filt.is_voice:
                    message.reply_voice(filt.reply)
                elif filt.is_video:
                    message.reply_video(filt.reply)
                elif filt.has_markdown:
                    buttons = sql.get_buttons(chat.id, filt.keyword)
                    keyb = build_keyboard_parser(context.bot, chat.id, buttons)
                    keyboard = InlineKeyboardMarkup(keyb)

                    try:
                        send_message(
                            update.effective_message,
                            filt.reply,
                            parse_mode=ParseMode.MARKDOWN,
                            disable_web_page_preview=True,
                            reply_markup=keyboard,
                        )
                    except BadRequest as excp:
                        if excp.message == "Protocolo de URL no admitido":
                            try:
                                send_message(
                                    update.effective_message,
                                    "Parece que está intentando utilizar un protocolo de URL no admitido. "
                                    "Telegram no admite botones para algunos protocolos, como tg://. Por favor, inténtalo "
                                    "De nuevo...",
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Error en filters: " + excp.message)
                        elif excp.message == "Mensaje de respuesta no encontrado":
                            try:
                                context.bot.send_message(
                                    chat.id,
                                    filt.reply,
                                    parse_mode=ParseMode.MARKDOWN,
                                    disable_web_page_preview=True,
                                    reply_markup=keyboard,
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Error en filters: " + excp.message)
                        else:
                            try:
                                send_message(
                                    update.effective_message,
                                    "Este mensaje no se pudo enviar porque tiene un formato incorrecto.",
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Error en filters: " + excp.message)
                            LOGGER.warning(
                                "El mensaje %s no se pudo analizar", str(filt.reply)
                            )
                            LOGGER.exception(
                                "No se pudo analizar el filtro %s en el chat %s",
                                str(filt.keyword),
                                str(chat.id),
                            )

                else:
                    # LEGACY - all new filters will have has_markdown set to True.
                    try:
                        send_message(update.effective_message, filt.reply)
                    except BadRequest as excp:
                        LOGGER.exception("Error en filters: " + excp.message)
                break


@run_async
def rmall_filters(update, context):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in DRAGONS:
        update.effective_message.reply_text(
            "Solo el propietario del chat puede borrar todas las notas a la vez."
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Detener todos los filters", callback_data="filters_rmall"
                    )
                ],
                [InlineKeyboardButton(text="Cancelar", callback_data="filters_cancel")],
            ]
        )
        update.effective_message.reply_text(
            f"¿Está seguro de que desea detener TODOS los filters en {chat.title}? Esta acción no se puede deshacer.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


@run_async
def rmall_callback(update, context):
    query = update.callback_query
    chat = update.effective_chat
    msg = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "filters_rmall":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            allfilters = sql.get_chat_triggers(chat.id)
            if not allfilters:
                msg.edit_text("No hay filters en este chat, nada que se detenga!")
                return

            count = 0
            filterlist = []
            for x in allfilters:
                count += 1
                filterlist.append(x)

            for i in filterlist:
                sql.remove_filter(chat.id, i)

            msg.edit_text(f"Limpiado {count} filters en {chat.title}")

        if member.status == "administrator":
            query.answer("Solo el dueño del chat puede hacer esto.")

        if member.status == "member":
            query.answer("Necesitas ser administrador para hacer esto.")
    elif query.data == "filters_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            msg.edit_text("Se ha cancelado la limpieza de todos los filters.")
            return
        if member.status == "administrator":
            query.answer("Solo el dueño del chat puede hacer esto.")
        if member.status == "member":
            query.answer("Necesitas ser administrador para hacer esto.")


# NOT ASYNC NOT A HANDLER
def get_exception(excp, filt, chat):
    if excp.message == "Protocolo de URL no admitido":
        return "Parece que está intentando utilizar el protocolo de URL que no es compatible. Telegram no admite claves para múltiples protocolos, como tg: //. Inténtalo de nuevo!"
    elif excp.message == "Mensaje de respuesta no encontrado":
        return "noreply"
    else:
        LOGGER.warning("El mensaje %s no se pudo analizar", str(filt.reply))
        LOGGER.exception(
            "No se pudo analizar el filtro %s en chat %s", str(filt.keyword), str(chat.id)
        )
        return "Estos datos no se pudieron enviar porque tienen un formato incorrecto."


# NOT ASYNC NOT A HANDLER
def addnew_filter(update, chat_id, keyword, text, file_type, file_id, buttons):
    msg = update.effective_message
    totalfilt = sql.get_chat_triggers(chat_id)
    if len(totalfilt) >= 150:  # Idk why i made this like function....
        msg.reply_text("Este grupo ha alcanzado su límite máximo de filters de 150.")
        return False
    else:
        sql.new_add_filter(chat_id, keyword, text, file_type, file_id, buttons)
        return True


def __stats__():
    return "• {} filters, across {} chats.".format(sql.num_filters(), sql.num_chats())


def __import_data__(chat_id, data):
    # set chat filters
    filters = data.get("filters", {})
    for trigger in filters:
        sql.add_to_blacklist(chat_id, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    cust_filters = sql.get_chat_triggers(chat_id)
    return "Hay `{}` filters personalizados aquí.".format(len(cust_filters))


__help__ = """
 ❍ /filters*:* Lista de todos los filters activos guardados en el chat.

*Sólo administradores:*
 ❍ /filter <palabra> <mensaje de respuesta>*:* Agrega un filter a este chat. El bot ahora responderá ese mensaje cada vez que 'palabra'\
 es mencionada. Si responde a un sticker con una palabra clave, el bot responderá con ese sticker. NOTA: Para todo filter \
 las palabras clave están en minúsculas. Si desea que su palabra clave sea una oración, use comillas. ej: /filter "hola" ¿Cómo \
 estás?
 Separe las diferentes respuestas por `%%%` para obtener respuestas aleatorias.
 
*Ejemplo:* 
 `/filter "nombre del filter"
 Reply 1
 %%%
 Reply 2
 %%%
 Reply 3`
 
 ❍ /stop <filter palabra>*:* Detiene ese filter.

*Sólo para el creador de chat:*
 ❍ /removeallfilters*:* Elimina todos los filters de chat a la vez.

*Note*: Los filtros también admiten formateadores de rebajas como: {first}, {last} etc.. y botones.
 Revisa ❍ /markdownhelp para saber más!

"""

__mod_name__ = "Fɪʟᴛᴇʀs"

FILTER_HANDLER = CommandHandler("filter", filters)
STOP_HANDLER = CommandHandler("stop", stop_filter)
RMALLFILTER_HANDLER = CommandHandler(
    "removeallfilters", rmall_filters, filters=Filters.group
)
RMALLFILTER_CALLBACK = CallbackQueryHandler(rmall_callback, pattern=r"filters_.*")
LIST_HANDLER = DisableAbleCommandHandler("filters", list_handlers, admin_ok=True)
CUST_FILTER_HANDLER = MessageHandler(
    CustomFilters.has_text & ~Filters.update.edited_message, reply_filter
)

dispatcher.add_handler(FILTER_HANDLER)
dispatcher.add_handler(STOP_HANDLER)
dispatcher.add_handler(LIST_HANDLER)
dispatcher.add_handler(CUST_FILTER_HANDLER, HANDLER_GROUP)
dispatcher.add_handler(RMALLFILTER_HANDLER)
dispatcher.add_handler(RMALLFILTER_CALLBACK)

__handlers__ = [
    FILTER_HANDLER,
    STOP_HANDLER,
    LIST_HANDLER,
    (CUST_FILTER_HANDLER, HANDLER_GROUP, RMALLFILTER_HANDLER),
]
