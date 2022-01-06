import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import json
import os
import requests
from bs4 import BeautifulSoup


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!, 我們目前可用指令有:start、clear、news、check、city，輸入其他東西則會學你說話喔',
    )

def clear(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /clear is issued."""
    update.message.reply_text('🔥')

def goodmorning(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /clear is issued."""
    update.message.reply_text('Good morning MotherFucker')
    

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def news(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /news is issued."""
    url = "https://www.cdc.gov.tw/Bulletin/List/MmgtpeidAR5Ooai4-fgHzQ"
    html = requests.get(url)
    sp = BeautifulSoup(html.text, 'html5lib')
    boxes = sp.find_all(attrs={"class": "content-boxes-v3"})
    output = ''
    site_domain = 'https://www.cdc.gov.tw'
    for box in boxes:
        links = box.find_all('a')
        for link in links:
            if link.get('title'):
                output += site_domain + link.get('href') + '\n\n'
    update.message.reply_text(output)

def check(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /check is issued."""
    url = 'https://covid19dashboard.cdc.gov.tw/dash3'
    html = requests.get(url)
    sp = BeautifulSoup(html.text, 'html5lib')
    site_json = json.loads(sp.text)
    context = ''
    keys = list(site_json['0'].keys())
    values = list(site_json['0'].values())
    for i in range(len(keys)):
        context += str(keys[i])+str(values[i])+'\n'
    update.message.reply_text(context)

def city(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /locale is issued."""
    return_str = ""
    date, data = get_locale_infected()
    return_str += "更新日期: {} \n".format(date)
    for location, number in data:
        total = number[0]
        new_cases = 0
        if len(number) > 1:
                new_cases = number[1]
        return_str += "{}: 累積確診人數:{},\t本日新增人數: {}\n".format(location, total, new_cases)
    update.message.reply_text(return_str)

#取得各地區資料
def get_locale_infected():
        url = "https://covid-19.nchc.org.tw/dt_005-covidTable_taiwan.php"
        html = requests.get(url, verify=False)
        sp = BeautifulSoup(html.text, 'html5lib')
        date = sp.find(attrs={"class": "col-lg-4 col-sm-6 text-center my-5"}).text
        date = date.replace("\n", "")
        date = date.replace("\t", "")
        boxes = sp.find_all(attrs={"class": "col-lg-12 main"})
        links = boxes[1].find_all('a')
        data = []
        for link in links:
                span = link.find("span")
                text = span.text
                location, numbers = text.split(" ")
                numbers = numbers.split("+")
                numbers[-1] = "".join(numbers[-1].split())  # 去除\xa0
                data.append([location, numbers])
        return [date, data] 


"""Start the bot."""
# Create the Updater and pass it your bot's token.
updater = Updater("1678597485:AAHc4zLsO0c4FEMUh2w4mcqSfYTRiaj0kJQ")

# Get the dispatcher to register handlers
dispatcher = updater.dispatcher

# on different commands - answer in Telegram
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("goodmorning", goodmorning))
dispatcher.add_handler(CommandHandler("clear", clear))
dispatcher.add_handler(CommandHandler("news", news))
dispatcher.add_handler(CommandHandler("check", check))
dispatcher.add_handler(CommandHandler("city", city))

# on non command i.e message - echo the message on Telegram
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

# Start the Bot
updater.start_polling()

updater.idle(stop_signals=())