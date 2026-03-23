# find-the-fish-bot

A bot with a mini-game using an inline keyboard.

## Used tech

- aiogram
- sqlalchemy
- alembic
- fluentogram
- PostgreSQL as database
- Redis as cache
- Docker with docker-compose for deployment

## Commands

- /start - start the bot
- /profile - view the profile
- /game - start the “find the fish” game
- /top - leaderboard of top players
- /stop - stop the current game
- /mygames - view the game history

## Easy start

Clone the repository:
```bash
git clone https://github.com/tauriene/find-the-fish-bot.git
```
---
Go to project folder:
```bash
cd find-the-fish-bot
```
---
Run in terminal:
```bash
docker compose up 
```