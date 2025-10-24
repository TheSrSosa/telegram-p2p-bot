import os
import re
import signal
import asyncio
from telethon import TelegramClient, events
from dotenv import load_dotenv
from flask import Flask

# ---------------------- #
# 🔹 Cargar variables del entorno (.env)
# ---------------------- #
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
CHANNEL_ORIGEN = os.getenv("CHANNEL_ORIGEN")
CHANNEL_DESTINO = os.getenv("CHANNEL_DESTINO")

# ---------------------- #
# 🔹 Inicializar Telethon
# ---------------------- #
client = TelegramClient("userbot_session", API_ID, API_HASH)

pattern_ratio = re.compile(r"Ratio:\s*\$(\d+(?:\.\d+)?)\s*x\s*USD", re.IGNORECASE)

# ---------------------- #
# 🔹 Mensaje al iniciar
# ---------------------- #
async def start_bot():
    await client.send_message(CHANNEL_DESTINO, "Cazando ofertas 🕵️‍♂️")
    print("✅ UserBot corriendo...")

# ---------------------- #
# 🔹 Mensaje al detener
# ---------------------- #
def handle_exit(signum, frame):
    print("Bot detenido, enviando mensaje de cierre...")
    asyncio.get_event_loop().create_task(
        client.send_message(CHANNEL_DESTINO, "Descansando 😴")
    )
    raise SystemExit

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# ---------------------- #
# 🔹 Filtrar ofertas #Compra #USDT (BSC)
# ---------------------- #
@client.on(events.NewMessage(chats=CHANNEL_ORIGEN))
async def ofertas_usdt(event):
    texto = event.message.message or ""
    if "#Compra" in texto and "#USDT (BSC)" in texto and "Ratio: $1.00 x USD" in texto:
        await client.send_message(CHANNEL_DESTINO, texto)

# ---------------------- #
# 🔹 Comando "cup"
# ---------------------- #
@client.on(events.NewMessage(chats=CHANNEL_DESTINO))
async def comandos(event):
    texto = event.message.message.lower().strip()

    if texto == "cup":
        await client.send_message(CHANNEL_DESTINO, "Analizando últimas 30 ofertas CUP... 💸")
        mensajes = await client.get_messages(CHANNEL_ORIGEN, limit=100)
        ratios = []

        for msg in mensajes:
            texto_msg = msg.message or ""
            if "#Venta" in texto_msg and "#CUP" in texto_msg:
                match = pattern_ratio.search(texto_msg)
                if match:
                    valor = float(match.group(1))
                    ratios.append(valor)
                    if len(ratios) >= 30:
                        break

        if ratios:
            promedio = sum(ratios) / len(ratios)
            await client.send_message(CHANNEL_DESTINO, f"El promedio de venta en CUP es: ${promedio:.2f} x USD 💰")
        else:
            await client.send_message(CHANNEL_DESTINO, "No encontré suficientes ofertas #Venta en #CUP 😕")

    elif texto == "mlc":
        await client.send_message(CHANNEL_DESTINO, "Analizando últimas 30 ofertas MLC... 💰")
        mensajes = await client.get_messages(CHANNEL_ORIGEN, limit=100)
        ratios = []

        for msg in mensajes:
            texto_msg = msg.message or ""
            if "#Venta" in texto_msg and "#MLC" in texto_msg:
                match = pattern_ratio.search(texto_msg)
                if match:
                    valor = float(match.group(1))
                    ratios.append(valor)
                    if len(ratios) >= 30:
                        break

        if ratios:
            promedio = sum(ratios) / len(ratios)
            await client.send_message(CHANNEL_DESTINO, f"El promedio de venta en MLC es: ${promedio:.2f} x USD 💵")
        else:
            await client.send_message(CHANNEL_DESTINO, "No encontré suficientes ofertas #Venta en #MLC 😕")

# ---------------------- #
# 🔹 Flask para mantener activo el bot
# ---------------------- #
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 El UserBot está corriendo correctamente 24/7."

def keep_alive():
    app.run(host="0.0.0.0", port=8080)

# ---------------------- #
# 🔹 Iniciar todo
# ---------------------- #
if __name__ == "__main__":
    import threading
    threading.Thread(target=keep_alive).start()

    with client:
        client.loop.run_until_complete(start_bot())
        client.run_until_disconnected()
