import logging
import os
import threading

import pyrogram
from flask import Flask

from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Render health checks require a process listening on $PORT
web = Flask(__name__)


@web.route("/")
def health():
    return "Bot is running", 200


def run_web():
    web.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


threading.Thread(target=run_web, daemon=True).start()

app = pyrogram.Client(
    "mwk",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.APP_ID,
    api_hash=Config.API_HASH,
    plugins=dict(root="modules")
)
app.run()
