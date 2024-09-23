import discord
from discord.ext import commands
import random

# Replace with your bot's token
TOKEN = 'YOUR_BOT_TOKEN_HERE'

# Create intents
intents = discord.Intents.default()
intents.messages = True  # Enable message intents
intents.guilds = True    # Enable guild-related events

# Initialize the bot with intents
bot = commands.Bot(command_prefix='$', intents=intents)

# Define card values
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

# Dictionary to keep track of win streaks
win_streaks = {}

# Function to calculate hand value
def calculate_hand_value(hand):
    value = sum(card_values[card] for card in hand)
    # Adjust for Aces
    aces = hand.count('A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

# Blackjack command
@bot.command()
async def blackjack(ctx):
    player_id = ctx.author.id
    # Initialize win streak if not present
    if player_id not in win_streaks:
        win_streaks[player_id] = {'streak': 0}

    # Initial hands
    player_hand = random.sample(list(card_values.keys()), 2)
    dealer_hand = random.sample(list(card_values.keys()), 2)

    await ctx.send(f"Your hand: {player_hand} (Value: {calculate_hand_value(player_hand)})")
    await ctx.send(f"Dealer's hand: {dealer_hand[0]} and [Hidden]")

    # Player's turn
    while True:
        await ctx.send("Do you want to hit or stand? (Type 'hit' or 'stand')")
        msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg.content.lower() == 'hit':
            player_hand.append(random.choice(list(card_values.keys())))
            player_value = calculate_hand_value(player_hand)
            await ctx.send(f"Your hand: {player_hand} (Value: {player_value})")

            if player_value > 21:
                await ctx.send("You busted! Dealer wins.")
                win_streaks[player_id]['streak'] = 0  # Reset win streak
                return
        elif msg.content.lower() == 'stand':
            break

    # Dealer's turn
    dealer_value = calculate_hand_value(dealer_hand)
    while dealer_value < 17:
        dealer_hand.append(random.choice(list(card_values.keys())))
        dealer_value = calculate_hand_value(dealer_hand)

    await ctx.send(f"Dealer's hand: {dealer_hand} (Value: {dealer_value})")

    # Determine winner
    if dealer_value > 21:
        await ctx.send("Dealer busted! You win!")
        win_streaks[player_id]['streak'] += 1  # Increment win streak
    elif player_value > dealer_value:
        await ctx.send("You win!")
        win_streaks[player_id]['streak'] += 1  # Increment win streak
    elif player_value < dealer_value:
        await ctx.send("Dealer wins.")
        win_streaks[player_id]['streak'] = 0  # Reset win streak
    else:
        await ctx.send("It's a tie!")  # Win streak does not reset on tie

    # Send current win streak
    await ctx.send(f"Your current win streak: {win_streaks[player_id]['streak']}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

bot.run(TOKEN)

