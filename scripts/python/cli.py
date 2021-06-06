import logging
import sys
from typing import Optional

import click
from a_protocol_0.enums.CommandEnum import CommandEnum
from commands.activate_rev2_editor import activate_rev2_editor
from commands.reload_ableton import reload_ableton
from commands.search_set import search_set
from commands.sync_presets import sync_presets
from commands.toggle_ableton_button import toggle_ableton_button
from lib.click import click_and_restore_pos, pixel_has_color
from lib.keys import send_keys
from lib.window.find_window import SearchTypeEnum, find_window_handle_by_criteria, show_windows
from lib.window.window import focus_window

logging.basicConfig(
    filename="C:\\Users\\thiba\\OneDrive\\Documents\\protocol0_logs\\cli.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger().addHandler(logging.StreamHandler())


@click.group()
def cli():
    pass


@cli.command(name=CommandEnum.SEND_CLICK.name)
@click.argument("x")
@click.argument("y")
def command_send_click(x: str, y: str) -> None:
    click_and_restore_pos(int(x), int(y))


@cli.command(name=CommandEnum.SEND_KEYS.name)
@click.argument("keys")
def command_send_keys(keys: str) -> None:
    send_keys(keys)


@cli.command(name=CommandEnum.PIXEL_HAS_COLOR.name)
@click.argument("x")
@click.argument("y")
@click.argument("color")
def command_pixel_has_color(x: str, y: str, color: str) -> None:
    res = pixel_has_color(x=int(x), y=int(y), color=color)
    sys.exit(1 if res else 0)


@cli.command(name=CommandEnum.IS_PLUGIN_WINDOW_VISIBLE.name)
@click.argument("name")
def command_is_plugin_window_visible(name: str) -> None:
    res = find_window_handle_by_criteria(class_name="AbletonVstPlugClass", partial_name=name)
    sys.exit(1 if res else 0)


@cli.command(name=CommandEnum.ACTIVATE_REV2_EDITOR.name)
def command_activate_rev2_editor() -> None:
    activate_rev2_editor()


@cli.command(name=CommandEnum.TOGGLE_ABLETON_BUTTON.name)
@click.argument("x")
@click.argument("y")
@click.argument("activate")
def command_toggle_ableton_button(x: str, y: str, activate: str) -> None:
    toggle_ableton_button(x=int(x), y=int(y), activate=bool(int(activate)))


@cli.command(name=CommandEnum.RELOAD_ABLETON.name)
def command_reload_ableton() -> None:
    reload_ableton()


@cli.command(name=CommandEnum.FOCUS_WINDOW.name)
@click.argument("name")
@click.argument("search_type", required=False)
def command_focus_window(name: str, search_type: Optional[str]) -> None:
    search_type_enum = SearchTypeEnum.get_from_value(search_type, SearchTypeEnum.NAME)  # type: SearchTypeEnum
    focus_window(name, search_type_enum)


@cli.command(name=CommandEnum.SEARCH_SET.name)
def command_search_set() -> None:
    search_set()


@cli.command(name=CommandEnum.SYNC_PRESETS.name)
def command_sync_presets() -> None:
    sync_presets()


@cli.command(name="SHOW_WINDOWS")
def command_show_windows() -> None:
    show_windows()


if __name__ == "__main__":
    cli()
