import discord
from discord.ext import commands
import random

# Replace with your bot's token
TOKEN = 'your_discord_bot_token'

# Create intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Initialize the bot with intents
bot = commands.Bot(command_prefix='$', intents=intents)

# Define card values
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

# Win streak dictionary
win_streaks = {}

# Function to calculate hand value
def calculate_hand_value(hand):
    value = sum(card_values[card] for card in hand)
    aces = hand.count('A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


# Blackjack command
@bot.command()
async def blackjack(ctx):
    player_id = ctx.author.id  # Get the user's ID
    player_hand = random.sample(list(card_values.keys()), 2)
    dealer_hand = random.sample(list(card_values.keys()), 2)

    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)

    await ctx.send(f"{ctx.author.mention}, your hand: {player_hand} (Value: {player_value})")
    await ctx.send(f"Dealer's hand: {dealer_hand[0]} and [Hidden]")

    # Player's turn
    while True:
        await ctx.send(f"{ctx.author.mention}, do you want to hit or stand? (Type 'hit' or 'stand')")
        msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg.content.lower() == 'hit':
            player_hand.append(random.choice(list(card_values.keys())))
            player_value = calculate_hand_value(player_hand)
            await ctx.send(f"{ctx.author.mention}, your hand: {player_hand} (Value: {player_value})")

            if player_value > 21:
                await ctx.send(f"{ctx.author.mention}, you busted! Dealer wins.")
                # Reset win streak
                win_streaks[player_id] = 0
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
        await ctx.send(f"{ctx.author.mention}, dealer busted! You win!")
        # Increment win streak
        win_streaks[player_id] = win_streaks.get(player_id, 0) + 1
    elif player_value > dealer_value:
        await ctx.send(f"{ctx.author.mention}, you win!")
        # Increment win streak
        win_streaks[player_id] = win_streaks.get(player_id, 0) + 1
    elif player_value < dealer_value:
        await ctx.send(f"{ctx.author.mention}, dealer wins!")
        # Reset win streak
        win_streaks[player_id] = 0
    else:
        await ctx.send(f"{ctx.author.mention}, it's a tie!")
        # Do not reset win streak

    # Show win streak
    current_streak = win_streaks.get(player_id, 0)
    await ctx.send(f"{ctx.author.mention}, your current win streak: {current_streak}")

# Terms of Service command
@bot.command()
async def terms(ctx):
    await ctx.send("You can view our Terms of Service here: https://docs.google.com/document/d/1C5Ugwgu7rhKRh613BHeSUem_XH8B5iakSphVNnCBlLs/edit?pli=1")

# Privacy Policy command
@bot.command()
async def privacy(ctx):
    await ctx.send("You can view our Privacy Policy here: https://docs.google.com/document/d/1EaQ8u65wdOtNBRHH79gh0IyEtrPNs_OAbyp7PMo5pZ0/pub")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

bot.run(TOKEN)
