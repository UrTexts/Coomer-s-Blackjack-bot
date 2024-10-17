import discord
from discord.ext import commands, tasks
import os
import json
import random
from datetime import datetime, timedelta

# Replace with your bot's token
TOKEN = ''  # Replace with your actual bot token

# Create intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Initialize the bot with intents
bot = commands.Bot(command_prefix='$', intents=intents)

# Define the path for the balances file
BALANCES_FILE = os.path.join(os.path.dirname(__file__), "balances.json")

# Function to check or create the balances file
def check_balances_file():
    if not os.path.exists(BALANCES_FILE):
        with open(BALANCES_FILE, 'w') as file:
            json.dump({}, file)
        print(f"Created new balances.json file at {BALANCES_FILE}")

# Function to load balances from JSON file
def load_balances():
    check_balances_file()
    try:
        with open(BALANCES_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}

# Function to save balances to JSON file
def save_balances(balances):
    with open(BALANCES_FILE, 'w') as file:
        json.dump(balances, file, indent=4)

# Function to adjust balance
def adjust_balance(user_id, amount):
    balances = load_balances()

    # Initialize user balance if not already present
    if user_id not in balances:
        balances[user_id] = {"balance": 0, "last_reward": None}

    balances[user_id]["balance"] += amount
    save_balances(balances)
    return balances[user_id]["balance"]

# Command to check balance
@bot.command(name='balance')
async def balance(ctx):
    user_id = str(ctx.author.id)
    balances = load_balances()

    if user_id not in balances:
        balances[user_id] = {"balance": 0, "last_reward": None}
        save_balances(balances)

    user_balance = balances[user_id]["balance"]
    await ctx.send(f"{ctx.author.mention}, your current balance is: {user_balance} coins.")

# Command to manually give coins
@bot.command(name='give')
async def give(ctx, user: discord.User, amount: int):
    admin_id = ____  # Replace with your user ID
    if ctx.author.id != admin_id:
        await ctx.send(f"{ctx.author.mention}, you do not have permission to use this command.")
        return

    user_id = str(user.id)
    new_balance = adjust_balance(user_id, amount)
    await ctx.send(f"{ctx.author.mention}, you gave {amount} coins to {user.mention}. Their new balance is: {new_balance} coins.")

# Daily coin distribution task
@tasks.loop(hours=12)
async def give_daily_rewards():
    balances = load_balances()
    now = datetime.now()

    for user_id, data in balances.items():
        last_reward = data.get("last_reward")

        # If the user has never received a reward, or it's been 12+ hours
        if last_reward is None or now - datetime.fromisoformat(last_reward) >= timedelta(hours=12):
            balances[user_id]["balance"] += 50
            balances[user_id]["last_reward"] = now.isoformat()

    save_balances(balances)
    print("50 coins given to all users.")

# Start the background task when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    give_daily_rewards.start()  # Start the task

# Blackjack command with betting system
@bot.command(name='blackjack')
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
    new_balance = adjust_balance(user_id, -bet)

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
        new_balance = adjust_balance(user_id, winnings)  # Add winnings to user's balance
        await ctx.send(f"{ctx.author.mention}, you win! You gained {winnings} coins. Your new balance is: {new_balance} coins.")
    elif player_value < dealer_value:
        await ctx.send(f"{ctx.author.mention}, dealer wins! You lost {bet} coins. Your balance is now: {new_balance} coins.")
    else:
        # Refund the bet in case of a tie
        new_balance = adjust_balance(user_id, bet)
        await ctx.send(f"{ctx.author.mention}, it's a tie! Your bet has been refunded. Your balance is now: {new_balance} coins.")

# Leaderboard command
@bot.command(name='leaderboard')
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
@bot.command(name='terms')
async def terms(ctx):
    terms_text = (
        "By using this bot, you agree to the following terms:\n"
        "1. Be respectful to others in the server.\n"
        "2. Do not use the bot for spamming or misuse of commands.\n"
        "3. The bot is not responsible for any losses incurred during games."
    )
    await ctx.send(terms_text)

# Privacy command
@bot.command(name='privacy')
async def privacy(ctx):
    privacy_text = (
        "Your privacy is important to us. We do not collect any personal data from users."
    )
    await ctx.send(privacy_text)

# Run the bot
bot.run(TOKEN)
