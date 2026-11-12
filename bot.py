import os
import asyncio
import logging
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Ortam değişkenleri ---
API_ID         = int(os.environ["API_ID"])
API_HASH       = os.environ["API_HASH"]
SESSION_STRING = os.environ.get("SESSION_STRING", "").strip()
PHONE          = os.environ.get("PHONE", "").strip()
INTERVAL       = int(os.environ.get("INTERVAL_SECONDS", 300))

raw_groups = os.environ.get("GROUPS", "").strip()
GROUPS = [g.strip() for g in raw_groups.split(",") if g.strip()]

MESSAGES = [
    "🌟 Size özel sorgu panel botu yapılır — fiyat için dm 📩",
    "⚡ Kendi sorgu panelinizi kurmak ister misiniz? Fiyat için dm atın 📩",
    "🔥 Özel panel botu kurulumu yapıyorum — detaylar için dm 📩",
    "💎 Sorgu panel botu isteyenler dm atabilir, uygun fiyat garantisi — fiyat için dm 📩",
    "🚀 Panel botu kurulumu hızlı ve güvenilir — fiyat için dm 📩",
    "✅ Size özel sxrgu p4nel botu yapılır — fiyat için dm 📩",
    "📊 Özel sorgu paneli kurmak isteyenler buraya — fiyat için dm 📩",
    "💡 Panel botu kurulumu yapıyorum, ilgilenenler — fiyat için dm 📩",
]


# --- Başlangıç kontrolleri ---
def validate_env():
    errors = []
    if not SESSION_STRING and not PHONE:
        errors.append("SESSION_STRING veya PHONE tanımlı olmalı.")
    if not GROUPS:
        errors.append("GROUPS boş. Örnek: GROUPS=@grup1,-1001234567890")
    if errors:
        for err in errors:
            logger.error("❌ %s", err)
        sys.exit(1)


# --- Mesaj gönderme ---
async def send_to_group(client: TelegramClient, group: str, message: str):
    try:
        await client.send_message(group, message)
        logger.info("✅ Gönderildi → %s", group)
    except FloodWaitError as e:
        logger.warning("⏳ FloodWait: %s için %ds bekleniyor.", group, e.seconds)
        await asyncio.sleep(e.seconds)
        try:
            await client.send_message(group, message)
            logger.info("✅ Tekrar gönderildi → %s", group)
        except Exception as retry_err:
            logger.error("❌ Tekrar denemede hata [%s]: %s", group, retry_err)
    except Exception as e:
        logger.error("❌ Gönderilemedi [%s]: %s", group, e)


# --- Bağlantı kurma (yeniden deneme destekli) ---
async def create_client():
    # Railway WebSocket sorununu önlemek için TCP bağlantısı kullan
    kwargs = dict(
        connection=ConnectionTcpAbridged,
        connection_retries=10,
        retry_delay=5,
        auto_reconnect=True,
    )
    if SESSION_STRING:
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, **kwargs)
        await client.start()
    else:
        client = TelegramClient("session", API_ID, API_HASH, **kwargs)
        await client.start(phone=PHONE)
    return client


# --- Ana döngü ---
async def main():
    validate_env()

    logger.info("Bağlanıyor...")
    client = await create_client()
    logger.info("Oturum açıldı. Gruplar: %s", GROUPS)
    logger.info("Mesaj aralığı: %ds | Varyasyon: %d mesaj", INTERVAL, len(MESSAGES))

    turn = 0
    async with client:
        while True:
            message = MESSAGES[turn % len(MESSAGES)]
            logger.info("─── Tur %d | Mesaj #%d ───", turn + 1, (turn % len(MESSAGES)) + 1)
            await asyncio.gather(*[send_to_group(client, g, message) for g in GROUPS])
            logger.info("Tur bitti. %ds sonra tekrar.", INTERVAL)
            turn += 1
            await asyncio.sleep(INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
