from classes.bot_handler import BotHandler
from classes.messenger import Messenger


class BaseController:
    messenger: Messenger
    bot_handler: BotHandler

    def __init__(self, messenger: Messenger, bot_handler: BotHandler):
        self.messenger = messenger
        self.bot_handler = bot_handler
