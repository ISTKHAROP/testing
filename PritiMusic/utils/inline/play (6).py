import math
import random

from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton

from config import SUPPORT_CHAT, SUPPORT_CHANNEL, OWNER_USERNAME
from PritiMusic import app
import config
from PritiMusic.utils.formatters import time_to_seconds

# 💎 Premium Emojis ID List for Pyrogram's icon_custom_emoji_id
PREMIUM_EMOJIS = [
    5258362837411045098, 6102938383456146362, 5463274047771000031, 6100397162976252509,
    5373310679241466020, 5408916593780470262, 5776182936638329359, 5258389041006518073,
    6280269890821558384, 5936143551854285132, 6172332822892647766, 5891211339170326418,
    5409368076447657845, 6172312314423808834, 6082387600599944892, 6271537028307881531
]

# 🎧 Specific Premium Emoji IDs for Playback Controls
PLAY_EMOJI = 6158973722255429425     # ▶️
PAUSE_EMOJI = 4970176665062736422    # ⏸️
EQ_EMOJI = 5350396951407895212       # 🎛 (Equalizer / Menu Icon - Replaced Replay)
SKIP_EMOJI = 4969851488793788974     # ⏭️
STOP_EMOJI = 6129486856212979482     # 🛑

# 🎛 Specific Premium Emoji IDs for EQ & Volume Menu
EMOJI_VDOWN = 5409331062419502443    # 🔉
EMOJI_VUP = 6039381989985882045      # 📢
EMOJI_BOOST = 6172332822892647766    # 🚀
EMOJI_8D = 5373310679241466020       # 🌀
EMOJI_AUDI = 6188045471118790922     # 🌍
EMOJI_DJ = 6082387600599944892       # 🎧
EMOJI_BASS = 6100220081474639964     # ⚡️
EMOJI_CLUB = 6172312314423808834     # ✨
EMOJI_SLOWED = 6172273586703700991   # 🥀
EMOJI_NIGHTCORE = 5258334469152054985# 🎶
EMOJI_NORMAL = 5350396951407895212   # ⚙️
EMOJI_UPDATES = 6039381989985882045  # 📢
EMOJI_SUPPORT = 6021618194228187816  # 💬
EMOJI_OWNER = 6237864166879663987    # 👑
EMOJI_BACK = 5352759161945867747     # 🔙

# 🎨 Dynamic Color Generator
def get_style_map():
    styles = [ButtonStyle.PRIMARY, ButtonStyle.SUCCESS, ButtonStyle.DANGER]
    random.shuffle(styles)
    return {1: styles[0], 2: styles[1], 3: styles[2], 4: styles[0]}

# 🔘 Smart Button Creator
def create_btn(text, cb=None, url=None, style=ButtonStyle.PRIMARY, emoji_id=None, no_emoji=False):
    kwargs = {"text": text, "style": style}
    if cb: kwargs["callback_data"] = cb
    if url: kwargs["url"] = url
    
    # Premium Emoji Logic
    if emoji_id:
        kwargs["icon_custom_emoji_id"] = int(emoji_id)
    elif not no_emoji:
        kwargs["icon_custom_emoji_id"] = int(random.choice(PREMIUM_EMOJIS))
        
    return InlineKeyboardButton(**kwargs)

# Helper for the Clone button
def clone_button(style):
    return create_btn(
        text="ᴄʟᴏɴᴇ-ᴍᴇ", 
        url="https://t.me/clone_MUSICrobot",
        style=style
    )

# --- NESTED EQ & VOLUME MARKUP ---
def eq_markup(_, chat_id):
    s_map = get_style_map()
    buttons = [
        # 1. Volume Controller & Booster
        [
            create_btn(text="V-Down", cb=f"vol_down|{chat_id}", style=s_map[2], emoji_id=EMOJI_VDOWN),
            create_btn(text="V-Up", cb=f"vol_up|{chat_id}", style=s_map[2], emoji_id=EMOJI_VUP),
            create_btn(text="Booster", cb=f"vol_boost|{chat_id}", style=s_map[1], emoji_id=EMOJI_BOOST)
        ],
        # 2. Spatial & Auditorium
        [
            create_btn(text="8D Audio", cb=f"eq_8d|{chat_id}", style=s_map[1], emoji_id=EMOJI_8D),
            create_btn(text="Auditorium", cb=f"eq_auditorium|{chat_id}", style=s_map[1], emoji_id=EMOJI_AUDI)
        ],
        # 3. DJ, Bass & Club 
        [
            create_btn(text="DJ Remix", cb=f"eq_dj|{chat_id}", style=s_map[1], emoji_id=EMOJI_DJ),
            create_btn(text="Punchy Bass", cb=f"eq_bass|{chat_id}", style=s_map[1], emoji_id=EMOJI_BASS)
        ],
        [
            create_btn(text="EDM/Club", cb=f"eq_club|{chat_id}", style=s_map[1], emoji_id=EMOJI_CLUB),
            create_btn(text="Slowed", cb=f"eq_slowed|{chat_id}", style=s_map[3], emoji_id=EMOJI_SLOWED)
        ],
        # 4. Trends & Normal
        [
            create_btn(text="Nightcore", cb=f"eq_nightcore|{chat_id}", style=s_map[3], emoji_id=EMOJI_NIGHTCORE),
            create_btn(text="Normal", cb=f"eq_normal|{chat_id}", style=s_map[3], emoji_id=EMOJI_NORMAL)
        ],
        # 5. Support & Update
        [
            create_btn(text="Update Channel", url=SUPPORT_CHANNEL, style=s_map[2], emoji_id=EMOJI_UPDATES),
            create_btn(text="Support Channel", url=SUPPORT_CHAT, style=s_map[2], emoji_id=EMOJI_SUPPORT)
        ],
        # 6. Credits & Back Button
        [
            create_btn(text="the shiv", url=f"https://t.me/{OWNER_USERNAME}", style=s_map[3], emoji_id=EMOJI_OWNER),
            create_btn(text="Back", cb=f"PanelMarkup None|{chat_id}", style=s_map[1], emoji_id=EMOJI_BACK)
        ]
    ]
    return buttons


# --- STANDARD MARKUP FUNCTIONS ---

def track_markup(_, videoid, user_id, channel, fplay):
    s_map = get_style_map()
    buttons = [
        [
            create_btn(text=_["P_B_1"], cb=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style=s_map[2]),
            create_btn(text=_["P_B_2"], cb=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style=s_map[2]),
        ],
        [
            clone_button(s_map[1]),
            create_btn(text=_["CLOSE_BUTTON"], cb=f"forceclose {videoid}|{user_id}", style=s_map[2])
        ],
    ]
    return buttons


def stream_markup_timer(_, chat_id, played, dur):
    try:
        played_sec = time_to_seconds(str(played))
        if str(dur).lower() in ["live", "unknown", "0"]:
            duration_sec = 0
        else:
            duration_sec = time_to_seconds(str(dur))
    except Exception:
        played_sec = 0
        duration_sec = 0
    
    total_blocks = 10
    if duration_sec > 0:
        filled_blocks = int((played_sec / duration_sec) * total_blocks)
    else:
        filled_blocks = 0
        
    filled_blocks = min(max(filled_blocks, 0), total_blocks)
    bar = "▰" * filled_blocks + "▱" * (total_blocks - filled_blocks)

    s_map = get_style_map()
    buttons = [
        # Row 1: Timer
        [
            create_btn(text=f"{played} {bar} {dur}", cb="GetTimer", style=s_map[1])
        ],
        # Row 2: 5 Compact Play Controls with EQ Menu replacing Replay
        [
            create_btn(text="\u200b", cb=f"ADMIN Resume|{chat_id}", style=s_map[3], emoji_id=PLAY_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Pause|{chat_id}", style=s_map[3], emoji_id=PAUSE_EMOJI),
            create_btn(text="\u200b", cb=f"EQMenu|{chat_id}", style=s_map[3], emoji_id=EQ_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Skip|{chat_id}", style=s_map[3], emoji_id=SKIP_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Stop|{chat_id}", style=s_map[3], emoji_id=STOP_EMOJI),
        ],
        # Row 3: Autoplay & Clone merged
        [
            create_btn(text="ᴀᴜᴛᴏ-ᴘʟᴀʏ", cb=f"ADMIN Autoplay|{chat_id}", style=s_map[1]),
            clone_button(s_map[1])
        ],
        # Row 4: Close
        [
            create_btn(text=_["CLOSE_BUTTON"], cb="close", style=s_map[2]),
        ]
    ]
    return buttons


def stream_markup(_, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            create_btn(text="\u200b", cb=f"ADMIN Resume|{chat_id}", style=s_map[3], emoji_id=PLAY_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Pause|{chat_id}", style=s_map[3], emoji_id=PAUSE_EMOJI),
            create_btn(text="\u200b", cb=f"EQMenu|{chat_id}", style=s_map[3], emoji_id=EQ_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Skip|{chat_id}", style=s_map[3], emoji_id=SKIP_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Stop|{chat_id}", style=s_map[3], emoji_id=STOP_EMOJI),
        ],
        [
            create_btn(text="ᴀᴜᴛᴏ-ᴘʟᴀʏ", cb=f"ADMIN Autoplay|{chat_id}", style=s_map[1]),
            clone_button(s_map[1])
        ],
        [
            create_btn(text=_["CLOSE_BUTTON"], cb="close", style=s_map[2]),
        ]
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    s_map = get_style_map()
    buttons = [
        [
            create_btn(text=_["P_B_1"], cb=f"LuckyPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}", style=s_map[2]),
            create_btn(text=_["P_B_2"], cb=f"LuckyPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}", style=s_map[2]),
        ],
        [
            clone_button(s_map[1]),
            create_btn(text=_["CLOSE_BUTTON"], cb=f"forceclose {videoid}|{user_id}", style=s_map[2])
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    s_map = get_style_map()
    buttons = [
        [
            create_btn(text=_["P_B_3"], cb=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}", style=s_map[1]),
        ],
        [
            clone_button(s_map[1]),
            create_btn(text=_["CLOSE_BUTTON"], cb=f"forceclose {videoid}|{user_id}", style=s_map[2])
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    s_map = get_style_map()
    buttons = [
        [
            create_btn(text=_["P_B_1"], cb=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}", style=s_map[2]),
            create_btn(text=_["P_B_2"], cb=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}", style=s_map[2]),
        ],
        [
            create_btn(text="ʙᴀᴄᴋ", cb=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}", style=s_map[3], emoji_id=EMOJI_BWD),
            create_btn(text=_["CLOSE_BUTTON"], cb=f"forceclose {query}|{user_id}", style=s_map[3], emoji_id=EMOJI_CLOSE),
            create_btn(text="ɴᴇxᴛ", cb=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}", style=s_map[3], emoji_id=EMOJI_FWD),
        ],
        [clone_button(s_map[2])],
    ]
    return buttons


def telegram_markup(_, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            create_btn(text="ɴᴇxᴛ", cb=f"PanelMarkup None|{chat_id}", style=s_map[1]),
            create_btn(text=_["CLOSEMENU_BUTTON"], cb="close", style=s_map[2]),
        ],
    ]
    return buttons


def queue_markup(_, videoid, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            create_btn(text=_["S_B_3"], url=f"https://t.me/{app.username}?startgroup=true", style=s_map[1]),
        ],
        [
            create_btn(text="\u200b", cb=f"ADMIN Resume|{chat_id}", style=s_map[3], emoji_id=PLAY_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Pause|{chat_id}", style=s_map[3], emoji_id=PAUSE_EMOJI),
            create_btn(text="\u200b", cb=f"EQMenu|{chat_id}", style=s_map[3], emoji_id=EQ_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Skip|{chat_id}", style=s_map[3], emoji_id=SKIP_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Stop|{chat_id}", style=s_map[3], emoji_id=STOP_EMOJI),
        ],
        [
            create_btn(text="ᴀᴜᴛᴏ-ᴘʟᴀʏ", cb=f"ADMIN Autoplay|{chat_id}", style=s_map[1]),
            clone_button(s_map[1])
        ],
        [
            create_btn(text="ᴍᴏʀᴇ", cb=f"PanelMarkup None|{chat_id}", style=s_map[1]),
        ],
    ]
    return buttons


def stream_markup2(_, chat_id):
    return stream_markup(_, chat_id)


def stream_markup_timer2(_, chat_id, played, dur):
    return stream_markup_timer(_, chat_id, played, dur)


def panel_markup_1(_, videoid, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            create_btn(text=_["S_B_3"], url=f"https://t.me/{app.username}?startgroup=true", style=s_map[1]),
        ],
        [
            create_btn(text="sʜᴜғғʟᴇ", cb=f"ADMIN Shuffle|{chat_id}", style=s_map[3]),
            create_btn(text="ʟᴏᴏᴘ", cb=f"ADMIN Loop|{chat_id}", style=s_map[3]),
        ],
        [
            create_btn(text="-10 sᴇᴄ", cb=f"ADMIN 1|{chat_id}", style=s_map[2]),
            create_btn(text="+10 sᴇᴄ", cb=f"ADMIN 2|{chat_id}", style=s_map[2]),
        ],
        [
            create_btn(text="ᴀᴜᴛᴏ-ᴘʟᴀʏ", cb=f"ADMIN Autoplay|{chat_id}", style=s_map[1]),
            clone_button(s_map[1])
        ],
        [
            create_btn(text="ʜᴏᴍᴇ", cb=f"Pages Back|2|{videoid}|{chat_id}", style=s_map[2]),
            create_btn(text="ɴᴇxᴛ", cb=f"Pages Forw|2|{videoid}|{chat_id}", style=s_map[2]),
        ],
    ]
    return buttons


def panel_markup_2(_, videoid, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            create_btn(text=_["S_B_3"], url=f"https://t.me/{app.username}?startgroup=true", style=s_map[1]),
        ],
        [
            create_btn(text="0.5x", cb=f"SpeedUP {chat_id}|0.5", style=s_map[3]),
            create_btn(text="0.75x", cb=f"SpeedUP {chat_id}|0.75", style=s_map[3]),
            create_btn(text="1.0x", cb=f"SpeedUP {chat_id}|1.0", style=s_map[3]),
        ],
        [
            create_btn(text="1.5x", cb=f"SpeedUP {chat_id}|1.5", style=s_map[2]),
            create_btn(text="2.0x", cb=f"SpeedUP {chat_id}|2.0", style=s_map[2]),
        ],
        [
            clone_button(s_map[1]),
            create_btn(text="ʙᴀᴄᴋ", cb=f"Pages Back|1|{videoid}|{chat_id}", style=s_map[1], emoji_id=EMOJI_BACK),
        ],
    ]
    return buttons


def panel_markup_5(_, videoid, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            create_btn(text=_["S_B_3"], url=f"https://t.me/{app.username}?startgroup=true", style=s_map[1]),
        ],
        [
            create_btn(text="\u200b", cb=f"ADMIN Resume|{chat_id}", style=s_map[3], emoji_id=PLAY_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Pause|{chat_id}", style=s_map[3], emoji_id=PAUSE_EMOJI),
            create_btn(text="\u200b", cb=f"EQMenu|{chat_id}", style=s_map[3], emoji_id=EQ_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Skip|{chat_id}", style=s_map[3], emoji_id=SKIP_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Stop|{chat_id}", style=s_map[3], emoji_id=STOP_EMOJI),
        ],
        [
            create_btn(text="ᴀᴜᴛᴏ-ᴘʟᴀʏ", cb=f"ADMIN Autoplay|{chat_id}", style=s_map[1]),
            clone_button(s_map[1])
        ],
        [
            create_btn(text="ʜᴏᴍᴇ", cb=f"MainMarkup {videoid}|{chat_id}", style=s_map[2]),
            create_btn(text="ɴᴇxᴛ", cb=f"Pages Forw|1|{videoid}|{chat_id}", style=s_map[2]),
        ],
    ]
    return buttons


def panel_markup_3(_, videoid, chat_id):
    s_map = get_style_map()
    buttons = [
        [
            create_btn(text="0.5x", cb=f"SpeedUP {chat_id}|0.5", style=s_map[3]),
            create_btn(text="0.75x", cb=f"SpeedUP {chat_id}|0.75", style=s_map[3]),
            create_btn(text="1.0x", cb=f"SpeedUP {chat_id}|1.0", style=s_map[3]),
        ],
        [
            create_btn(text="1.5x", cb=f"SpeedUP {chat_id}|1.5", style=s_map[2]),
            create_btn(text="2.0x", cb=f"SpeedUP {chat_id}|2.0", style=s_map[2]),
        ],
        [
            clone_button(s_map[1]),
            create_btn(text="ʙᴀᴄᴋ", cb=f"Pages Back|2|{videoid}|{chat_id}", style=s_map[1], emoji_id=EMOJI_BACK),
        ],
    ]
    return buttons


def panel_markup_4(_, vidid, chat_id, played, dur):
    try:
        played_sec = time_to_seconds(str(played))
        if str(dur).lower() in ["live", "unknown", "0"]:
            duration_sec = 0
        else:
            duration_sec = time_to_seconds(str(dur))
    except Exception:
        played_sec = 0
        duration_sec = 0
    
    total_blocks = 10
    if duration_sec > 0:
        filled_blocks = int((played_sec / duration_sec) * total_blocks)
    else:
        filled_blocks = 0
        
    filled_blocks = min(max(filled_blocks, 0), total_blocks)
    bar = "▰" * filled_blocks + "▱" * (total_blocks - filled_blocks)

    s_map = get_style_map()
    buttons = [
        [
            create_btn(text=f"{played} {bar} {dur}", cb="GetTimer", style=s_map[1])
        ],
        [
            create_btn(text="\u200b", cb=f"ADMIN Resume|{chat_id}", style=s_map[3], emoji_id=PLAY_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Pause|{chat_id}", style=s_map[3], emoji_id=PAUSE_EMOJI),
            create_btn(text="\u200b", cb=f"EQMenu|{chat_id}", style=s_map[3], emoji_id=EQ_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Skip|{chat_id}", style=s_map[3], emoji_id=SKIP_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Stop|{chat_id}", style=s_map[3], emoji_id=STOP_EMOJI),
        ],
        [
            create_btn(text="ᴀᴜᴛᴏ-ᴘʟᴀʏ", cb=f"ADMIN Autoplay|{chat_id}", style=s_map[1]),
            clone_button(s_map[1])
        ],
        [
            create_btn(text="ʜᴏᴍᴇ", cb=f"MainMarkup {vidid}|{chat_id}", style=s_map[1]),
        ],
    ]
    return buttons


def panel_markup_clone(_, vidid, chat_id, played, dur):
    try:
        played_sec = time_to_seconds(str(played))
        if str(dur).lower() in ["live", "unknown", "0"]:
            duration_sec = 0
        else:
            duration_sec = time_to_seconds(str(dur))
    except Exception:
        played_sec = 0
        duration_sec = 0
    
    total_blocks = 10
    if duration_sec > 0:
        filled_blocks = int((played_sec / duration_sec) * total_blocks)
    else:
        filled_blocks = 0
        
    filled_blocks = min(max(filled_blocks, 0), total_blocks)
    bar = "▰" * filled_blocks + "▱" * (total_blocks - filled_blocks)

    s_map = get_style_map()
    buttons = [
        [
            create_btn(text=f"{played} {bar} {dur}", cb="GetTimer", style=s_map[1])
        ],
        [
            create_btn(text="\u200b", cb=f"ADMIN Resume|{chat_id}", style=s_map[3], emoji_id=PLAY_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Pause|{chat_id}", style=s_map[3], emoji_id=PAUSE_EMOJI),
            create_btn(text="\u200b", cb=f"EQMenu|{chat_id}", style=s_map[3], emoji_id=EQ_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Skip|{chat_id}", style=s_map[3], emoji_id=SKIP_EMOJI),
            create_btn(text="\u200b", cb=f"ADMIN Stop|{chat_id}", style=s_map[3], emoji_id=STOP_EMOJI),
        ],
        [
            create_btn(text="-20s", cb=f"ADMIN SeekBack|{chat_id}", style=s_map[4]),
            create_btn(text="+20s", cb=f"ADMIN SeekForward|{chat_id}", style=s_map[4]),
        ],
        [
            create_btn(text="ᴀᴜᴛᴏ-ᴘʟᴀʏ", cb=f"ADMIN Autoplay|{chat_id}", style=s_map[1]),
            clone_button(s_map[1])
        ],
        [
            create_btn(text=_["CLOSE_BUTTON"], cb="close", style=s_map[2], emoji_id=EMOJI_CLOSE)
        ]
    ]
    return buttons
