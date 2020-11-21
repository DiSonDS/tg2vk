import random
from datetime import datetime

import hues
from kutana import Plugin

plugin = Plugin(
    name="Telegram to VK",
    description="Forwards messages from the Telegram chat to the VK chat",
)


def create_message_header(timestamp, raw_update):
    date = datetime.fromtimestamp(timestamp)
    # local_date = utc_to_local(date)
    date_string = date.strftime("%H:%M %d.%m.%y")
    name = raw_update["message"]["from"]["first_name"]
    emoji = "👤"
    return f"{emoji} {name} ({date_string})"


@plugin.on_attachments(
    [
        "image",
        "doc",
        "audio",
        "video",
        "sticker",
        "location",
        "voice",
        "video_note",
        "poll",
    ]
)
async def _(msg, ctx):
    """Handle only telegram messages with attachments."""
    hues.log(f"CID:{msg.receiver_id} UID:{msg.sender_id} ATTACHMENTS:{msg.attachments}")

    if (
        ctx.backend.get_identity() == "telegram"
        and msg.receiver_id == ctx.config["tg_chat_id"]
    ):
        # get vk backend
        vk_backend = ctx.app.get_backends()[1]
        # get vk chat_id
        chat_id = ctx.config["vk_chat_id"]

        msg_raw = msg.raw["message"]
        if msg_raw.get("photo"):
            if msg_raw.get("caption"):
                caption = msg_raw["caption"]
                attach_text = (
                    f'[photo - "{caption}" '
                    f"{msg_raw['photo'][-1]['width']}x{msg_raw['photo'][-1]['height']}]"
                )
            else:
                attach_text = (
                    f"[photo - "
                    f"{msg_raw['photo'][-1]['width']}x{msg_raw['photo'][-1]['height']}]"
                )
        elif msg_raw.get("document"):
            attach_text = f"[doc - \"{msg_raw['document']['file_name']}\"]"
        elif msg_raw.get("sticker"):
            attach_text = f"[sticker - \"{msg_raw['sticker']['emoji']}\"]"
        elif msg_raw.get("location"):
            lat = msg_raw["location"]["latitude"]
            long = msg_raw["location"]["longitude"]
            return await vk_backend.request(
                "messages.send",
                chat_id=chat_id,
                lat=lat,
                long=long,
                random_id=random.randint(1, 99999),
            )
        elif msg_raw.get("voice"):
            attach_text = f"[voice - {msg_raw['voice']['duration']} сек]"
        elif msg_raw.get("video_note"):
            attach_text = f"[video_note - {msg_raw['video_note']['duration']} сек]"
        elif msg_raw.get("poll"):
            attach_text = f"[poll - \"{msg_raw['poll']['question']}\"]"
        else:
            attach_text = "[unsupported attachment type]"

        header = create_message_header(msg.date, msg.raw)
        msg_text = f"{header}\n{attach_text}"

        return await vk_backend.request(
            "messages.send",
            chat_id=chat_id,
            message=msg_text,
            random_id=random.randint(1, 99999),
        )


@plugin.on_any_unprocessed_message()
async def _(msg, ctx):
    """Handle only telegram messages without attachments."""
    hues.log(f"CID:{msg.receiver_id} UID:{msg.sender_id} TEXT:{msg.text}")

    if (
        ctx.backend.get_identity() == "telegram"
        and msg.receiver_id == ctx.config["tg_chat_id"]
    ):
        # get vk backend
        vk_backend = ctx.app.get_backends()[1]
        # get vk chat_id
        chat_id = ctx.config["vk_chat_id"]

        header = create_message_header(msg.date, msg.raw)
        msg_text = f"{header}\n{msg.text}"

        return await vk_backend.request(
            "messages.send",
            chat_id=chat_id,
            message=msg_text,
            random_id=random.randint(1, 99999),
        )


@plugin.on_commands(["get_chat_id"])
async def _(msg, ctx):
    """Return chat_id."""
    return await ctx.reply(msg.receiver_id)
