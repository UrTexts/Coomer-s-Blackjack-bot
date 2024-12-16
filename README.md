# Coomer's Blackjack Bot

Coomer's Blackjack Bot is a fun and interactive Discord bot designed for gambling with virtual currency! This bot allows users to play blackjack against the bot using a custom in-game currency, with various commands to manage player coins, stats, and gameplay.
# Features

    Blackjack Gameplay: Players can play blackjack against the bot using virtual coins.
    Player Stats: Track user stats, including wins, losses, and coin balances.
    Commands: Several bot commands for interacting with the game and managing user stats.
    Virtual Economy: Players can earn and spend virtual coins within the game.

# Commands
`$give`

 Usage: $give <user> <amount>
 Description: Give a specified amount of coins to another user. (Only available to the bot owner)

`$balance`

 Usage: $balance
 Description: View your current coin balance.

`$blackjack <amount>`

Usage: $bet <amount>
Description: Place a bet to start a game of blackjack. The amount must be within your current balance.

`$leaderboard`

 Usage: $leaderboard
 Description: View the leaderboard of top players based on wins or total coins.

# Installation
Requirements:

    Python 3.8 or higher
    discord.py library
    A Discord bot token

Steps to Install:

 Clone the repository:

`git clone https://github.com/UrTexts/Coomer-s-Blackjack-bot.git`

# Install dependencies:
use pip to install all the impots.

Set up your bot token in the main file:

TOKEN = 'your_discord_bot_token_here'

Run the bot:

`python CoomersGamblingBot.py`

Invite your bot to a server with appropriate permissions (bot must have permission to send messages and read message history).
