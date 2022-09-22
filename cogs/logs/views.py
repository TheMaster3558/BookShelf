from __future__ import annotations

import dataclasses
from typing import Iterable
import discord

event_names: tuple[tuple[str, ...], ...] = (
    (
        'Channel Create',  # on_guild_channel_create
        'Channel Delete',  # on_guild_channel_delete
        'Channel Update',  # on_guild_channel_update
        'Channel Pins Update'  # on_guild_channel_pins_update
    ),
    (
        'Server Update',  # on_guild_update
        'Server Emojis Update',  # on_guild_emojis_update
        'Server Stickers Update'  # on_guild_stickers_update
    ),
    (
        'Invite Create',  # on_invite_create
        'Invite Delete',  # on_invite_delete
        'Integration Update'  # on_guild_integrations_update
    ),
    (
        'Member Join',  # on_raw_member_join
        'Member Leave',  # on_raw_member_remove + audit log query
        'Member Update'  # on_member_update + on_user_update
    ),
    (
        'Kick',  # on_raw_member_remove + audit log query
        'Ban',  # on_member_ban
        'Unban',  # on_member_unban,
        'Prunes'  # on_raw_member_remove + audit log query
    ),
    (
        'Message Edit',  # on_raw_message_edit
        'Message Delete'  # on_raw_message_delete
    ),
    (
        'Reaction Clear',  # on_raw_reaction_clear
        'Reaction Clear Emoji'  # on_raw_reaction_clear_emoji
    ),
    (
        'Role Create',  # on_guild_role_create
        'Role Delete',  # on_guild_role_delete
        'Role Update'  # on_guild_role_update
    ),
    (
        'Thread Create',  # on_thread_create
        'Thread Update',  # on_raw_thread_update
        'Thread Remove',  # on_thread_remove
        'Thread Delete'  # on_raw_raw_thread_delete
    ),
    (
        'Member Voice State Update',  # on_voice_state_update
    )
)


class EventButton(discord.ui.Button['EventTogglerView']):
    def __init__(self, name: str, row: int):
        super().__init__(
            label=name,
            custom_id=name.replace(' ', '_'),
            style=discord.ButtonStyle.green,
            row=row
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        self.style = discord.ButtonStyle.red
        await interaction.message.edit(view=self.view)
        self.view.manager.enabled[self.label] = not (self.view.manager.enabled.get(self.label, True))


class EventTogglerView(discord.ui.View):
    def __init__(self, manager: Manager, names: Iterable[tuple[str]]):
        super().__init__(timeout=None)
        self.manager = manager

        for number, more_names in enumerate(names):
            for name in more_names:
                self.add_item(EventButton(name, row=number))


def get_views() -> tuple[Manager, list[EventTogglerView]]:
    manager = Manager({})
    first = event_names[:4]
    second = event_names[4:8]
    third = event_names[8:]
    return (manager,
            [
                EventTogglerView(manager, first),
                EventTogglerView(manager, second),
                EventTogglerView(manager, third)
            ]
    )


@dataclasses.dataclass
class Manager:
    enabled: dict[str, bool]
