import os
import json
import random
import asyncio
import re
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler

# === CONFIGURATION ===
TOKEN = "8180492165:AAFQrauI5Zu-wR2RfgQPRnlBbTSEoHFv-cE"
ADMIN_ID = 6715045621
KEYS_FILE = "keys.json"
DATABASE_FILES = ["logs.txt"]
USED_ACCOUNTS_FILE = "used_accounts.txt"
BANNED_USERS_FILE = "banned_users.txt"
LINES_TO_SEND = 100

# === DOMAIN LIST ===
DOMAINS = [
    "100082", "mlbb", "garena", "roblox", "8ballpool", "paypal", "instagram", "facebook", "youtube", "Netflix", "epicgames", "riotgames", "bank", "crypto", "binance", "telegram", "tiktok", "pornhub", "codashop", "valorant"
]

# === LOAD DATABASE ===
if not os.path.exists(USED_ACCOUNTS_FILE):
    open(USED_ACCOUNTS_FILE, "w").close()

if not os.path.exists(BANNED_USERS_FILE):
    open(BANNED_USERS_FILE, "w").close()

def load_keys():
    return json.load(open(KEYS_FILE, "r", encoding="utf-8")) if os.path.exists(KEYS_FILE) else {"keys": {}, "user_keys": {}, "logs": {}, "banned_users": [], "user_generation_stats": {}}

def save_keys(data):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

keys_data = load_keys()

# === GENERATE KEY SYSTEM ===
def generate_random_key(length=5):
    return "1hs8oh" + ''.join(random.choices("0123456789", k=length))

def get_expiry_time(duration):
    now = datetime.now()
    duration_map = {
        "1m": 60, "3m": 180, "5m": 300, "10m": 600, "20m": 1200, "30m": 1800,
        "1h": 3600, "1d": 86400, "3d": 259200, "5d": 432000, "7d": 604800, "32d": 2764800,
    }
    return None if duration == "lifetime" else (now + timedelta(seconds=duration_map[duration])).timestamp()

# === REMOVE EXPIRED KEYS ===
async def remove_expired_keys():
    while True:
        now = datetime.now().timestamp()
        # Remove expired keys from user_keys
        keys_to_remove = [key for key, expiry in keys_data["user_keys"].items() if expiry is not None and now > expiry]
        for key in keys_to_remove:
            del keys_data["user_keys"][key]
        
        # Remove expired keys from keys
        keys_to_remove = [key for key, expiry in keys_data["keys"].items() if expiry is not None and now > expiry]
        for key in keys_to_remove:
            del keys_data["keys"][key]

        save_keys(keys_data)
        await asyncio.sleep(60)  # Check every minute

# === GENERATE MENU (3 Columns) ===
async def generate_menu(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat_id)
    print(f"Checking if {chat_id} has a key...")  # Debugging line

    if chat_id not in keys_data["user_keys"]:
        print(f"No key found for {chat_id}")  # Debugging line
        return await update.message.reply_text("𝙄𝙉𝙑𝘼𝙇𝙄𝘿 𝙉𝙊 𝙆𝙀𝙔")

    print(f"User {chat_id} has a valid key.")  # Debugging line

    # Split the domains list into chunks of 3
    chunks = [DOMAINS[i:i + 3] for i in range(0, len(DOMAINS), 3)]
    print(f"Domain chunks: {chunks}")  # Debugging line

    # Create keyboard buttons for each chunk
    keyboard = []
    for chunk in chunks:
        row = [InlineKeyboardButton(domain, callback_data=f"generate_{domain}") for domain in chunk]
        keyboard.append(row)

    # Send the message with the inline keyboard
    await update.message.reply_text("*𝙥𝙞𝙘𝙠 𝙣𝙤𝙬 𝙩𝙤 𝙜𝙚𝙣𝙚𝙧𝙖𝙩𝙚 𝙩𝙭𝙩!:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# === FAST TXT GENERATION (2 SECONDS) ===
async def generate_filtered_accounts(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    chat_id, selected_domain = str(query.message.chat_id), query.data.replace("generate_", "")

    if chat_id not in keys_data["user_keys"]:
        return await query.message.reply_text("𝙄𝙉𝙑𝘼𝙇𝙄𝘿 𝙉𝙊 𝙆𝙀𝙔")

    processing_msg = await query.message.reply_text("𝘽𝙊𝙏 𝙄𝙎 𝙂𝙀𝙉𝙀𝙍𝘼𝙏𝙄𝙉𝙂 𝙋𝙇𝙎 𝙒𝘼𝙄𝙏.")

    # Load used accounts
    try:
        with open(USED_ACCOUNTS_FILE, "r", encoding="utf-8", errors="ignore") as f:
            used_accounts = set(f.read().splitlines())
    except:
        used_accounts = set()

    # Find matching lines FAST
    matched_lines = []
    for db_file in DATABASE_FILES:
        if len(matched_lines) >= LINES_TO_SEND:
            break
        try:
            with open(db_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    stripped_line = line.strip()
                    if selected_domain in stripped_line and stripped_line not in used_accounts:
                        matched_lines.append(stripped_line)
                        if len(matched_lines) >= LINES_TO_SEND:
                            break
        except:
            continue

    if not matched_lines:
        return await processing_msg.edit_text("❌ **Hoy bat mo inubos Yong txt!!!**", parse_mode="Markdown")

    # Append used accounts
    with open(USED_ACCOUNTS_FILE, "a", encoding="utf-8", errors="ignore") as f:
        f.writelines("\n".join(matched_lines) + "\n")

    filename = f"Pʀᴇᴍɪᴜᴍ_Kɪᴀɴ_{selected_domain}.txt"
    with open(filename, "w", encoding="utf-8", errors="ignore") as f:
        f.write(f"𝙂𝙀𝙉𝙀𝙍𝘼𝙏𝙊𝙍 𝘽𝙔 𝘿𝙊𝙎\n📅 𝘿𝘼𝙏𝙀 𝙡 𝙏𝙄𝙈𝙀: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n🔍 Domain: {selected_domain}\n\n")
        f.writelines("\n".join(matched_lines))

    await asyncio.sleep(2)  # ✅ Strict 2-second delay

    await processing_msg.delete()
    try:
        with open(filename, "rb") as f:
            await query.message.reply_document(document=InputFile(f, filename=filename), caption=f"𝙋𝙍𝙀𝙈𝙄𝙐𝙈 `{selected_domain}` Generated!**", parse_mode="Markdown")
    except Exception as e:
        return await query.message.reply_text(f" 𝙀𝙍𝙍𝙊𝙍 𝙎𝙀𝙉𝘿𝙄𝙉𝙂 𝙁𝙄𝙇𝙀𝙎: {str(e)}")

    os.remove(filename)

    # Track generation stats for the user
    if chat_id not in keys_data["user_generation_stats"]:
        keys_data["user_generation_stats"][chat_id] = {}

    if selected_domain not in keys_data["user_generation_stats"][chat_id]:
        keys_data["user_generation_stats"][chat_id][selected_domain] = 0

    keys_data["user_generation_stats"][chat_id][selected_domain] += len(matched_lines)

    save_keys(keys_data)
    
# === STATS COMMAND ===
async def stats_command(update: Update, context: CallbackContext):
    if update.message.chat_id != ADMIN_ID:
        return await update.message.reply_text("𝙔𝙊𝙐𝙍 𝙉𝙊𝙏 𝘼𝘿𝙈𝙄𝙉 ;-;")

    total_keys_generated = len(keys_data["keys"])
    total_keys_redeemed = len(keys_data["user_keys"])
    active_users = len(keys_data["user_keys"])

    expired_keys_count = 0
    current_time = datetime.now().timestamp()

    # Count expired keys
    for key, expiry in keys_data["keys"].items():
        if expiry is not None and current_time > expiry:
            expired_keys_count += 1

    # Prepare the stats message
    stats_text = f"""
     **𝘽𝙊𝙏 𝙎𝙏𝘼𝙏𝙎:**

    **𝙏𝙊𝙏𝘼𝙇 𝙆𝙀𝙔𝙎 𝙂𝙀𝙉𝙀𝙍𝘼𝙏𝙀𝘿**: `{total_keys_generated}`
    **𝙏𝙊𝙏𝘼𝙇 𝙆𝙀𝙔𝙎 𝙍𝙀𝘿𝙀𝙀𝙈𝙀𝘿**: `{total_keys_redeemed}`
    **𝘼𝘾𝙏𝙄𝙑𝙀 𝙐𝙎𝙀𝙍𝙎**: `{active_users}`
    **𝙀𝙓𝙋𝙄𝙍𝙀𝘿 𝙆𝙀𝙔𝙎**: `{expired_keys_count}`

    **𝘾𝙐𝙍𝙍𝙀𝙉𝙏 𝙏𝙄𝙈𝙀**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    **𝙐𝙎𝙀𝙍 𝙂𝙀𝙉𝙀𝙍𝘼𝙏𝙄𝙊𝙉 Stats:**
    """

    # Include user generation stats
    for user_id, domains in keys_data["user_generation_stats"].items():
        user_info = f"User {user_id}:"
        for domain, count in domains.items():
            user_info += f" `{domain}: {count} account(s)`"
        stats_text += f"\n{user_info}"

    await update.message.reply_text(stats_text, parse_mode="Markdown")
    
# === CLEAR GENERATION HISTORY COMMAND ===
async def clear_generation_history(update: Update, context: CallbackContext):
    if update.message.chat_id != ADMIN_ID:
        return await update.message.reply_text("𝙔𝙊𝙐𝙍 𝙉𝙊𝙏 𝘼𝘿𝙈𝙄𝙉 ;-;")

    # Clear the user generation stats
    keys_data["user_generation_stats"] = {}
    save_keys(keys_data)

    await update.message.reply_text("✅ **Generation history has been cleared!**", parse_mode="Markdown")
    
# === CLEAR USED ACCOUNTS COMMAND ===
async def clear_used_accounts(update: Update, context: CallbackContext):
    if update.message.chat_id != ADMIN_ID:
        return await update.message.reply_text("𝙔𝙊𝙐𝙍 𝙉𝙊𝙏 𝘼𝘿𝙈𝙄𝙅")

    # Clear the used accounts file
    with open(USED_ACCOUNTS_FILE, "w", encoding="utf-8", errors="ignore") as f:
        f.truncate(0)  # This will clear the file

    await update.message.reply_text("✅ **Used accounts list has been cleared!**", parse_mode="Markdown")
    
# === BAN USER COMMAND ===
async def ban_user(update: Update, context: CallbackContext):
    if update.message.chat_id != ADMIN_ID:
        return await update.message.reply_text(" 𝙔𝙊𝙐𝙍 𝙉𝙊𝙏 𝘼𝘿𝙈𝙄𝙉")

    if len(context.args) != 1:
        return await update.message.reply_text("⚠ 𝙐𝙎𝘼𝙂𝙀: `/ban <user_id>`", parse_mode="Markdown")

    user_id = context.args[0]

    # Check if the user is already banned
    with open(BANNED_USERS_FILE, "r", encoding="utf-8", errors="ignore") as f:
        banned_users = set(f.read().splitlines())

    if user_id in banned_users:
        return await update.message.reply_text(f"𝙐𝙎𝙀𝙍 𝙒𝙄𝙏𝙃 𝙄𝘿 `{user_id}` 𝙄𝙎 𝘼𝙇𝙇𝙍𝙀𝘼𝘿𝙔 𝘽𝘼𝙉𝙉𝙀𝘿", parse_mode="Markdown")

    # Add the user ID to the banned users list
    with open(BANNED_USERS_FILE, "a", encoding="utf-8", errors="ignore") as f:
        f.write(user_id + "\n")

    await update.message.reply_text(f" 𝙪𝙨𝙚𝙧 𝙬𝙞𝙩𝙝 𝙞𝙙 `{user_id}` 𝙃𝙖𝙨 𝘽𝙚𝙚𝙣 𝘽𝙖𝙣𝙣𝙚𝙙.", parse_mode="Markdown")

# === UNBAN USER COMMAND ===
async def unban_user(update: Update, context: CallbackContext):
    if update.message.chat_id != ADMIN_ID:
        return await update.message.reply_text("❌ Sino kaba para mag unban? hindi ka admin tang ina ka!")

    if len(context.args) != 1:
        return await update.message.reply_text("⚠ 𝙐𝙎𝘼𝙂𝙀: `/unban <user_id>`", parse_mode="Markdown")

    user_id = context.args[0]

    # Read the banned users file
    try:
        with open(BANNED_USERS_FILE, "r", encoding="utf-8", errors="ignore") as f:
            banned_users = set(f.read().splitlines())
    except FileNotFoundError:
        banned_users = set()

    # If the user is not in the banned list
    if user_id not in banned_users:
        return await update.message.reply_text(f"❌ 𝙪𝙨𝙚𝙧 𝙬𝙞𝙩𝙝 𝙞𝙙 `{user_id}` 𝙄𝙨 𝙉𝙤𝙩 𝘽𝙖𝙣𝙣𝙚𝙙.", parse_mode="Markdown")

    # Remove the user ID from the banned users list
    banned_users.remove(user_id)
    with open(BANNED_USERS_FILE, "w", encoding="utf-8", errors="ignore") as f:
        f.writelines("\n".join(banned_users) + "\n")

    await update.message.reply_text(f"𝙐𝙎𝙀𝙍 𝙒𝙄𝙏𝙃 𝙄𝘿 `{user_id}` 𝙃𝘼𝙎 𝘽𝙀𝙀𝙉 𝘽𝘼𝙉𝙉𝙀𝘿.", parse_mode="Markdown")

# === GENERATE KEY COMMAND ===
async def generate_key(update: Update, context: CallbackContext):
    if update.message.chat_id != ADMIN_ID:
        return await update.message.reply_text(" 𝙔𝙊𝙐𝙍 𝙉𝙊𝙏 𝘼𝙉 𝘼𝘿𝙈𝙄𝙉 𝙏𝙊 𝙂𝙀𝙉𝙀𝙍𝘼𝙏𝙀 𝙆𝙀𝙔")

    if len(context.args) != 1 or context.args[0] not in ["1m", "3m", "5m", "10m", "20m", "30m", "1h", "1d", "3d", "5d", "7d", "32d", "lifetime"]:
        return await update.message.reply_text("⚠ Usage: `/genkey <duration>`\nExample: `/genkey 1h`", parse_mode="Markdown")

    duration = context.args[0]
    new_key = generate_random_key()
    expiry = get_expiry_time(duration)

    keys_data["keys"][new_key] = expiry
    save_keys(keys_data)

    await update.message.reply_text(f"✅ **𝙎𝙐𝘾𝘾𝙀𝙎𝙎𝙁𝙐𝙇𝙇𝙔 𝙂𝙀𝙉𝙀𝙍𝘼𝙏𝙀𝘿 1 𝙠𝙚𝙮**\n🔑 Key: `{new_key}`\n⏳ Expires: `{duration}`", parse_mode="Markdown")

# === REDEEM KEY COMMAND ===
async def redeem_key(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat_id)

    if len(context.args) != 1:
        return await update.message.reply_text("⚠ Usage: `/key <your_key>`", parse_mode="Markdown")

    entered_key = context.args[0]

    if entered_key not in keys_data["keys"]:
        return await update.message.reply_text("𝙔𝙊𝙐𝙍 𝙆𝙀𝙔 𝙄𝙎 𝙒𝙍𝙊𝙉𝙂")

    expiry = keys_data["keys"][entered_key]
    if expiry is not None and datetime.now().timestamp() > expiry:
        del keys_data["keys"][entered_key]
        save_keys(keys_data)
        return await update.message.reply_text("𝙔𝙊𝙐𝙍 𝙆𝙀𝙔 𝙀𝙓𝙋𝙄𝙍𝙀𝘿")

    keys_data["user_keys"][chat_id] = expiry
    del keys_data["keys"][entered_key]
    save_keys(keys_data)

    await update.message.reply_text("𝙔𝙤𝙪 𝘼𝙧𝙚 𝘼𝙘𝙘𝙚𝙨𝙨 𝙉𝙤𝙬 𝘾𝙡𝙞𝙘𝙠 /generate 𝙩𝙤 𝙂𝙀𝙉𝙀𝙍𝘼𝙏𝙀 𝙏𝙓𝙏")

# === EXTEND USER KEY COMMAND ===
async def extend_for_user(update: Update, context: CallbackContext):
    if update.message.chat_id != ADMIN_ID:
        return await update.message.reply_text("𝙔𝙊𝙐𝙍 𝙉𝙊𝙏 𝘼𝙉 𝘼𝘿𝙈𝙄𝙅 𝙏𝙊 𝙀𝙓𝙏𝙀𝙉𝘿 𝙆𝙀𝙔")

    if len(context.args) != 2:
        return await update.message.reply_text("⚠ Usage: `/extendforuser <user_id> <duration>`\nExample: `/extendforuser 123456789 1d`", parse_mode="Markdown")

    try:
        user_id = str(context.args[0])  # Convert to string to match user_keys keys
        duration = context.args[1]
    except:
        return await update.message.reply_text("⚠ 𝙞𝙣𝙫𝙖𝙡𝙞𝙙 𝙖𝙧𝙜𝙪𝙢𝙚𝙣𝙩𝙨. 𝙪𝙨𝙖𝙜𝙚: `/extendforuser <user_id> <duration>`", parse_mode="Markdown")

    # Check if user exists in the user_keys
    if user_id not in keys_data["user_keys"]:
        return await update.message.reply_text(f"𝙐𝙎𝙀𝙍 𝙒𝙄𝙏𝙃 𝙐𝘿 `{user_id}`𝘿𝙤𝙚𝙨 𝙉𝙤𝙩 𝙃𝙖𝙫𝙚 𝘼 𝙍𝙚𝙙𝙚𝙚𝙢𝙚𝙙 𝙆𝙚𝙮", parse_mode="Markdown")

    # Calculate the new expiry time
    expiry = get_expiry_time(duration)
    if expiry is None:
        return await update.message.reply_text("⚠ 𝙞𝙣𝙫𝙖𝙡𝙞𝙙 𝙙𝙪𝙧𝙖𝙩𝙞𝙤𝙣. 𝙥𝙡𝙚𝙖𝙨𝙚 𝙪𝙨𝙚 𝙤𝙣𝙚 𝙤𝙛 𝙩𝙝𝙚 𝙛𝙤𝙡𝙡𝙤𝙬𝙞𝙣𝙜: 1𝙢, 3𝙢, 5𝙢, 10𝙢, 20𝙢, 30𝙢, 1𝙝, 1𝙙, 3𝙙, 5𝙙, 7𝙙, 𝙡𝙞𝙛𝙚𝙩𝙞𝙢𝙚.", parse_mode="Markdown")

    # Update the user's key expiry
    keys_data["user_keys"][user_id] = expiry
    save_keys(keys_data)

    # Notify the admin
    await update.message.reply_text(f"𝙏𝙃𝙀 𝙀𝙓𝙋𝙄𝙍𝘼𝙏𝙄𝙊𝙉 𝙊𝙁 𝙐𝙎𝙀𝙍 `{user_id}`'s 𝙆𝙀𝙔 𝙃𝘼𝙎 𝘽𝙀𝙀𝙉 𝙀𝙓𝙏𝙀𝙉𝘿𝙀𝘿 𝙏𝙊 `{duration}`.", parse_mode="Markdown")

# === VIEW LOGS COMMAND ===
async def view_logs(update: Update, context: CallbackContext):
    if update.message.chat_id != ADMIN_ID:
        return await update.message.reply_text("𝙔𝙊𝙐 𝘼𝙍𝙀 𝙉𝙊𝙏 𝘼𝙐𝙏𝙃𝙊𝙍𝙄𝙕𝙀𝘿 𝙏𝙊 𝙑𝙄𝙀𝙒 𝙇𝙊𝙂𝙎")

    if not keys_data["user_keys"]:
        return await update.message.reply_text("𝙉𝙊 𝙐𝙎𝙀𝙍𝙎 𝙃𝘼𝙑𝙀 𝙍𝙀𝘿𝙀𝙀𝙈𝙀𝘿 𝙔𝙀𝙏.")

    log_text = "📋 **𝙍𝙀𝘿𝙀𝙀𝙈 𝙆𝙀𝙔 𝙇𝙊𝙂:**\n"
    for user, expiry in keys_data["user_keys"].items():
        expiry_text = "Lifetime" if expiry is None else datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')
        log_text += f"👤 `{user}` - ⏳ 𝙀𝙓𝙋𝙄𝙍𝙀𝙎: `{expiry_text}`\n"

    await update.message.reply_text(log_text, parse_mode="Markdown")

# === HELP COMMAND ===
async def help_command(update: Update, context: CallbackContext):
    help_text = """
 **𝘼𝙑𝘼𝙄𝙇𝘼𝘽𝙇𝙀 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎:**

🫵 🧑‍💻 **User Commands:**
- **/generate**: 𝙨𝙝𝙤𝙬 𝙩𝙝𝙚 𝙡𝙞𝙨𝙩 𝙤𝙛 𝙙𝙤𝙢𝙖𝙞𝙣𝙨 𝙩𝙤 𝙜𝙚𝙣𝙚𝙧𝙖𝙩𝙚 𝙖𝙘𝙘𝙤𝙪𝙣𝙩𝙨. 𝙨𝙚𝙡𝙚𝙘𝙩 𝙛𝙧𝙤𝙢 𝙖 𝙡𝙞𝙨𝙩.
- **/key <your_key>**: 𝙧𝙚𝙙𝙚𝙚𝙢 𝙮𝙤𝙪𝙧 𝙠𝙚𝙮 𝙩𝙤 𝙜𝙚𝙩 𝙖𝙘𝙘𝙚𝙨𝙨 𝙩𝙤 𝙙𝙤𝙢𝙖𝙞𝙣 𝙖𝙘𝙘𝙤𝙪𝙣𝙩 𝙜𝙚𝙣𝙚𝙧𝙖𝙩𝙞𝙤𝙣.

 👑 Admin Commands:
- **/genkey <duration>: 𝙜𝙚𝙣𝙚𝙧𝙖𝙩𝙚 𝙖 𝙠𝙚𝙮 𝙬𝙞𝙩𝙝 𝙖 𝙨𝙥𝙚𝙘𝙞𝙛𝙞𝙚𝙙 𝙚𝙭𝙥𝙞𝙧𝙖𝙩𝙞𝙤𝙣 𝙙𝙪𝙧𝙖𝙩𝙞𝙤𝙣 (𝙚.𝙜., 1𝙝, 3𝙙).
- **/logs 𝙫𝙞𝙚𝙬 𝙩𝙝𝙚 𝙡𝙤𝙜𝙨 𝙤𝙛 𝙧𝙚𝙙𝙚𝙚𝙢𝙚𝙙 𝙠𝙚𝙮𝙨.
- **/stats 𝙫𝙞𝙚𝙬 𝙩𝙝𝙚 𝙗𝙤𝙩'𝙨 𝙠𝙚𝙮 𝙪𝙨𝙖𝙜𝙚 𝙨𝙩𝙖𝙩𝙞𝙨𝙩𝙞𝙘𝙨.
- **/extendforuser <user_id> <duration>**: 𝙚𝙭𝙩𝙚𝙣𝙙 𝙩𝙝𝙚 𝙚𝙭𝙥𝙞𝙧𝙖𝙩𝙞𝙤𝙣 𝙤𝙛 𝙖 𝙨𝙥𝙚𝙘𝙞𝙛𝙞𝙘 𝙪𝙨𝙚𝙧'𝙨 𝙠𝙚𝙮.
- **/ban <user_id>: 𝙗𝙖𝙣 𝙖 𝙪𝙨𝙚𝙧 𝙛𝙧𝙤𝙢 𝙪𝙨𝙞𝙣𝙜 𝙩𝙝𝙚 𝙗𝙤𝙩.
- **/unban <user_id>: 𝙪𝙣𝙗𝙖𝙣 𝙖 𝙪𝙨𝙚𝙧 𝙛𝙧𝙤𝙢 𝙪𝙨𝙞𝙣𝙜 𝙩𝙝𝙚 𝙗𝙤𝙩.
- **/clearused 𝙘𝙡𝙚𝙖𝙧 𝙩𝙝𝙚 𝙡𝙞𝙨𝙩 𝙤𝙛 𝙪𝙨𝙚𝙙 𝙖𝙘𝙘𝙤𝙪𝙣𝙩𝙨 (𝙖𝙙𝙢𝙞𝙣-𝙤𝙣𝙡𝙮).
- **/cleargenerationhistory 𝙘𝙡𝙚𝙖𝙧 𝙩𝙝𝙚 𝙜𝙚𝙣𝙚𝙧𝙖𝙩𝙞𝙤𝙣 𝙝𝙞𝙨𝙩𝙤𝙧𝙮 


"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

# === BOT SETUP ===
def main():
    app = Application.builder().token(TOKEN).build()

    # Add the command handlers
    app.add_handler(CommandHandler("generate", generate_menu))
    app.add_handler(CallbackQueryHandler(generate_filtered_accounts, pattern="^generate_"))
    app.add_handler(CommandHandler("genkey", generate_key))
    app.add_handler(CommandHandler("key", redeem_key))
    app.add_handler(CommandHandler("logs", view_logs))
    app.add_handler(CommandHandler("help", help_command))  # Add the /help command handler
    app.add_handler(CommandHandler("extendforuser", extend_for_user))  # Add the /extendforuser command handler

    # Admin commands for banning/unbanning users
    app.add_handler(CommandHandler("ban", ban_user))  # Add /ban command handler
    app.add_handler(CommandHandler("unban", unban_user))  # Add /unban command handler
    
    # Admin command for clearused
    app.add_handler(CommandHandler("clearused", clear_used_accounts))  # Add /clearused command handler

    # Admin command for clearing generation history
    app.add_handler(CommandHandler("cleargenerationhistory", clear_generation_history))  # Add /cleargenerationhistory command handler
    
    # Add the /stats command handler
    app.add_handler(CommandHandler("stats", stats_command))  # Add /stats command handler
   
    # Start the background task to remove expired keys
    asyncio.ensure_future(remove_expired_keys())

    print("𝘽𝙊𝙏 𝙄𝙎 𝙍𝙐𝙉𝙉𝙄𝙉𝙂....")
    app.run_polling()

if __name__ == "__main__":
    main()