from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class FieldData:
    name: str = ""
    value: str = ""
    inline: bool = False
    collapsed: bool = False


@dataclass
class EmbedData:
    author_name: str = ""
    author_url: str = ""
    author_icon_url: str = ""
    title: str = ""
    description: str = ""
    url: str = ""
    color: str = "#E47D3A"
    image_url: str = ""
    thumbnail_url: str = ""
    footer_text: str = ""
    footer_icon_url: str = ""
    timestamp_enabled: bool = False
    fields: list[FieldData] = field(default_factory=list)
    collapsed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EmbedData":
        fields = [FieldData(**f) for f in data.get("fields", [])]
        allowed = {
            "author_name", "author_url", "author_icon_url", "title", "description",
            "url", "color", "image_url", "thumbnail_url", "footer_text", "footer_icon_url",
            "timestamp_enabled", "collapsed"
        }
        values = {k: data.get(k, getattr(cls(), k)) for k in allowed}
        values["fields"] = fields
        return cls(**values)


@dataclass
class DraftState:
    selected_guild_id: str = ""
    selected_channel_id: str = ""
    selected_guild_name: str = ""
    selected_channel_name: str = ""
    embeds: list[EmbedData] = field(default_factory=lambda: [EmbedData()])

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_guild_id": self.selected_guild_id,
            "selected_channel_id": self.selected_channel_id,
            "selected_guild_name": self.selected_guild_name,
            "selected_channel_name": self.selected_channel_name,
            "embeds": [e.to_dict() for e in self.embeds],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DraftState":
        embeds = [EmbedData.from_dict(e) for e in data.get("embeds", [])]
        if len(embeds) > 10:
            embeds = embeds[:10]
        if not embeds:
            embeds = [EmbedData()]
        return cls(
            selected_guild_id=str(data.get("selected_guild_id", "")),
            selected_channel_id=str(data.get("selected_channel_id", "")),
            selected_guild_name=str(data.get("selected_guild_name", "")),
            selected_channel_name=str(data.get("selected_channel_name", "")),
            embeds=embeds,
        )
