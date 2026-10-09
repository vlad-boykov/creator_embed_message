from datetime import datetime, timezone

import lolka

from .models import EmbedData


def build_embed(data: EmbedData) -> lolka.Embed:
    colour = int(data.color.lstrip("#"), 16) if data.color else 0xE47D3A
    embed = lolka.Embed(colour=colour)

    if data.title.strip():
        embed.title = data.title
    if data.description.strip():
        embed.description = data.description
    if data.url.strip():
        embed.url = data.url.strip()

    if data.author_name.strip():
        embed.set_author(
            name=data.author_name,
            url=data.author_url.strip() or None,
            icon_url=data.author_icon_url.strip() or None,
        )

    if data.image_url.strip():
        embed.set_image(url=data.image_url.strip())
    if data.thumbnail_url.strip():
        embed.set_thumbnail(url=data.thumbnail_url.strip())

    if data.footer_text.strip() or data.footer_icon_url.strip():
        embed.set_footer(
            text=data.footer_text.strip() or None,
            icon_url=data.footer_icon_url.strip() or None,
        )

    if data.timestamp_enabled:
        embed.timestamp = datetime.now(timezone.utc)

    for field in data.fields:
        if field.name.strip() or field.value.strip():
            embed.add_field(
                name=field.name,
                value=field.value,
                inline=field.inline,
            )

    return embed


def is_empty(data: EmbedData) -> bool:
    return not any([
        data.author_name.strip(), data.author_url.strip(), data.author_icon_url.strip(),
        data.title.strip(), data.description.strip(), data.url.strip(),
        data.image_url.strip(), data.thumbnail_url.strip(), data.footer_text.strip(),
        data.footer_icon_url.strip(), data.timestamp_enabled,
        any(f.name.strip() or f.value.strip() for f in data.fields),
    ])
