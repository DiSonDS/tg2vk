import json
from kutana import Kutana, load_plugins
from kutana.backends import Vkontakte, Telegram

# Import configuration
with open("configuration.json") as fh:
    config = json.load(fh)

# Create application
app = Kutana()

# Set config
app.config.update(
    {"vk_chat_id": config["vk_chat_id"], "tg_chat_id": config["tg_chat_id"]}
)

# Add manager to application
app.add_backend(Telegram(token=config["tg_token"]))
app.add_backend(Vkontakte(token=config["vk_token"]))

# Load and register plugins
app.add_plugins(load_plugins("plugins/"))

if __name__ == "__main__":
    # Run application
    app.run()
