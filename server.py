import json
from flask import Flask, render_template_string

# Initialize the Flask app
app = Flask(__name__)

# Function to read balances and calculate win percentage from the JSON file
def load_balances():
    with open('balances.json', 'r') as f:
        data = json.load(f)
    leaderboard = []
    for player_id, player_data in data.items():
        # Safely get 'username', 'balance', 'games_played', and 'wins'
        username = player_data.get("username", "Unknown Player")
        balance = player_data.get("balance", 0)
        games_played = player_data.get("games_played", 0)
        wins = player_data.get("wins", 0)
        
        # Calculate win percentage (avoid division by zero)
        if games_played > 0:
            win_percentage = (wins / games_played) * 100
        else:
            win_percentage = 0

        leaderboard.append({
            "name": username,
            "coins": balance,
            "win_percentage": win_percentage
        })
    
    # Sort leaderboard by coins in descending order for the first leaderboard
    leaderboard_by_coins = sorted(leaderboard, key=lambda x: x["coins"], reverse=True)
    # Sort leaderboard by win percentage in descending order for the second leaderboard
    leaderboard_by_win_percentage = sorted(leaderboard, key=lambda x: x["win_percentage"], reverse=True)
    
    return leaderboard_by_coins, leaderboard_by_win_percentage

# Sample leaderboard data (now loading from balances.json)
leaderboard_by_coins, leaderboard_by_win_percentage = load_balances()

# Your HTML template with both leaderboards
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blackjack Leaderboards</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #2d2d2d;
            color: white;
            padding: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        table, th, td {
            border: 1px solid #444;
        }
        th, td {
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #444;
        }
        tr:nth-child(even) {
            background-color: #3a3a3a;
        }
    </style>
</head>
<body>
    <h1>Blackjack Leaderboards</h1>

    <!-- Leaderboard by Coins -->
    <h2>Leaderboard by Coins</h2>
    <table>
        <thead>
            <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Coins</th>
            </tr>
        </thead>
        <tbody>
            {% for player in leaderboard_by_coins %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ player.name }}</td>
                <td>{{ player.coins }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <!-- Leaderboard by Win Percentage -->
    <h2>Leaderboard by Win Percentage</h2>
    <table>
        <thead>
            <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Win Percentage</th>
            </tr>
        </thead>
        <tbody>
            {% for player in leaderboard_by_win_percentage %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ player.name }}</td>
                <td>{{ player.win_percentage|round(2) }}%</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

@app.route('/')
def index():
    leaderboard_by_coins, leaderboard_by_win_percentage = load_balances()  # Re-load the data every time the page is accessed
    return render_template_string(html_content, leaderboard_by_coins=leaderboard_by_coins, leaderboard_by_win_percentage=leaderboard_by_win_percentage)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
