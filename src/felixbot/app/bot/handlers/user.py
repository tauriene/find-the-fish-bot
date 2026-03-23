from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from fluentogram import TranslatorRunner

from felixbot.app.bot.keyboards.inline import get_my_games_kb, MyGamesCallback
from felixbot.app.infrastructure.db import DbRepo, Game

router = Router()


@router.message(CommandStart())
async def cmd_start(msg: Message, db_repo: DbRepo, i18n: TranslatorRunner):
    username = msg.from_user.username or msg.from_user.id
    await db_repo.add_user(msg.from_user.id, username)
    await msg.answer(i18n.start())


@router.message(Command("profile"))
async def cmd_profile(msg: Message, db_repo: DbRepo, i18n: TranslatorRunner):
    user = await db_repo.get_user(msg.from_user.id)

    await msg.answer(
        i18n.profile(tg_id=user.tg_id, wins=user.wins, defeats=user.defeats)
    )


@router.message(Command("top"))
async def cmd_stats(msg: Message, db_repo: DbRepo, i18n: TranslatorRunner):
    top_users = await db_repo.get_top_users(limit=3)

    result = f"{i18n.player.top()}\n\n"

    for i, user in enumerate(top_users, start=1):
        result += f"{i}) @{user.tg_username} - {user.wins} {i18n.wins()}\n"

    await msg.answer(result)


def format_game(game: Game, index: int, total: int, i18n):
    result = "🏆" if game.is_win else "❌"

    return (
        f"{i18n.games.title()}: {index + 1} / {total}\n\n"
        f"{i18n.result()}: {result}\n\n"
        f"{i18n.finished.at()}: {game.ended_at.strftime('%d.%m.%Y %H:%M')}"
    )


@router.message(Command("mygames"))
async def cmd_my_games(msg: Message, db_repo: DbRepo, i18n: TranslatorRunner):
    games = await db_repo.get_user_games(msg.from_user.id)

    if not games:
        await msg.answer(i18n.no.games())
        return

    page, total_pages = 0, len(games)
    text = format_game(games[page], page, total_pages, i18n)

    await msg.answer(text, reply_markup=get_my_games_kb(page, total_pages))


@router.callback_query(MyGamesCallback.filter())
async def cb_mygames(
    cb: CallbackQuery,
    callback_data: MyGamesCallback,
    db_repo: DbRepo,
    i18n: TranslatorRunner,
):
    games = await db_repo.get_user_games(cb.from_user.id)

    if not games:
        await cb.answer(i18n.no.games(), show_alert=True)
        return

    page = callback_data.page
    total_pages = len(games)

    if page < 0 or page >= total_pages:
        await cb.answer()
        return

    msg_text = format_game(games[page], page, total_pages, i18n)

    await cb.answer()
    await cb.message.edit_text(
        msg_text, reply_markup=get_my_games_kb(page, total_pages)
    )
