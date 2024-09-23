import discord
from discord.ext import commands
import random
import os

# Replace with your bot's token
# Get the API key from the secret
api_key = os.getenv("DISCORD_BOT_TOKEN")

# Create intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Initialize the bot with intents
bot = commands.Bot(command_prefix='$', intents=intents)

# Define card values
card_values = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'J': 10,
    'Q': 10,
    'K': 10,
    'A': 11
}

# Win streak dictionary
win_streaks = {}

# Function to create a deck of cards
def create_deck():
    deck = []
    for card in card_values.keys():
        for _ in range(4):
            deck.append(card)
    return deck

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
    # Create a standard deck of cards
    deck = create_deck()
    random.shuffle(deck)  # Shuffle the deck

    player_hand = random.sample(deck, 2)  # Deal initial hands
    dealer_hand = random.sample(deck, 2)

    # Remove dealt cards from the deck
    for card in player_hand + dealer_hand:
        deck.remove(card)

    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)

    await ctx.send(
        f"{ctx.author.mention}, your hand: {player_hand} (Value: {player_value})"
    )
    await ctx.send(f"Dealer's hand: {dealer_hand[0]} and [Hidden]")

    # Player's turn
    while True:
        await ctx.send(
            f"{ctx.author.mention}, do you want to hit or stand? (Type 'hit' or 'stand')"
        )
        msg = await bot.wait_for(
            'message', check=lambda message: message.author == ctx.author)

        if msg.content.lower() == 'hit':
            if len(deck) > 0:  # Ensure there are cards left in the deck
                player_hand.append(random.choice(deck))
                deck.remove(player_hand[-1])  # Remove the card from the deck
                player_value = calculate_hand_value(player_hand)
                await ctx.send(
                    f"{ctx.author.mention}, your hand: {player_hand} (Value: {player_value})"
                )

                if player_value > 21:
                    await ctx.send(
                        f"{ctx.author.mention}, you busted! Dealer wins.")
                    # Reset win streak
                    win_streaks[player_id] = 0
                    return
            else:
                await ctx.send(
                    f"{ctx.author.mention}, there are no more cards in the deck! The game ends here.")
                return
        elif msg.content.lower() == 'stand':
            break

    # Dealer's turn
    dealer_value = calculate_hand_value(dealer_hand)
    while dealer_value < 17:
        if len(deck) > 0:  # Ensure there are cards left in the deck
            dealer_hand.append(random.choice(deck))
            deck.remove(dealer_hand[-1])  # Remove the card from the deck
            dealer_value = calculate_hand_value(dealer_hand)
        else:
            await ctx.send(
                f"{ctx.author.mention}, there are no more cards in the deck! The game ends here.")
            return

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
    await ctx.send(
        f"{ctx.author.mention}, your current win streak: {current_streak}")

# Terms of Service command
@bot.command()
async def terms(ctx):
    await ctx.send(
        "You can view our Terms of Service here: https://docs.google.com/document/d/1C5Ugwgu7rhKRh613BHeSUem_XH8B5iakSphVNnCBlLs/pub"
    )

# Privacy Policy command
@bot.command()
async def privacy(ctx):
    await ctx.send(
        "You can view our Privacy Policy here: https://docs.google.com/document/d/1EaQ8u65wdOtNBRHH79gh0IyEtrPNs_OAbyp7PMo5pZ0/pub"
    )

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

import os
...
bot.run(os.getenv("DISCORD_BOT_TOKEN"))