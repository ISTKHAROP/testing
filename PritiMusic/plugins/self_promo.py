import asyncio
import time
from datetime import datetime, timedelta, timezone
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait

from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI, LOGGER_ID, SUDOERS, OWNER_ID
from PritiMusic import app
from PritiMusic.utils.database import get_served_users, get_served_chats

# IST (Indian Standard Time) Setup
IST = timezone(timedelta(hours=5, minutes=30))

# ==========================================
# DATABASE SETUP
# ==========================================
dbclient = AsyncIOMotorClient(MONGO_DB_URI)
db = dbclient.MahiMusic
promo_msgs_db = db.promo_messages
promo_toggle_db = db.promo_settings
broadcast_time_db = db.promo_time

async def is_promo_on() -> bool:
    chat = await promo_toggle_db.find_one({"_id": "promo_toggle"})
    if not chat:
        return False
    return chat.get("status", False)

async def set_promo_status(status: bool):
    await promo_toggle_db.update_one({"_id": "promo_toggle"}, {"$set": {"status": status}}, upsert=True)

async def save_promo_msg(chat_id: int, message_id: int):
    await promo_msgs_db.insert_one({
        "chat_id": chat_id,
        "message_id": message_id,
        "timestamp": int(time.time())
    })

async def get_old_promo_msgs():
    time_limit = int(time.time()) - 172800 # 48 hours
    return promo_msgs_db.find({"timestamp": {"$lt": time_limit}})

async def delete_promo_record(chat_id: int, message_id: int):
    await promo_msgs_db.delete_one({"chat_id": chat_id, "message_id": message_id})


# ==========================================
# PROMO DETAILS
# ==========================================
PROMO_IMAGE = "https://d.uguu.se/beSAOQgM.jpg"
PROMO_TEXT = """
╔═══════ ✦ 🎧 ✦ ═══════╗
       ѕɪᴢᴢᴜ ᴍᴜꜱɪᴄ
      ᴄʟᴏɴᴇ ꜰᴜᴛᴜʀᴇ
╚═══════ ✦ 🎧 ✦ ═══════╝

⊚ ᴛʜɪꜱ ɪꜱ ✶ ѕɪᴢᴢᴜ ᴍᴜꜱɪᴄ ᴄʟᴏɴᴇ ✶

➻ ᴘʀᴇᴍɪᴜᴍ ᴅᴇꜱɪɢɴ
➻ ꜱᴍᴀʀᴛ ᴍᴜꜱɪᴄ ᴘʟᴀʏᴇʀ
➻ ʙᴜɪʟᴛ ꜰᴏʀ ᴛᴇʟᴇɢʀᴀᴍ

🎧 24x7 ᴍᴜꜱɪᴄ
⚡️ ꜰᴀꜱᴛ ʀᴇꜱᴘᴏɴꜱᴇ
🎶 ᴜɴʟɪᴍɪᴛᴇᴅ ᴘʟᴀʏ
🔊 ʜɪɢʜ-ǫᴜᴀʟɪᴛʏ ᴀᴜᴅɪᴏ
💫 ꜱᴛᴀʙʟᴇ & ꜱᴍᴏᴏᴛʜ

➻ ᴀᴅᴅ ᴍᴇ ➜ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ
➻ /play ꜱᴏɴɢ ɴᴀᴍᴇ 🎵

🎀 ѕɪᴢᴢᴜ ᴍᴜꜱɪᴄ
✦ ᴄʟᴏɴᴇ ꜰᴜᴛᴜʀᴇ ✦
"""

# FIX: Pyrogram doesn't support 'ButtonStyle', so it was removed to prevent crashes.
PROMO_BUTTON = InlineKeyboardMarkup(
    [[
        InlineKeyboardButton(
            "🎵 ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ 🎧",
            url="https://t.me/SizzuMusicBot"
        ),
        InlineKeyboardButton(
            "✦ ᴄʟᴏɴᴇ ꜰᴜᴛᴜʀᴇ ✦",
            url="https://t.me/SizzuMusicBot"
        )
    ]]
)


# ==========================================
# CORE BROADCAST FUNCTION
# ==========================================
async def run_broadcast():
    users = await get_served_users()
    chats = await get_served_chats()

    u_success, u_failed = 0, 0
    g_success, g_failed = 0, 0

    # Broadcast to Users
    for user in users:
        user_id = user["user_id"] if isinstance(user, dict) else user
        try:
            msg = await app.send_photo(
                chat_id=int(user_id),
                photo=PROMO_IMAGE,
                caption=PROMO_TEXT,
                reply_markup=PROMO_BUTTON
            )
            await save_promo_msg(int(user_id), msg.id)
            u_success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            u_failed += 1
        await asyncio.sleep(0.5)

    # Broadcast to Groups
    for chat in chats:
        chat_id = chat["chat_id"] if isinstance(chat, dict) else chat
        try:
            msg = await app.send_photo(
                chat_id=int(chat_id),
                photo=PROMO_IMAGE,
                caption=PROMO_TEXT,
                reply_markup=PROMO_BUTTON
            )
            await save_promo_msg(int(chat_id), msg.id)
            g_success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            g_failed += 1
        await asyncio.sleep(0.5)

    return u_success, u_failed, g_success, g_failed


# ==========================================
# COMMAND: ON / OFF / RUN
# ==========================================
@app.on_message(filters.command(["selfpromo", "promo"], prefixes=["/", "!", "."]))
async def promo_toggle_cmd(client, message: Message):
    user_id = message.from_user.id
    
    sudo_list = [int(x) for x in SUDOERS] if isinstance(SUDOERS, list) else []
    owner_id_int = int(OWNER_ID) if OWNER_ID else 0
    
    if user_id not in sudo_list and user_id != owner_id_int:
        return await message.reply_text(
            f"❌ **Access Denied!**\n"
            f"Mujhe laga aap owner ho, par aapki User ID `{user_id}` config.py ke `SUDOERS` ya `OWNER_ID` mein nahi hai."
        )

    if len(message.command) != 2:
        return await message.reply_text(
            "**Usage Options:**\n"
            "`/selfpromo on` - Start auto broadcast (7 AM & 7 PM)\n"
            "`/selfpromo off` - Stop auto broadcast\n"
            "`/selfpromo run` - Instantly broadcast right now"
        )
    
    state = message.command[1].lower()
    
    if state == "on":
        await set_promo_status(True)
        await message.reply_text("✅ **Auto Self Promo Started!**\nBot will broadcast daily at 7:00 AM & 7:00 PM.")
        
    elif state == "off":
        await set_promo_status(False)
        await message.reply_text("❌ **Auto Self Promo Stopped!**")
        
    elif state == "run":
        status_msg = await message.reply_text("🔄 **Manual Broadcast Started...** Please wait.")
        try:
            u_success, u_failed, g_success, g_failed = await run_broadcast()
            stats_text = f"📢 **Manual Promo Completed**\n\n👥 **Users:** ✅ {u_success} | ❌ {u_failed}\n🏘 **Groups:** ✅ {g_success} | ❌ {g_failed}"
            await status_msg.edit_text(stats_text)
            if LOGGER_ID:
                await app.send_message(LOGGER_ID, stats_text)
        except Exception as e:
            await status_msg.edit_text(f"❌ Error in broadcast: {e}")
            
    else:
        await message.reply_text("**Invalid argument.** Use `/selfpromo on`, `off`, or `run`.")


# ==========================================
# BACKGROUND TASK: TWICE A DAY & 48H DELETE
# ==========================================
async def auto_promo_task():
    while True:
        try:
            # 1. DELETE OLD MESSAGES (48 HOURS OLD)
            old_messages = await get_old_promo_msgs()
            async for doc in old_messages:
                try:
                    await app.delete_messages(chat_id=doc["chat_id"], message_ids=doc["message_id"])
                except Exception:
                    pass
                await delete_promo_record(doc["chat_id"], doc["message_id"])
                await asyncio.sleep(1)

            # 2. CHECK IF PROMO IS ON
            if await is_promo_on():
                now = datetime.now(IST)
                
                # Check current target slot (7 AM or 7 PM)
                if now.hour >= 19:
                    current_target_slot = f"{now.strftime('%Y-%m-%d')}_19"
                elif now.hour >= 7:
                    current_target_slot = f"{now.strftime('%Y-%m-%d')}_07"
                else:
                    yesterday = now - timedelta(days=1)
                    current_target_slot = f"{yesterday.strftime('%Y-%m-%d')}_19"
                
                # 3. GET LAST RUN SLOT
                last_run_data = await broadcast_time_db.find_one({"_id": "last_run_slot"})
                last_run_slot = last_run_data["slot"] if last_run_data else ""
                
                # Agar last run wala slot aur abhi ka slot alag hai, toh bot promo bhejega
                # Ye bot restart hone par bhi properly handle karega
                if last_run_slot != current_target_slot:
                    await broadcast_time_db.update_one({"_id": "last_run_slot"}, {"$set": {"slot": current_target_slot}}, upsert=True)
                    
                    u_success, u_failed, g_success, g_failed = await run_broadcast()
                    stats_text = f"📢 **Auto Promo Completed ({current_target_slot}:00)**\n\n👥 **Users:** ✅ {u_success} | ❌ {u_failed}\n🏘 **Groups:** ✅ {g_success} | ❌ {g_failed}"
                    if LOGGER_ID:
                        await app.send_message(LOGGER_ID, stats_text)

        except Exception as e:
            pass
            
        # Har 60 seconds (1 min) mein check karega taaki exact time par hit ho
        await asyncio.sleep(60)

# Task Start Hook
try:
    asyncio.get_event_loop().create_task(auto_promo_task())
except:
    pass
