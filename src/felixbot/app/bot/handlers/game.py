import asyncio
import random

from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from fluentogram import TranslatorRunner
from uuid import uuid4

from felixbot.app.bot.keyboards.inline import (
    get_game_menu_kb,
    get_game_kb,
    GameCallback,
)
from felixbot.app.infrastructure.db import DbRepo
from felixbot.app.infrastructure.redis import RedisRepo

router = Router()


class GameSG(StatesGroup):
    start = State()
    game = State()


@router.message(Command("game"), StateFilter(None))
async def cmd_game(msg: Message, state: FSMContext, i18n: TranslatorRunner):
    await state.set_state(GameSG.start)
    await msg.answer(
        i18n.game.menu(),
        reply_markup=get_game_menu_kb(i18n.start.button(), i18n.cancel.button()),
    )


@router.callback_query(F.data == "start", GameSG.start)
async def cb_start(
    cb: CallbackQuery, state: FSMContext, redis_repo: RedisRepo, i18n: TranslatorRunner
):
    await cb.answer()

    await state.set_state(GameSG.game)

    game_id = str(uuid4())
    win_key = random.randint(0, 24)

    game_data = {
        "game_id": game_id,
        "win_key": win_key,
        "moves_left": 10,
        "is_processing": False,
    }

    await redis_repo.save_game(cb.from_user.id, game_data)

    await cb.message.edit_text(
        i18n.get("moves-left", moves=game_data["moves_left"]),
        reply_markup=get_game_kb(game_id),
    )


@router.callback_query(GameCallback.filter(), GameSG.game)
async def cb_clicked(
    cb: CallbackQuery,
    callback_data: GameCallback,
    state: FSMContext,
    redis_repo: RedisRepo,
    db_repo: DbRepo,
    i18n: TranslatorRunner,
):
    tg_id = cb.from_user.id

    game_data = await redis_repo.get_game(tg_id)
    if not game_data:
        await state.clear()
        await cb.message.edit_text(i18n.game.expired())
        return

    if callback_data.game_id != game_data["game_id"]:
        await cb.message.edit_text(i18n.game.expired())
        return

    if game_data["is_processing"]:
        await cb.answer()
        return

    game_data["is_processing"] = True
    await redis_repo.save_game(tg_id, game_data)

    index = callback_data.index
    row = index // 5
    col = index % 5

    kb = cb.message.reply_markup

    if kb.inline_keyboard[row][col].text != "🌊":
        game_data["is_processing"] = False
        await redis_repo.save_game(tg_id, game_data)
        await cb.answer(i18n.already.clicked())
        return

    if index == game_data["win_key"]:
        kb.inline_keyboard[row][col].text = "🐠"

        await cb.answer()
        await cb.message.edit_text(i18n.show.win.cell(), reply_markup=kb)

        await asyncio.sleep(1)

        await cb.message.delete()
        await cb.message.answer(i18n.win())

        await redis_repo.delete_game(tg_id)
        await state.clear()


        await db_repo.add_game(tg_id, ended_at=datetime.now(tz=ZoneInfo('Europe/Moscow')), is_win=True)
        await db_repo.increment_user_wins(tg_id)
        return

    if game_data["moves_left"] == 1:
        win_index = game_data["win_key"]
        win_row = win_index // 5
        win_col = win_index % 5

        kb.inline_keyboard[row][col].text = "❌"

        kb.inline_keyboard[win_row][win_col].text = "🐠"

        await cb.answer()
        await cb.message.edit_text(i18n.show.win.cell(), reply_markup=kb)

        await asyncio.sleep(1)

        await cb.message.delete()
        await cb.message.answer(i18n.lose())

        await redis_repo.delete_game(tg_id)
        await state.clear()

        await db_repo.add_game(tg_id, ended_at=datetime.now(tz=ZoneInfo('Europe/Moscow')), is_win=False)
        await db_repo.increment_user_defeats(tg_id)
        return

    kb.inline_keyboard[row][col].text = "❌"
    game_data["moves_left"] -= 1

    await cb.answer()
    await cb.message.edit_text(
        i18n.moves.left(moves=game_data["moves_left"]), reply_markup=kb
    )

    game_data["is_processing"] = False
    await redis_repo.save_game(tg_id, game_data)


@router.callback_query(GameCallback.filter())
async def cb_any_game_callback(
    cb: CallbackQuery,
    callback_data: GameCallback,
    redis_repo: RedisRepo,
    i18n: TranslatorRunner,
):
    tg_id = cb.from_user.id
    game_data = await redis_repo.get_game(tg_id)

    if (not game_data) or callback_data.game_id != game_data["game_id"]:
        await cb.message.edit_text(i18n.game.expired())

    await cb.answer()


@router.callback_query(F.data == "cancel", GameSG.start)
async def cb_cancel(cb: CallbackQuery, state: FSMContext, i18n: TranslatorRunner):
    await cb.answer()
    await state.clear()
    await cb.message.edit_text(i18n.cancel.game())


@router.message(Command("stop"), ~StateFilter(GameSG.start))
async def cmd_stop(msg: Message, state: FSMContext, redis_repo: RedisRepo, i18n: TranslatorRunner):
    tg_id = msg.from_user.id

    if not await redis_repo.exists(tg_id):
        await msg.reply(i18n.no.active.game())
        return

    await state.clear()
    await redis_repo.delete_game(tg_id)
    await msg.answer(i18n.stop())


@router.message(GameSG.start)
@router.message(GameSG.game)
async def process_in_game(msg: Message):
    await msg.delete()
