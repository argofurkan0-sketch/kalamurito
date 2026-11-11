import os
import asyncio
import logging
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

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

# GROUPS: virgülle ayrılmış grup listesi
# Örnek: GROUPS=@grup1,@grup2,-1001234567890
raw_groups = os.environ.get("GROUPS", "").strip()
GROUPS = [g.strip() for g in raw_groups.split(",") if g.strip()]

MESSAGE = "🌟 Size özel sxrgu p4nel botu yapılır — fiyat için dm 📩"


# --- Başlangıç kontrolleri ---
def validate_env():
    errors = []

    if not SESSION_STRING and not PHONE:
        errors.append(
            "SESSION_STRING veya PHONE tanımlı olmalı. "
            "create_session.py ile SESSION_STRING oluştur."
        )
    if not GROUPS:
        errors.append(
            "GROUPS boş. Örnek: GROUPS=@grup1,@grup2,-1001234567890"
        )

    if errors:
        for err in errors:
            logger.error("❌ %s", err)
        sys.exit(1)


# --- Mesaj gönderme ---
async def send_to_group(client: TelegramClient, group: str):
    """Tek bir gruba mesaj gönderir. FloodWait gelirse bekler, bir kez daha dener."""
    try:
        await client.send_message(group, MESSAGE)
        logger.info("✅ Gönderildi → %s", group)
    except FloodWaitError as e:
        logger.warning("⏳ FloodWait: %s için %ds bekleniyor.", group, e.seconds)
        await asyncio.sleep(e.seconds)
        try:
            await client.send_message(group, MESSAGE)
            logger.info("✅ Tekrar gönderildi → %s", group)
        except Exception as retry_err:
            logger.error("❌ Tekrar denemede hata [%s]: %s", group, retry_err)
    except Exception as e:
        logger.error("❌ Gönderilemedi [%s]: %s", group, e)


# --- Ana döngü ---
async def main():
    validate_env()

    if SESSION_STRING:
        client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
        await client.start()
        logger.info("StringSession ile oturum açıldı.")
    else:
        client = TelegramClient("session", API_ID, API_HASH)
        await client.start(phone=PHONE)
        logger.info("Dosya session ile oturum açıldı.")

    logger.info("Grup sayısı: %d → %s", len(GROUPS), GROUPS)
    logger.info("Mesaj aralığı: %ds", INTERVAL)

    async with client:
        while True:
            logger.info("─── Tur başlıyor ───")
            await asyncio.gather(*[send_to_group(client, g) for g in GROUPS])
            logger.info("Tur bitti. %ds sonra tekrar.", INTERVAL)
            await asyncio.sleep(INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
