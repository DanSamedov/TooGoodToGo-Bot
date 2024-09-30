from tgtg import TgtgClient
import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


reply_keyboard = [
    ["Subscription"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)


subscribed_users = []
availableness = 0
cafelist = []


with open("userslist_tgtg.txt", "r") as file:
    for line in file:
        words = line.split()

        for word in words:
            if word not in subscribed_users:
                subscribed_users.append(int(word))


client = TgtgClient(access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDk5OTMxMzUsImlhdCI6MTcwOTgyMDMzNSwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6InRzU2IyeVFZUmZlc2Q1dzNRbUFNQXc6MDoxIiwic3ViIjoiMTE2Nzc1NjIzIn0.SInxMXQIy49GmCz8Z_C-6uOF69mmh8ce_HtxLUyqJto",
                    refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDEzNTYzMzUsImlhdCI6MTcwOTgyMDMzNSwiaXNzIjoidGd0Z19zb3RlcmlhIiwidCI6IkhoeXdsQ2dzU1ZDWExSMTlCNEZqTlE6MDowIiwic3ViIjoiMTE2Nzc1NjIzIn0.1Wn08UywX61BOIDQlmZmz8rV6d19LXUi7Uo4JHEnt8Q", 
                    user_id="116775623", cookie="datadome=qFIMqCFOombG9jywFCc7g1h3IXzR_FGwvC2f87ZdFPApyb~xRX1YH6IJ17NPOHmXACrY5inC5_PXoBHKwje89xM3_yy85XNjuzteOIgcolkHfg3Pq1B1CNF52wJigchx; Max-Age=5184000; Domain=.apptoogoodtogo.com; Path=/; Secure; SameSite=Lax")


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

    items = client.get_items(
        favorites_only=True,
        latitude=51.941248,
        longitude=15.504714,
        radius=10,
    )

    temp_availableness = availableness

    for i in items:
        store_name = i["store"]["store_name"]
        item_id = i["item"]["item_id"]
        full_price = i["item"]["item_value"]["minor_units"]/100
        disc_price = i["item"]["item_price"]["minor_units"]/100
        availableness = i["items_available"]
        photo = i["item"]["logo_picture"]["current_url"]
        address = i["store"]["store_location"]["address"]["address_line"]

        text = (f"New surprise bag from <a href=\"https://www.google.com/maps?q={address}\">{store_name}</a>!\n"
                f"The full price was {full_price}, now its {disc_price}.\n"
                f"There are {availableness} bags available now\n")
        
        if availableness != temp_availableness and item_id not in cafelist:
            cafelist.append(item_id)
            for i in subscribed_users:
                await context.bot.send_photo(i, photo, text, parse_mode='HTML')
        elif availableness == temp_availableness and item_id in cafelist:
            cafelist.remove(item_id)


async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    global subscribed_users

    if chat_id not in subscribed_users:
            subscribed_users.append(chat_id)
            chat_id_str = str(chat_id)
            with open("userslist_tgtg.txt", "a") as file:
                file.write(' ' + chat_id_str)
            await update.message.reply_text('You are subscribed')   
    else:
        subscribed_users.remove(chat_id)
        subscribed_users_str = " "
        subscribed_users_str = subscribed_users_str.join(str(x) for x in subscribed_users)
        with open("userslist_tgtg.txt", "w") as file:
            file.write(subscribed_users_str)
        await update.message.reply_text('You are unsubscribed')


def main() -> None:
    application = Application.builder().token("6993514315:AAFbzYgIaxahMbdILe2H-T-Q5zV08HRN-FM").build()

    application.job_queue.run_repeating(subscription, 10, name='subscription')

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(filters.Regex("Subscription"), users_list))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()