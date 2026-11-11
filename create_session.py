"""
Bu scripti SADECE BİR KEZ local'de çalıştır.
Çıktıdaki SESSION_STRING değerini Railway'e yapıştır.

Çalıştırmak için:
  pip install telethon
  python create_session.py
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID   = input("API_ID: ").strip()
API_HASH = input("API_HASH: ").strip()
PHONE    = input("Telefon numarası (+905xxxxxxxxx): ").strip()


async def main():
    client = TelegramClient(StringSession(), int(API_ID), API_HASH)
    await client.start(phone=PHONE)

    session_string = client.session.save()
    print("\n" + "=" * 60)
    print("✅ SESSION_STRING (Railway'e kopyala):")
    print("=" * 60)
    print(session_string)
    print("=" * 60)
    print("\nBu değeri Railway Variables'a SESSION_STRING adıyla ekle.")

    await client.disconnect()


asyncio.run(main())
