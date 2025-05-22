from telethon import TelegramClient, events
import asyncio
import re
import datetime

class KrakenHunter:
    def __init__(self, session_name, api_id, api_hash, kraken_message_id):
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.bot_username = 'JangUzBot'
        self.kraken_message_id = kraken_message_id
        self.is_running = False
        self.stop_event = asyncio.Event()
        self.session_name = session_name
        self.last_action_time = None
        self.hunting_task = None
        
        # Event handler ni to'g'ri registratsiya qilish
        self.client.add_event_handler(self.handle_messages, events.NewMessage)

    async def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{self.session_name}] {message}")

    async def check_resources(self, max_retries=3):
        """Sopol va olmos miqdorini navbat bilan tekshirish"""
        try:
            await self.log("🔍 Resurslarni tekshirish boshlandi...")

            sopol_count = 0
            olmos_count = 0

            # 1. Sopolni tekshirish - sahro
            await self.client.send_message(self.bot_username, "/sahro")
            await asyncio.sleep(2)

            sahro_msg = await self.client.get_messages(self.bot_username, limit=1)
            if sahro_msg and sahro_msg[0].text:
                sahro_text = sahro_msg[0].text
                await self.log(f"📩 Sahro xabari:\n{sahro_text}")

                # Sopolni topish
                sopol_match = re.search(r'🪔Sopol.*?(\d+)', sahro_text)
                if sopol_match:
                    sopol_count = int(sopol_match.group(1))
                    await self.log(f"📊 Sopol: {sopol_count}")
            else:
                await self.log("⚠️ Sahro javobi topilmadi.")

            # 2. Olmosni tekshirish - yuklar
            await self.client.send_message(self.bot_username, "/yuklar")
            await asyncio.sleep(2)

            yuklar_msg = await self.client.get_messages(self.bot_username, limit=1)
            if yuklar_msg and yuklar_msg[0].text:
                yuklar_text = yuklar_msg[0].text
                await self.log(f"📩 Yuklar xabari:\n{yuklar_text}")

                # Olmosni topish
                olmos_match = re.search(r'💎Olmos.*?(\d+)', yuklar_text)
                if olmos_match:
                    olmos_count = int(olmos_match.group(1))
                    await self.log(f"💎 Olmos: {olmos_count}")
            else:
                await self.log("⚠️ Yuklar javobi topilmadi.")

            await self.log(f"📈 Jami resurslar: Sopol={sopol_count}, Olmos={olmos_count}")

            return olmos_count >= 1 or sopol_count >= 2

        except Exception as e:
            await self.log(f"❌ Resurslarni tekshirishda xato: {str(e)}")
            return False

    async def check_health(self):
        """Jonni tekshirish va to'ldirish"""
        try:
            await self.client.send_message(self.bot_username, "/sahro")
            await asyncio.sleep(2)
            
            messages = await self.client.get_messages(self.bot_username, limit=3)
            for msg in messages:
                if "Joningiz" in msg.text:
                    health = re.search(r'Joningiz[^\d]*(\d+)', msg.text)
                    if health:
                        current_health = int(health.group(1))
                        await self.log(f"❤️ Jon: {current_health}/100")
                        
                        if current_health >= 5:
                            return True
                        
                        await self.log("🔴 Jon yetarli emas, to'ldirilmoqda...")
                        
                        if not await self.check_resources():
                            await self.log("❌ Jon to'ldirish uchun resurslar yetarli emas")
                            return False
                        
                        await self.client.send_message(self.bot_username, "Oshxona🏪")
                        await asyncio.sleep(2)
                        
                        kitchen_msgs = await self.client.get_messages(self.bot_username, limit=3)
                        for msg in kitchen_msgs:
                            if msg.buttons:
                                for row in msg.buttons:
                                    for button in row:
                                        if "sushi" in button.text.lower():
                                            await button.click()
                                            await self.log("🍣 Sushi sotib olindi (Olmos ishlatildi)")
                                            await asyncio.sleep(2)
                                            return True
                                
                                foods = [
                                    {"nomi": "Polov🍲", "narxi": 20, "jon": 10},
                                    {"nomi": "Lag'mon🍜", "narxi": 10, "jon": 5},
                                    {"nomi": "Sho'rva🍛", "narxi": 5, "jon": 3},
                                    {"nomi": "Go'sht🍗", "narxi": 2, "jon": 1}
                                ]
                                
                                for food in foods:
                                    for row in msg.buttons:
                                        for button in row:
                                            if food["nomi"] in button.text:
                                                await button.click()
                                                await self.log(f"🍽 {food['nomi']} sotib olindi (+{food['jon']} jon)")
                                                await asyncio.sleep(2)
                                                return True
                        
                        await self.log("⚠️ Hech qanday ovqat sotib olinmadi")
                        return False
            
            await self.log("⚠️ Jon ma'lumotlari topilmadi")
            return False
            
        except Exception as e:
            await self.log(f"❌ Jonni to'ldirishda xato: {str(e)}")
            return False

    async def start_kraken_hunt(self):
        try:
            msg = await self.client.get_messages(self.bot_username, ids=self.kraken_message_id)
            
            if not msg:
                messages = await self.client.get_messages(self.bot_username, limit=5)
                for m in messages:
                    if m.buttons:
                        for row in m.buttons:
                            for button in row:
                                if "Krakenni ovlashni boshlash" in button.text:
                                    msg = m
                                    break
            
            if msg and msg.buttons:
                for row in msg.buttons:
                    for button in row:
                        if "Krakenni ovlashni boshlash" in button.text:
                            await button.click()
                            await self.log("⛵️ Kraken ovlash boshlandi! 41 daqiqa kutilmoqda...")
                            return True
            
            await self.log("⚠️ Kraken ovlash tugmasi topilmadi")
            return False
            
        except Exception as e:
            await self.log(f"❌ Kraken ovlashda xato: {str(e)}")
            return False

    async def handle_messages(self, event):
        """Xabarlarni qayta ishlash"""
        if event.is_private and event.sender_id == (await self.client.get_me()).id:
            text = event.message.text.lower()
            
            if text in ['/start', '.kraken on']:
                if self.is_running:
                    await event.reply("ℹ️ Bot allaqachon ishlamoqda!")
                    return
                    
                self.is_running = True
                self.stop_event.clear()
                if self.hunting_task:
                    self.hunting_task.cancel()
                self.hunting_task = asyncio.create_task(self.hunting_cycle())
                await event.reply(f"✅ {self.session_name} uchun Kraken ovlash boshlandi!")
                
            elif text in ['/stop', '.kraken stop']:
                if not self.is_running:
                    await event.reply("ℹ️ Bot allaqachon to'xtatilgan!")
                    return
                    
                self.is_running = False
                self.stop_event.set()
                if self.hunting_task:
                    self.hunting_task.cancel()
                await event.reply(f"🛑 {self.session_name} uchun Kraken ovlash to'xtatildi")
                
            elif text == '/info':
                status = "🟢 Ishlamoqda" if self.is_running else "🔴 To'xtatilgan"
                await event.reply(
                    f"📊 {self.session_name} ma'lumotlari:\n"
                    f"• Holat: {status}\n"
                    f"• Xabar ID: {self.kraken_message_id}\n"
                    f"• So'nggi harakat: {self.last_action_time}"
                )

    async def hunting_cycle(self):
        """Kraken ovlash tsikli"""
        try:
            while not self.stop_event.is_set():
                await asyncio.sleep(10)
                
                if not await self.check_resources():
                    await self.log("🔴 Resurslar yetarli emas, 10 soniya kutish...")
                    await asyncio.sleep(10)
                    continue
                    
                if not await self.check_health():
                    await self.log("🔴 Jon to'ldirish muvaffaqiyatsiz, 10 soniya kutish...")
                    await asyncio.sleep(10)
                    continue
                    
                if await self.start_kraken_hunt():
                    for _ in range(246):
                        await asyncio.sleep(10)
                        if not self.is_running or self.stop_event.is_set():
                            await self.log("🛑 Kraken ovlash to'xtatildi")
                            return
                    
                    await self.log("🎉 Kraken ovlash muvaffaqiyatli yakunlandi!")
                else:
                    await asyncio.sleep(10)
                    
        except asyncio.CancelledError:
            await self.log("🛑 Hunting cycle bekor qilindi")
            raise
        except Exception as e:
            await self.log(f"❌ Hunting cycleda katta xato: {str(e)}")
        finally:
            self.is_running = False
            self.stop_event.set()

async def main():
    sessions = [
        {"name": "maftuna", "api_id": 22456377, "api_hash": "f22c08aa10f86e8aa11efe6d41b27f21", "kraken_id": 29709},
        {"name": "jaxakrak", "api_id": 22456377, "api_hash": "f22c08aa10f86e8aa11efe6d41b27f21", "kraken_id": 28392},
        {"name": "umidga", "api_id": 22456377, "api_hash": "f22c08aa10f86e8aa11efe6d41b27f21", "kraken_id": 15334},
        {"name": "lafasovch", "api_id": 22456377, "api_hash": "f22c08aa10f86e8aa11efe6d41b27f21", "kraken_id": 6914},
        {"name": "uuucn", "api_id": 22456377, "api_hash": "f22c08aa10f86e8aa11efe6d41b27f21", "kraken_id": 7745},
    ]
    
    print("🚀 Kraken Ovlash Boti ishga tushmoqda...\n")
    
    hunters = []
    for config in sessions:
        try:
            hunter = KrakenHunter(
                session_name=config["name"],
                api_id=config["api_id"],
                api_hash=config["api_hash"],
                kraken_message_id=config["kraken_id"]
            )
            await hunter.client.start()
            hunters.append(hunter)
            print(f"✅ {config['name']} - Xabar ID: {config['kraken_id']}")
        except Exception as e:
            print(f"❌ {config['name']} sessionini ishga tushirishda xato: {str(e)}")
    
    print("\n📌 Buyruqlar har bir session uchun alohida:")
    print("• /start yoki .kraken on - Botni ishga tushirish")
    print("• /stop yoki .kraken stop - Botni to'xtatish")
    print("• /info - Session holati haqida ma'lumot\n")
    
    await asyncio.gather(*[hunter.client.run_until_disconnected() for hunter in hunters])

if __name__ == '__main__':
    asyncio.run(main())
