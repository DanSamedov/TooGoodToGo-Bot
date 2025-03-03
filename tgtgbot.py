import os
import logging
from dotenv import load_dotenv
from tgtg import TgtgClient
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import urllib.parse

# Load environment variables from .env file
load_dotenv()

# Get API credentials from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
COOKIE = os.getenv("COOKIE")

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Define keyboard
reply_keyboard = [["Subscription"]]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

# Initialize variables
subscribed_users = []
availableness = 0
cafelist = []

# Load subscribed users from file
try:
    with open("userslist_tgtg.txt", "r") as file:
        for line in file:
            words = line.split()
            for word in words:
                if word not in subscribed_users:
                    subscribed_users.append(int(word))
except FileNotFoundError:
    logger.warning("userslist_tgtg.txt not found. Creating a new one on first subscription.")

# Initialize TGTG client
client = TgtgClient(
    access_token=ACCESS_TOKEN,
    refresh_token=REFRESH_TOKEN,
    cookie=COOKIE,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Use command /help to get help",
        reply_markup=markup,
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help") 

async def subscription(context: ContextTypes.DEFAULT_TYPE) -> None:
    global availableness
    try:
        items = client.get_items(
            favorites_only=True,
            latitude=51.941248,
            longitude=15.504714,
            radius=10,
        )
    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        return

    temp_availableness = availableness
    for i in items:
        try:
            store_name = i["store"]["store_name"]
            item_id = i["item"]["item_id"]
            full_price = i["item"]["item_value"]["minor_units"] / 100
            disc_price = i["item"]["item_price"]["minor_units"] / 100
            availableness = i["items_available"]
            photo = i["item"]["logo_picture"]["current_url"]
            address = i["store"]["store_location"]["address"]["address_line"]
            
            encoded_address = urllib.parse.quote(address)

            text = (f"New surprise bag from <a href=\"https://www.google.com/maps?q={encoded_address}\">{store_name}</a>!\n"
                    f"The full price was {full_price}, now it's {disc_price}.\n"
                    f"There are {availableness} bags available now\n")
            
            if availableness != temp_availableness and item_id not in cafelist:
                cafelist.append(item_id)
                for user_id in subscribed_users:
                    await context.bot.send_photo(user_id, photo, text, parse_mode='HTML')
            elif availableness == temp_availableness and item_id in cafelist:
                cafelist.remove(item_id)
        except KeyError as e:
            logger.warning(f"Unexpected data format: missing key {e}")

async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    global subscribed_users
    
    if chat_id not in subscribed_users:
        subscribed_users.append(chat_id)
        with open("userslist_tgtg.txt", "a") as file:
            file.write(f' {chat_id}')
        await update.message.reply_text('You are subscribed')
    else:
        subscribed_users.remove(chat_id)
        with open("userslist_tgtg.txt", "w") as file:
            file.write(" ".join(map(str, subscribed_users)))
        await update.message.reply_text('You are unsubscribed')

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.job_queue.run_repeating(subscription, 10, name='subscription')
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Regex("Subscription"), users_list))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
