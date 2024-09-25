import discord
from discord.ext import commands
import random
import os
import json
from datetime import datetime, timedelta

# Replace with your bot's token
Token = 'yourtoken'  # Replace with your actual bot token

# Create intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Initialize the bot with intents
bot = commands.Bot(command_prefix='$', intents=intents)

# Define the path for the balances file
BALANCES_FILE = os.path.join(os.path.dirname(__file__), "balances.json")

# Function to load balances from JSON file
def load_balances():
    if not os.path.exists(BALANCES_FILE):
        return {}
    with open(BALANCES_FILE, 'r') as file:
        return json.load(file)

# Function to save balances to JSON file
def save_balances(balances):
    with open(BALANCES_FILE, 'w') as file:
        json.dump(balances, file, indent=4)

# Function to adjust balance
def adjust_balance(user_id, amount):
    balances = load_balances()
    if user_id not in balances:
        balances[user_id] = {"balance": 0, "last_daily": None}
    balances[user_id]["balance"] += amount
    save_balances(balances)
    return balances[user_id]["balance"]

# Balance command
@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    balances = load_balances()

    if user_id not in balances:
        balances[user_id] = {"balance": 0, "last_daily": None}
        save_balances(balances)

    user_balance = balances[user_id]["balance"]
    await ctx.send(f"{ctx.author.mention}, your current balance is: {user_balance} coins.")

# Daily command
@bot.command()
async def daily(ctx):
    user_id = str(ctx.author.id)
    balances = load_balances()

    # Initialize user balance if not already present
    if user_id not in balances:
        balances[user_id] = {"balance": 0, "last_daily": None}
        save_balances(balances)

    last_daily = balances[user_id]["last_daily"]
    now = datetime.now()

    # Check if the user can claim daily reward
    if last_daily is None or now - datetime.fromisoformat(last_daily) >= timedelta(days=1):
        amount = 100  # Amount to give for daily
        adjust_balance(user_id, amount)
        balances[user_id]["last_daily"] = now.isoformat()  # Store last_daily as ISO format string
        save_balances(balances)
        await ctx.send(f"{ctx.author.mention}, you received your daily reward of {amount} coins!")
    else:
        time_left = 24 - (now - datetime.fromisoformat(last_daily)).seconds // 3600
        await ctx.send(f"{ctx.author.mention}, you can claim your daily reward again in {time_left} hours.")

# Blackjack command with betting system
@bot.command()
async def blackjack(ctx, bet: int = None):
    if bet is None:
        await ctx.send(f"{ctx.author.mention}, please provide a bet amount. Usage: `$blackjack <bet>`.")
        return

    user_id = str(ctx.author.id)
    balances = load_balances()

    # Check if the user has enough coins to bet
    if user_id not in balances or balances[user_id]["balance"] < bet:
        await ctx.send(f"{ctx.author.mention}, you don't have enough coins to place this bet!")
        return

    # Deduct the bet amount from the user's balance
    balances[user_id]["balance"] -= bet
    save_balances(balances)

    # Create a standard deck of cards
    def create_deck():
        deck = []
        card_values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        for card in card_values:
            for _ in range(4):
                deck.append(card)
        return deck

    # Calculate hand value
    def calculate_hand_value(hand):
        card_values = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
        }
        value = sum(card_values[card] for card in hand)
        aces = hand.count('A')
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    # Start the game
    deck = create_deck()
    random.shuffle(deck)

    player_hand = random.sample(deck, 2)
    dealer_hand = random.sample(deck, 2)

    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)

    await ctx.send(f"{ctx.author.mention}, your hand: {player_hand} (Value: {player_value})")
    await ctx.send(f"Dealer's hand: {dealer_hand[0]} and [Hidden]")

    # Player's turn
    while True:
        await ctx.send(f"{ctx.author.mention}, do you want to hit or stand? (Type 'hit' or 'stand')")
        msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg.content.lower() == 'hit':
            player_hand.append(deck.pop())
            player_value = calculate_hand_value(player_hand)
            await ctx.send(f"{ctx.author.mention}, your hand: {player_hand} (Value: {player_value})")

            if player_value > 21:
                await ctx.send(f"{ctx.author.mention}, you busted! Dealer wins.")
                return
        elif msg.content.lower() == 'stand':
            break

    # Dealer's turn
    while dealer_value < 17:
        dealer_hand.append(deck.pop())
        dealer_value = calculate_hand_value(dealer_hand)

    await ctx.send(f"Dealer's hand: {dealer_hand} (Value: {dealer_value})")

    # Determine winner
    if dealer_value > 21 or player_value > dealer_value:
        winnings = bet * 2
        balances[user_id]["balance"] += winnings
        save_balances(balances)
        await ctx.send(f"{ctx.author.mention}, you win! You gained {winnings} coins.")
    elif player_value < dealer_value:
        await ctx.send(f"{ctx.author.mention}, dealer wins! You lost {bet} coins.")
    else:
        balances[user_id]["balance"] += bet  # Refund the bet in case of a tie
        save_balances(balances)
        await ctx.send(f"{ctx.author.mention}, it's a tie! Your bet has been refunded.")

    # Save the updated balances after the game ends
    save_balances(balances)

# Admin command to give money
@bot.command()
async def give(ctx, user: discord.User, amount: int):
    admin_id = 1234567890  # Replace with your user ID
    if ctx.author.id != admin_id:
        await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
        return

    user_id = str(user.id)
    balances = load_balances()
    adjust_balance(user_id, amount)
    await ctx.send(f"{ctx.author.mention}, you gave {amount} coins to {user.mention}.")

# Leaderboard command
@bot.command()
async def leaderboard(ctx):
    balances = load_balances()
    sorted_leaderboard = sorted(balances.items(), key=lambda item: item[1]["balance"], reverse=True)

    if len(sorted_leaderboard) == 0:
        await ctx.send("No players found.")
        return

    leaderboard_message = "**Leaderboard**\n\n"
    for i, (user_id, data) in enumerate(sorted_leaderboard[:10], 1):
        user = await bot.fetch_user(user_id)
        leaderboard_message += f"{i}. {user.name} - {data['balance']} coin(s)\n"

    await ctx.send(leaderboard_message)

# Terms command
@bot.command()
async def terms(ctx):
    terms_text = (
        "By using this bot, you agree to the following terms:\n"
        "1. Be respectful to other users.\n"
        "2. No spamming or flooding the chat.\n"
        "3. Follow Discord's community guidelines.\n"
        "4. The bot owner reserves the right to modify these terms at any time."
    )
    await ctx.send(terms_text)

# Privacy command
@bot.command()
async def privacy(ctx):
    privacy_text = (
        "Your privacy is important to us. Here are our privacy policies:\n"
        "1. We do not collect personal information without your consent.\n"
        "2. Any data collected is used solely for the purpose of providing bot services.\n"
        "3. We do not share your information with third parties."
    )
    await ctx.send(privacy_text)


bot.run(Token)
