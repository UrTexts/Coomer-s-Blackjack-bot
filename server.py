import json
from flask import Flask, render_template_string

# Initialize the Flask app
app = Flask(__name__)

# Function to read balances and calculate win percentage from the JSON file
def load_balances():
    with open("balances.json", "r") as f:
        return json.load(f)

def calculate_win_percentage(games_played, wins):
    if games_played == 0:
        return 0
    return (wins / games_played) * 100

# Route for the leaderboard page
@app.route('/')
def leaderboard():
    # Load balances from the JSON file
    balances = load_balances()

    # Create a list to store leaderboard data
    leaderboard_data = []

    # Iterate over balances and calculate win percentage
    for user_id, data in balances.items():
        games_played = data.get("games_played", 0)
        wins = data.get("wins", 0)
        win_percentage = calculate_win_percentage(games_played, wins)
       
        # Append the user data to leaderboard list
        leaderboard_data.append({
            "username": data.get("username", "Unknown"),
            "balance": data.get("balance", 0),
            "win_percentage": round(win_percentage, 2)
        })

    # Sort leaderboard by balance (descending order)
    leaderboard_data.sort(key=lambda x: x["balance"], reverse=True)

    # HTML template for the leaderboard
    leaderboard_html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Leaderboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f9; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #4CAF50; color: white; }
            tr:hover { background-color: #f1f1f1; }
        </style>
    </head>
    <body>
        <h1>Leaderboard</h1>
        <table>
            <tr>
                <th>Username</th>
                <th>Balance</th>
                <th>Win Percentage</th>
            </tr>
            {% for player in leaderboard %}
                <tr>
                    <td>{{ player.username }}</td>
                    <td>{{ player.balance }}</td>
                    <td>{{ player.win_percentage }}%</td>
                </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    '''

    # Render the leaderboard page with the data
    return render_template_string(leaderboard_html, leaderboard=leaderboard_data)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
