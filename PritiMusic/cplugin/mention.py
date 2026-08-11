import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus

# Make sure this filter supports clone clients in its internal logic
from PritiMusic.utils.istkhar_ban import admin_filter

# Store active spam chats
SPAM_CHATS = []

@Client.on_message(filters.command(["mention", "all"]) & filters.group & admin_filter)
async def tag_all_users(client: Client, message: Message): 
    replied = message.reply_to_message  
    
    if len(message.command) < 2 and not replied:
        await message.reply_text("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴛᴀɢ ᴀʟʟ**") 
        return                  
    
    if replied:
        SPAM_CHATS.append(message.chat.id)      
        usernum = 0
        usertxt = ""
        
        async for m in client.get_chat_members(message.chat.id): 
            if message.chat.id not in SPAM_CHATS:
                break       
                
            usernum += 1
            usertxt += f"\n⊚ [{m.user.first_name}](tg://user?id={m.user.id})\n"
            
            if usernum == 5:
                await replied.reply_text(usertxt)
                await asyncio.sleep(2)
                usernum = 0
                usertxt = ""
                
        try:
            if message.chat.id in SPAM_CHATS:
                SPAM_CHATS.remove(message.chat.id)
        except Exception:
            pass
            
    else:
        text = message.text.split(None, 1)[1]
        SPAM_CHATS.append(message.chat.id)
        
        usernum = 0
        usertxt = ""
        
        async for m in client.get_chat_members(message.chat.id):       
            if message.chat.id not in SPAM_CHATS:
                break 
                
            usernum += 1
            usertxt += f"\n⊚ [{m.user.first_name}](tg://user?id={m.user.id})\n"
            
            if usernum == 5:
                await client.send_message(message.chat.id, f'{text}\n{usertxt}')
                await asyncio.sleep(2)
                usernum = 0
                usertxt = ""                          
                
        try:
            if message.chat.id in SPAM_CHATS:
                SPAM_CHATS.remove(message.chat.id)
        except Exception:
            pass        
           

@Client.on_message(filters.command("alloff") & ~filters.private)
async def cancelcmd(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id in SPAM_CHATS:
        try:
            SPAM_CHATS.remove(chat_id)
        except Exception:
            pass   
        return await message.reply_text("**ᴛᴀɢ ᴀʟʟ sᴜᴄᴄᴇssғᴜʟʟʏ sᴛᴏᴘᴘᴇᴅ!**")     
                                     
    else:
        await message.reply_text("**ɴᴏ ᴘʀᴏᴄᴇss ᴏɴɢᴏɪɴɢ!**")  
        return       
              
