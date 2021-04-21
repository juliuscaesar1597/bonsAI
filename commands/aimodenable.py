from commands.base_command  import BaseCommand
from utils                  import get_emoji
from random                 import randint


class moderation(BaseCommand):

    def __init__(self):
        description = "Toggles AI moderation queue on and off"
        params = ["value"]
        super().__init__(description, params)

    async def handle(self, params, message, client):
        try:
            test = bool(params)
        except ValueError:
            await client.send_message(message.channel,
                                      "Please, follow the command with 'true' or 'false' to enable or disable the AI moderation queue")
            return

        def moderationai():
            if test == True:
                return True
            else:
                return False
