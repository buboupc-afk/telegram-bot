import os, json, time, threading, random, traceback
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7142950609"))
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN Railway Variables me add karo.")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
DATA_FILE = "data.json"
AUTO_DELETE_SECONDS = 300

DEFAULT = {
    "admins": [ADMIN_ID],
    "channels": [],
    "rewards": [],
    "users": [],
    "forward": True,
    "auto_delete": True,
    "refer": {"on": True, "target": 2, "reward_index": 0, "refs": {}, "claimed": []},
    "ads": {"on": True, "interval": 3600, "items": [], "targets": []}
}

def load():
    if not os.path.exists(DATA_FILE):
        save(DEFAULT)
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    for k, v in DEFAULT.items():
        if k not in data:
            data[k] = v
    return data

def save(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, indent=2)

db = load()

def safe_send(chat_id, text, **kwargs):
    msg = bot.send_message(chat_id, text, **kwargs)
    if db.get("auto_delete"):
        threading.Timer(AUTO_DELETE_SECONDS, delete_msg, args=(chat_id, msg.message_id)).start()
    return msg

def delete_msg(chat_id, msg_id):
    try:
        bot.delete_message(chat_id, msg_id)
    except:
        pass

def is_admin(uid):
    return int(uid) in db["admins"]

def add_user(uid):
    if uid not in db["users"]:
        db["users"].append(uid)
        save(db)

def admin_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📢 Channel", callback_data="channels"),
        types.InlineKeyboardButton("🎁 Reward", callback_data="rewards"),
        types.InlineKeyboardButton("👥 Refer", callback_data="refer"),
        types.InlineKeyboardButton("📣 Ads", callback_data="ads"),
        types.InlineKeyboardButton("📨 Broadcast", callback_data="broadcast"),
        types.InlineKeyboardButton("🎬 Media Broadcast", callback_data="mediabroadcast"),
        types.InlineKeyboardButton("🗑 Auto Delete", callback_data="autodelete"),
        types.InlineKeyboardButton("👮 Admins", callback_data="admins"),
        types.InlineKeyboardButton("📊 Stats", callback_data="stats"),
        types.InlineKeyboardButton("🔁 Forward", callback_data="forward")
    )
    return kb

def join_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(f"📢 Join {ch}", url=f"https://t.me/{ch.replace('@','')}") for ch in db["channels"]]
    if btns:
        kb.add(*btns)
    kb.add(types.InlineKeyboardButton("✅ VERIFY NOW", callback_data="verify"))
    return kb

def reward_claim_kb():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🎁 CLAIM REWARD", callback_data="claim_reward"))
    kb.add(types.InlineKeyboardButton("👥 MY REFER LINK", callback_data="my_ref_btn"))
    return kb

def check_join(uid):
    for ch in db["channels"]:
        try:
            mem = bot.get_chat_member(ch, uid)
            if mem.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def loading(chat_id, title):
    msg = bot.send_message(chat_id, f"{title}\n\n▰▱▱▱▱▱▱▱▱▱ 10%")
    for s in ["▰▰▱▱▱▱▱▱▱▱ 20%", "▰▰▰▰▱▱▱▱▱▱ 40%", "▰▰▰▰▰▰▱▱▱▱ 60%", "▰▰▰▰▰▰▰▰▱▱ 80%", "▰▰▰▰▰▰▰▰▰▰ 100%"]:
        time.sleep(0.45)
        try: bot.edit_message_text(f"{title}\n\n{s}", chat_id, msg.message_id)
        except: pass

@bot.message_handler(commands=["start"])
def start(m):
    uid = m.from_user.id
    add_user(uid)

    parts = m.text.split()
    if len(parts) > 1 and parts[1].isdigit() and db["refer"]["on"]:
        ref = parts[1]
        if str(uid) != ref:
            db["refer"]["refs"].setdefault(ref, [])
            if uid not in db["refer"]["refs"][ref]:
                db["refer"]["refs"][ref].append(uid)
                save(db)

    loading(uid, "👑 𝙂𝙊𝘿 𝙍𝘼𝙁𝙏𝘼𝘼𝙍 𝘽𝙊𝙏")

    text = f"""
<b>👑 GOD RAFTAAR HERE</b>

Hey <b>{m.from_user.first_name}</b> 🔥

📢 Join all channels below.
✅ Then click VERIFY NOW.
"""
    try:
        photos = bot.get_user_profile_photos(uid, limit=1)
        if photos.total_count > 0:
            bot.send_photo(uid, photos.photos[0][-1].file_id, caption=text, reply_markup=join_kb())
        else:
            safe_send(uid, text, reply_markup=join_kb())
    except:
        safe_send(uid, text, reply_markup=join_kb())

    if db["ads"]["on"] and db["ads"]["items"]:
        safe_send(uid, "📢 <b>Sponsored Ad</b>\n\n" + random.choice(db["ads"]["items"]))

@bot.callback_query_handler(func=lambda c: c.data == "verify")
def verify(c):
    uid = c.from_user.id
    msg = bot.send_message(uid, "🔎 Starting verification...\n\n▰▱▱▱▱▱▱▱▱▱ 10%")
    for s in [
        "📢 Checking channels...\n\n▰▰▰▱▱▱▱▱▱▱ 30%",
        "⚡ Verifying membership...\n\n▰▰▰▰▰▱▱▱▱▱ 50%",
        "🎁 Preparing reward...\n\n▰▰▰▰▰▰▰▱▱▱ 70%",
        "✅ Final checking...\n\n▰▰▰▰▰▰▰▰▰▱ 90%"
    ]:
        time.sleep(0.5)
        bot.edit_message_text(s, uid, msg.message_id)

    if check_join(uid):
        bot.edit_message_text("✅ Verification Successful!\n\nClick below to claim reward.", uid, msg.message_id, reply_markup=reward_claim_kb())
    else:
        bot.edit_message_text("❌ Verification Failed!\n\nPehle sab channel join karo.", uid, msg.message_id, reply_markup=join_kb())

@bot.callback_query_handler(func=lambda c: c.data == "claim_reward")
def claim_reward(c):
    uid = c.from_user.id
    if not check_join(uid):
        bot.answer_callback_query(c.id, "Pehle channels join karo.", show_alert=True)
        return
    ridx = db["refer"]["reward_index"]
    reward = db["rewards"][ridx] if db["rewards"] and 0 <= ridx < len(db["rewards"]) else "🎁 No reward set by admin."
    bot.send_message(uid, f"🎁 <b>Your Reward:</b>\n\n{reward}")

@bot.callback_query_handler(func=lambda c: c.data == "my_ref_btn")
def my_ref_btn(c):
    uid = str(c.from_user.id)
    count = len(db["refer"]["refs"].get(uid, []))
    link = f"https://t.me/{bot.get_me().username}?start={uid}"
    bot.send_message(c.from_user.id, f"👥 Referrals: {count}/{db['refer']['target']}\n🔗 {link}")

@bot.message_handler(commands=["admin"])
def admin(m):
    if is_admin(m.from_user.id):
        safe_send(m.chat.id, "🎛 <b>Admin Panel</b>", reply_markup=admin_menu())

@bot.callback_query_handler(func=lambda c: is_admin(c.from_user.id))
def panel(c):
    d = c.data
    if d == "stats":
        safe_send(c.message.chat.id, f"📊 Users: {len(db['users'])}\n📢 Channels: {len(db['channels'])}\n🎁 Rewards: {len(db['rewards'])}\n📣 Ads: {len(db['ads']['items'])}")
    elif d == "forward":
        db["forward"] = not db["forward"]; save(db)
        safe_send(c.message.chat.id, f"🔁 Forward: {'ON ✅' if db['forward'] else 'OFF ❌'}")
    elif d == "autodelete":
        db["auto_delete"] = not db["auto_delete"]; save(db)
        safe_send(c.message.chat.id, f"🗑 Auto delete 5 min: {'ON ✅' if db['auto_delete'] else 'OFF ❌'}")
    elif d == "channels":
        safe_send(c.message.chat.id, "📢 /addchannel @channel\n/removechannel @channel\n/listchannels")
    elif d == "rewards":
        safe_send(c.message.chat.id, "🎁 /addreward text/link\n/removereward 1\n/listrewards\n/setreferreward 1")
    elif d == "refer":
        safe_send(c.message.chat.id, "👥 /referon\n/referoff\n/setrefer 2\n/myref")
    elif d == "ads":
        safe_send(c.message.chat.id, "📣 /addad text\n/removead 1\n/listads\n/adson\n/adsoff\n/setadtime 3600\n/addadtarget @channel\n/listadtargets\n/runadnow")
    elif d == "admins":
        safe_send(c.message.chat.id, "👮 /addadmin id\n/removeadmin id\n/listadmins")
    elif d == "broadcast":
        safe_send(c.message.chat.id, "📨 Text broadcast:\n/broadcast message")
    elif d == "mediabroadcast":
        safe_send(c.message.chat.id, "🎬 Media broadcast:\nKisi photo/video/file/message ko reply karke command do:\n/mbroadcast")

@bot.message_handler(commands=["addchannel"])
def addchannel(m):
    if not is_admin(m.from_user.id): return
    try:
        ch = m.text.split()[1]
        if ch not in db["channels"]:
            db["channels"].append(ch); save(db)
        bot.reply_to(m, f"✅ Added: {ch}")
    except: bot.reply_to(m, "Use: /addchannel @channel")

@bot.message_handler(commands=["removechannel"])
def removechannel(m):
    if not is_admin(m.from_user.id): return
    try:
        ch = m.text.split()[1]
        if ch in db["channels"]:
            db["channels"].remove(ch); save(db)
        bot.reply_to(m, f"🗑 Removed: {ch}")
    except: bot.reply_to(m, "Use: /removechannel @channel")

@bot.message_handler(commands=["listchannels"])
def listchannels(m):
    if is_admin(m.from_user.id): bot.reply_to(m, "\n".join(db["channels"]) or "No channels.")

@bot.message_handler(commands=["addreward"])
def addreward(m):
    if not is_admin(m.from_user.id): return
    text = m.text.replace("/addreward", "").strip()
    if text:
        db["rewards"].append(text); save(db); bot.reply_to(m, "✅ Reward added.")
    else: bot.reply_to(m, "Use: /addreward reward text/link")

@bot.message_handler(commands=["removereward"])
def removereward(m):
    if not is_admin(m.from_user.id): return
    try:
        db["rewards"].pop(int(m.text.split()[1])-1); save(db); bot.reply_to(m, "🗑 Reward removed.")
    except: bot.reply_to(m, "Use: /removereward 1")

@bot.message_handler(commands=["listrewards"])
def listrewards(m):
    if is_admin(m.from_user.id):
        bot.reply_to(m, "\n".join([f"{i+1}. {r}" for i,r in enumerate(db["rewards"])]) or "No rewards.")

@bot.message_handler(commands=["referon"])
def referon(m):
    if is_admin(m.from_user.id): db["refer"]["on"]=True; save(db); bot.reply_to(m,"✅ Refer ON")

@bot.message_handler(commands=["referoff"])
def referoff(m):
    if is_admin(m.from_user.id): db["refer"]["on"]=False; save(db); bot.reply_to(m,"❌ Refer OFF")

@bot.message_handler(commands=["setrefer"])
def setrefer(m):
    if not is_admin(m.from_user.id): return
    try: db["refer"]["target"]=int(m.text.split()[1]); save(db); bot.reply_to(m,"✅ Refer target set.")
    except: bot.reply_to(m,"Use: /setrefer 2")

@bot.message_handler(commands=["setreferreward"])
def setreferreward(m):
    if not is_admin(m.from_user.id): return
    try: db["refer"]["reward_index"]=int(m.text.split()[1])-1; save(db); bot.reply_to(m,"✅ Refer reward selected.")
    except: bot.reply_to(m,"Use: /setreferreward 1")

@bot.message_handler(commands=["myref"])
def myref(m):
    uid=str(m.from_user.id)
    link=f"https://t.me/{bot.get_me().username}?start={uid}"
    bot.reply_to(m, f"👥 Referrals: {len(db['refer']['refs'].get(uid, []))}/{db['refer']['target']}\n🔗 {link}")

@bot.message_handler(commands=["addad"])
def addad(m):
    if not is_admin(m.from_user.id): return
    text=m.text.replace("/addad","").strip()
    if text: db["ads"]["items"].append(text); save(db); bot.reply_to(m,"✅ Ad added.")
    else: bot.reply_to(m,"Use: /addad ad text/link")

@bot.message_handler(commands=["removead"])
def removead(m):
    if not is_admin(m.from_user.id): return
    try: db["ads"]["items"].pop(int(m.text.split()[1])-1); save(db); bot.reply_to(m,"🗑 Ad removed.")
    except: bot.reply_to(m,"Use: /removead 1")

@bot.message_handler(commands=["listads"])
def listads(m):
    if is_admin(m.from_user.id):
        bot.reply_to(m, "\n".join([f"{i+1}. {a}" for i,a in enumerate(db["ads"]["items"])]) or "No ads.")

@bot.message_handler(commands=["adson"])
def adson(m):
    if is_admin(m.from_user.id): db["ads"]["on"]=True; save(db); bot.reply_to(m,"✅ Ads ON")

@bot.message_handler(commands=["adsoff"])
def adsoff(m):
    if is_admin(m.from_user.id): db["ads"]["on"]=False; save(db); bot.reply_to(m,"❌ Ads OFF")

@bot.message_handler(commands=["setadtime"])
def setadtime(m):
    if not is_admin(m.from_user.id): return
    try: db["ads"]["interval"]=int(m.text.split()[1]); save(db); bot.reply_to(m,"✅ Ad time set.")
    except: bot.reply_to(m,"Use: /setadtime 3600")

@bot.message_handler(commands=["addadtarget"])
def addadtarget(m):
    if not is_admin(m.from_user.id): return
    try:
        t=m.text.split()[1]
        if t not in db["ads"]["targets"]: db["ads"]["targets"].append(t); save(db)
        bot.reply_to(m,f"✅ Target added: {t}")
    except: bot.reply_to(m,"Use: /addadtarget @channel")

@bot.message_handler(commands=["listadtargets"])
def listadtargets(m):
    if is_admin(m.from_user.id): bot.reply_to(m, "\n".join(db["ads"]["targets"]) or "No targets.")

def run_ads():
    if not db["ads"]["on"] or not db["ads"]["items"]: return
    ad=random.choice(db["ads"]["items"])
    for t in db["ads"]["targets"]:
        try: bot.send_message(t, "📢 <b>Sponsored Ad</b>\n\n"+ad)
        except: pass

@bot.message_handler(commands=["runadnow"])
def runadnow(m):
    if is_admin(m.from_user.id): run_ads(); bot.reply_to(m,"✅ Ads sent.")

@bot.message_handler(commands=["addadmin"])
def addadmin(m):
    if not is_admin(m.from_user.id): return
    try:
        uid=int(m.text.split()[1])
        if uid not in db["admins"]: db["admins"].append(uid); save(db)
        bot.reply_to(m,"✅ Admin added.")
    except: bot.reply_to(m,"Use: /addadmin id")

@bot.message_handler(commands=["removeadmin"])
def removeadmin(m):
    if not is_admin(m.from_user.id): return
    try:
        uid=int(m.text.split()[1])
        if uid != ADMIN_ID and uid in db["admins"]: db["admins"].remove(uid); save(db)
        bot.reply_to(m,"🗑 Admin removed.")
    except: bot.reply_to(m,"Use: /removeadmin id")

@bot.message_handler(commands=["listadmins"])
def listadmins(m):
    if is_admin(m.from_user.id): bot.reply_to(m, "\n".join(map(str, db["admins"])))

@bot.message_handler(commands=["broadcast"])
def broadcast(m):
    if not is_admin(m.from_user.id): return
    text=m.text.replace("/broadcast","").strip()
    if not text: return bot.reply_to(m,"Use: /broadcast message")
    ok=0
    for u in db["users"]:
        try: bot.send_message(u,text); ok+=1
        except: pass
    bot.reply_to(m,f"✅ Broadcast sent: {ok}")

@bot.message_handler(commands=["mbroadcast"])
def mbroadcast(m):
    if not is_admin(m.from_user.id): return
    if not m.reply_to_message:
        return bot.reply_to(m, "Kisi media/message ko reply karke /mbroadcast bhejo.")
    ok=0
    for u in db["users"]:
        try:
            bot.copy_message(u, m.chat.id, m.reply_to_message.message_id)
            ok+=1
        except: pass
    bot.reply_to(m, f"✅ Media broadcast sent: {ok}")

@bot.message_handler(content_types=["text","photo","video","document","audio","voice"])
def all_msg(m):
    add_user(m.from_user.id)
    if db["forward"] and not is_admin(m.from_user.id):
        try: bot.forward_message(ADMIN_ID, m.chat.id, m.message_id)
        except: pass

def ad_loop():
    while True:
        time.sleep(int(db["ads"]["interval"]))
        run_ads()

app = Flask(__name__)
@app.route("/")
def home():
    return "Bot running!"

def web():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

def start_polling_forever():
    while True:
        try:
            print("Bot polling started...")
            bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
        except Exception:
            print("Bot crashed, restarting...")
            traceback.print_exc()
            time.sleep(5)

threading.Thread(target=web, daemon=True).start()
threading.Thread(target=ad_loop, daemon=True).start()
start_polling_forever()
