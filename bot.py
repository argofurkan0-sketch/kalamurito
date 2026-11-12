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
INTERVAL       = int(os.environ.get("INTERVAL_SECONDS", 60))

raw_groups = os.environ.get("GROUPS", "").strip()
GROUPS = [g.strip() for g in raw_groups.split(",") if g.strip()]

MESSAGES = [
    "🌟 Size özel sxrgu p4nel botu yapılır — fiyat için dm 📩",
    "⚡ Kendi sxrgu p4nelinizi kurmak ister misiniz? Fiyat için dm atın 📩",
    "🔥 Özel sxrgu p4nel botu kurulumu yapıyorum — detaylar için dm 📩",
    "💎 Sxrgu p4nel botu isteyenler dm atabilir, uygun fiyat garantisi — fiyat için dm 📩",
    "🚀 Sxrgu p4nel botu kurulumu hızlı ve güvenilir — fiyat için dm 📩",
    "✅ Size özel sxrgu p4nel botu kuruyorum — fiyat için dm 📩",
    "📊 Özel sxrgu p4neli kurmak isteyenler buraya — fiyat için dm 📩",
    "💡 Sxrgu p4nel botu kurulumu yapıyorum, ilgilenenler — fiyat için dm 📩",
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


# --- ID'yi doğru tipe çevir ---
def parse_target(group: str):
    g = group.strip()
    if g.lstrip("-").isdigit():
        return int(g)
    return g


# --- Mesaj gönderme ---
async def send_to_group(client: TelegramClient, entity, label: str, message: str):
    try:
        await client.send_message(entity, message)
        logger.info("✅ Gönderildi → %s", label)
    except FloodWaitError as e:
        logger.warning("⏳ FloodWait: %s için %ds bekleniyor.", label, e.seconds)
        await asyncio.sleep(e.seconds)
        try:
            await client.send_message(entity, message)
            logger.info("✅ Tekrar gönderildi → %s", label)
        except Exception as retry_err:
            logger.error("❌ Tekrar denemede hata [%s]: %s", label, retry_err)
    except Exception as e:
        logger.error("❌ Gönderilemedi [%s]: %s (%s)", label, e, type(e).__name__)


# --- Ana döngü ---
async def main():
    validate_env()

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

    logger.info("Oturum açıldı.")

    async with client:
        # Başlangıçta tüm grup entity'lerini çöz ve cache'e al
        # ID'li gruplar için bu adım şart
        resolved = []
        for g in GROUPS:
            try:
                target = parse_target(g)
                entity = await client.get_entity(target)
                resolved.append((entity, g))
                name = getattr(entity, "title", g)
                logger.info("✅ Grup çözümlendi: %s → %s", g, name)
            except Exception as e:
                logger.error("❌ Grup bulunamadı [%s]: %s (%s)", g, e, type(e).__name__)

        if not resolved:
            logger.error("Hiçbir grup çözümlenemedi, çıkılıyor.")
            sys.exit(1)

        logger.info("%d/%d grup hazır. Her %ds mesaj atılacak.", len(resolved), len(GROUPS), INTERVAL)

        turn = 0
        while True:
            message = MESSAGES[turn % len(MESSAGES)]
            logger.info("─── Tur %d | Mesaj #%d ───", turn + 1, (turn % len(MESSAGES)) + 1)
            await asyncio.gather(*[send_to_group(client, e, label, message) for e, label in resolved])
            logger.info("Tur bitti. %ds sonra tekrar.", INTERVAL)
            turn += 1
            await asyncio.sleep(INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
