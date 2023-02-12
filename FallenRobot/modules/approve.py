import html

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CallbackQueryHandler, run_async
from telegram.utils.helpers import mention_html

import FallenRobot.modules.sql.approve_sql as sql
from FallenRobot import DRAGONS, dispatcher
from FallenRobot.modules.disable import DisableAbleCommandHandler
from FallenRobot.modules.helper_funcs.chat_status import user_admin
from FallenRobot.modules.helper_funcs.extraction import extract_user
from FallenRobot.modules.log_channel import loggable


@loggable
@user_admin
@run_async
def approve(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "No se de quien hablas, vas a necesitar especificar un usuario!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrador" or member.status == "creador":
        message.reply_text(
            "El usuario ya es administrador: los bloqueos - las listas de bloqueo y la protección contra inundaciones ya no se aplican a ellos."
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"[{member.user['first_name']}](tg://user?id={member.user['id']}) ya está aprobado en {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.approve(message.chat_id, user_id)
    message.reply_text(
        f"[{member.user['first_name']}](tg://user?id={member.user['id']}) ha sido aprobado en {chat_title}! Ahora serán ignorados por acciones de administración automatizadas como bloqueos, listas de bloqueo y protección contra inundaciones..",
        parse_mode=ParseMode.MARKDOWN,
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#APPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@loggable
@user_admin
@run_async
def disapprove(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "No se de quien hablas, vas a necesitar especificar un usuario!"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrador" or member.status == "creador":
        message.reply_text("Este usuario es un administrador, no puede ser desaprobado.")
        return ""
    if not sql.is_approved(message.chat_id, user_id):
        message.reply_text(f"{member.user['first_name']} aún no está aprobado!")
        return ""
    sql.disapprove(message.chat_id, user_id)
    message.reply_text(
        f"{member.user['first_name']} Ya no está aprobado en {chat_title}."
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNAPPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@user_admin
@run_async
def approved(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "Los siguientes usuarios están aprobados.\n"
    approved_users = sql.list_approved(message.chat_id)
    for i in approved_users:
        member = chat.get_member(int(i.user_id))
        msg += f"- `{i.user_id}`: {member.user['first_name']}\n"
    if msg.endswith("approved.\n"):
        message.reply_text(f"No hay usuarios aprobados en {chat_title}.")
        return ""
    else:
        message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


@user_admin
@run_async
def approval(update, context):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    member = chat.get_member(int(user_id))
    if not user_id:
        message.reply_text(
            "No se de quien hablas, vas a necesitar especificar un usuario!"
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"{member.user['first_name']} es un usuario aprobado. No se les aplicarán bloqueos, protección contra inundaciones, ni listas de bloqueo."
        )
    else:
        message.reply_text(
            f"{member.user['first_name']} no es un usuario aprobado. Se verá afectado por los comandos normales."
        )


@run_async
def unapproveall(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in DRAGONS:
        update.effective_message.reply_text(
            "Solo el propietario del chat puede aprobar a todos los usuarios a la vez."
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Unapprove all users", callback_data="unapproveall_user"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Cancel", callback_data="unapproveall_cancel"
                    )
                ],
            ]
        )
        update.effective_message.reply_text(
            f"¿Está seguro de que desea desaprobar a TODOS los usuarios en {chat.title}? Esta acción no se puede deshacer.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


@run_async
def unapproveall_btn(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "unapproveall_user":
        if member.status == "creador" or query.from_user.id in DRAGONS:
            approved_users = sql.list_approved(chat.id)
            users = [int(i.user_id) for i in approved_users]
            for user_id in users:
                sql.disapprove(chat.id, user_id)

        if member.status == "administrador":
            query.answer("Sólo el dueño del chat puede hacer esto.")

        if member.status == "miembro":
            query.answer("Necesitas ser administrador para hacer esto.")
    elif query.data == "unapproveall_cancel":
        if member.status == "creador" or query.from_user.id in DRAGONS:
            message.edit_text("La eliminación de todos los usuarios aprobados ha sido cancelada.")
            return ""
        if member.status == "administrador":
            query.answer("Sólo el dueño del chat puede hacer esto..")
        if member.status == "member":
            query.answer("Necesitas ser administrador para hacer esto.")


__help__ = """
A veces, puede confiar en que un usuario no envíe contenido no deseado.
Tal vez no sea suficiente para convertirlos en administradores, pero es posible que esté de acuerdo con que los bloqueos, las listas negras y la protección contra inundaciones no se apliquen a ellos.

Para eso están las aprobaciones - aprueba a usuarios confiables para permitirles enviar. 

*Comandos para administradores:*
❍ /approval*:* Consulta el estado de aprobación de un usuario en este chat.
❍ /approve*:* Aprueba a un usuario. Los bloqueos, las listas negras y la protección contra inundaciones ya no se aplicarán a ellos.
❍ /unapprove*:* Desaprueba a un usuario. Ahora estarán sujetos a bloqueos, listas negras y antiinundaciones nuevamente.
❍ /approved*:* Lista de todos los usuarios aprobados.
❍ /unapproveall*:* Desaprueba *TODOS* los usuarios en un chat. Esto no se puede deshacer.
"""

APPROVE = DisableAbleCommandHandler("approve", approve)
DISAPPROVE = DisableAbleCommandHandler("unapprove", disapprove)
APPROVED = DisableAbleCommandHandler("approved", approved)
APPROVAL = DisableAbleCommandHandler("approval", approval)
UNAPPROVEALL = DisableAbleCommandHandler("unapproveall", unapproveall)
UNAPPROVEALL_BTN = CallbackQueryHandler(unapproveall_btn, pattern=r"unapproveall_.*")

dispatcher.add_handler(APPROVE)
dispatcher.add_handler(DISAPPROVE)
dispatcher.add_handler(APPROVED)
dispatcher.add_handler(APPROVAL)
dispatcher.add_handler(UNAPPROVEALL)
dispatcher.add_handler(UNAPPROVEALL_BTN)

__mod_name__ = "Aᴘᴘʀᴏᴠᴇ"
__command_list__ = ["approve", "unapprove", "approved", "approval"]
__handlers__ = [APPROVE, DISAPPROVE, APPROVED, APPROVAL]
