from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class GameCallback(CallbackData, prefix="game"):
    game_id: str
    index: int


class MyGamesCallback(CallbackData, prefix="mygames"):
    page: int


def get_game_menu_kb(start_text: str, cancel_text: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=start_text, callback_data="start")],
            [InlineKeyboardButton(text=cancel_text, callback_data="cancel")],
        ]
    )


def get_game_kb(game_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for i in range(25):
        kb.button(
            text="🌊", callback_data=GameCallback(game_id=game_id, index=i).pack()
        )

    return kb.adjust(5).as_markup()


def get_my_games_kb(page: int, total_pages: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if page > 0:
        kb.button(text="⬅️", callback_data=MyGamesCallback(page=page - 1).pack())

    if page < total_pages - 1:
        kb.button(text="➡️", callback_data=MyGamesCallback(page=page + 1).pack())

    return kb.adjust(2).as_markup()
