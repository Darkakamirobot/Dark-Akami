import flag
from countryinfo import CountryInfo

from FallenRobot import BOT_NAME, telethn
from FallenRobot.events import register


@register(pattern="^/country (.*)")
async def msg(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    lol = input_str
    country = CountryInfo(lol)
    try:
        a = country.info()
    except:
        await event.reply("País No disponible actualmente")
    name = a.get("name")
    bb = a.get("altSpellings")
    hu = ""
    for p in bb:
        hu += p + ",  "

    area = a.get("area")
    borders = ""
    hell = a.get("borders")
    for fk in hell:
        borders += fk + ",  "

    call = ""
    WhAt = a.get("callingCodes")
    for what in WhAt:
        call += what + "  "

    capital = a.get("capital")
    currencies = ""
    fker = a.get("currencies")
    for FKer in fker:
        currencies += FKer + ",  "

    HmM = a.get("demonym")
    geo = a.get("geoJSON")
    pablo = geo.get("features")
    Pablo = pablo[0]
    PAblo = Pablo.get("geometry")
    EsCoBaR = PAblo.get("type")
    iso = ""
    iSo = a.get("ISO")
    for hitler in iSo:
        po = iSo.get(hitler)
        iso += po + ",  "
    fla = iSo.get("alpha2")
    nox = fla.upper()
    okie = flag.flag(nox)

    languages = a.get("languages")
    lMAO = ""
    for lmao in languages:
        lMAO += lmao + ",  "

    nonive = a.get("nativeName")
    waste = a.get("population")
    reg = a.get("region")
    sub = a.get("subregion")
    tik = a.get("timezones")
    tom = ""
    for jerry in tik:
        tom += jerry + ",   "

    GOT = a.get("tld")
    lanester = ""
    for targaryen in GOT:
        lanester += targaryen + ",   "

    wiki = a.get("wiki")

    caption = f"""<b><u>Información recopilada con éxito</b></u>

<b>Nombre del país :</b> {name}
<b>Nombres alternativos :</b> {hu}
<b>Área del país :</b> {area} square kilometers
<b>Fronteras :</b> {borders}
<b>Códigos de llamadas :</b> {call}
<b>Capital del país :</b> {capital}
<b>Moneda del pais :</b> {currencies}
<b>Bandera del país :</b> {okie}
<b>Gentilicio :</b> {HmM}
<b>Tipo de país :</b> {EsCoBaR}
<b>Nombres ISO :</b> {iso}
<b>Idiomas :</b> {lMAO}
<b>Nombre nativo :</b> {nonive}
<b>Población :</b> {waste}
<b>Región :</b> {reg}
<b>Sub Región :</b> {sub}
<b>Zonas horarias :</b> {tom}
<b>Dominio de nivel superior :</b> {lanester}
<b>Wikipedia :</b> {wiki}

<u>Información recopilada por {BOT_NAME}</u>
"""

    await telethn.send_message(
        event.chat_id,
        caption,
        parse_mode="HTML",
        link_preview=None,
    )


__help__ = """
Daré información sobre un país.

 ❍ /country <nombre del país>*:* Recopilación de información sobre un país dado.
"""

__mod_name__ = "Cᴏᴜɴᴛʀʏ"
