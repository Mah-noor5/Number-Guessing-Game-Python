import random
import os
import time
import datetime

LEADERBOARD_FILE = "leaderboard.txt"

# Difficulty settings for the game
DIFFICULTY_SETTINGS = {
    "1": {"name": "Easy",   "range": (1, 50),   "max_attempts": 10, "hint_count": 3},
    "2": {"name": "Medium", "range": (1, 100),  "max_attempts": 7,  "hint_count": 2},
    "3": {"name": "Hard",   "range": (1, 200),  "max_attempts": 5,  "hint_count": 1},
    "4": {"name": "Expert", "range": (1, 500),  "max_attempts": 6,  "hint_count": 0},
}


def clear_screen():
    pass


def print_banner():
    print("=" * 55)
    print("       🎯  NUMBER  GUESSING  GAME  🎯")
    print("    Computer Applications in Engineering Design")
    print("=" * 55)


def print_separator():
    print("-" * 55)


# Prints text character by character for animation effect
def slow_print(text, delay=0.03):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()


# Validates integer input from user
def get_valid_integer(prompt, low=None, high=None):
    while True:
        try:
            value = int(input(prompt))

            if low is not None and value < low:
                print(f"  ⚠  Please enter a number >= {low}.")
                continue

            if high is not None and value > high:
                print(f"  ⚠  Please enter a number <= {high}.")
                continue

            return value

        except ValueError:
            print("  ⚠  Invalid input. Please enter a whole number.")


# Validates menu choices (1,2,3,4 etc.)
def get_valid_choice(prompt, valid_choices):
    while True:
        choice = input(prompt).strip()

        if choice in valid_choices:
            return choice

        print(f"  ⚠  Please choose from: {', '.join(valid_choices)}")


# Generates hints based on attempts
def generate_hint(secret, guess, attempt_no, hints_remaining):
    if hints_remaining <= 0:
        return None

    hints = []

    if attempt_no == 1:
        parity = "even" if secret % 2 == 0 else "odd"
        hints.append(f"💡 Hint: The number is {parity}.")

    elif attempt_no == 2:
        if secret % 5 == 0:
            hints.append("💡 Hint: The number is divisible by 5.")
        elif secret % 3 == 0:
            hints.append("💡 Hint: The number is divisible by 3.")
        else:
            hints.append("💡 Hint: The number is NOT divisible by 3 or 5.")

    else:
        diff = abs(secret - guess)

        if diff <= 5:
            hints.append("💡 Hint: You are VERY close (within 5)!")
        elif diff <= 15:
            hints.append("💡 Hint: You are getting warm (within 15).")
        else:
            hints.append("💡 Hint: Still a bit far away.")

    return hints[0] if hints else None


# Calculates player score
def calculate_score(max_attempts, attempts_used, hints_used, difficulty_name):
    difficulty_multiplier = {
        "Easy": 1,
        "Medium": 2,
        "Hard": 3,
        "Expert": 4
    }

    base_score = 1000
    attempt_penalty = attempts_used * 50
    hint_penalty = hints_used * 100

    raw_score = max(0, base_score - attempt_penalty - hint_penalty)
    multiplier = difficulty_multiplier.get(difficulty_name, 1)

    final_score = raw_score * multiplier

    return final_score


# Loads leaderboard data from file
def load_leaderboard():
    records = []

    if not os.path.exists(LEADERBOARD_FILE):
        return records

    try:
        with open(LEADERBOARD_FILE, "r") as f:
            for line in f:
                line = line.strip()

                if line:
                    parts = line.split("|")

                    if len(parts) == 4:
                        records.append({
                            "name": parts[0],
                            "score": int(parts[1]),
                            "difficulty": parts[2],
                            "date": parts[3],
                        })

    except (IOError, ValueError) as e:
        print(f"  ⚠  Could not load leaderboard: {e}")

    return records


# Saves score to leaderboard file
def save_to_leaderboard(name, score, difficulty):
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    try:
        with open(LEADERBOARD_FILE, "a") as f:
            f.write(f"{name}|{score}|{difficulty}|{date_str}\n")

    except IOError as e:
        print(f"  ⚠  Could not save score: {e}")


def display_leaderboard():
    records = load_leaderboard()

    print_separator()
    print("           🏆  LEADERBOARD — TOP 10  🏆")
    print_separator()

    if not records:
        print("  No records yet. Be the first to play!")
        print_separator()
        return

    # Sort scores in descending order
    records.sort(key=lambda r: r["score"], reverse=True)
    top10 = records[:10]

    print(f"  {'Rank':<5} {'Name':<15} {'Score':<8} {'Difficulty':<10} {'Date'}")
    print_separator()

    for rank, r in enumerate(top10, start=1):
        medal = ["🥇", "🥈", "🥉"][rank - 1] if rank <= 3 else f"  {rank}."

        print(
            f"  {medal:<5} {r['name']:<15} "
            f"{r['score']:<8} {r['difficulty']:<10} {r['date']}"
        )

    print_separator()


# Finds player's ranking position
def get_player_rank(score):
    records = load_leaderboard()

    if not records:
        return 1

    records.sort(key=lambda r: r["score"], reverse=True)

    for i, r in enumerate(records):
        if score >= r["score"]:
            return i + 1

    return len(records) + 1


def choose_difficulty():
    print_separator()
    print("  SELECT DIFFICULTY")
    print_separator()

    for key, s in DIFFICULTY_SETTINGS.items():
        lo, hi = s["range"]

        print(
            f"  [{key}]  {s['name']:<8}  Range: {lo}–{hi}"
            f"  Attempts: {s['max_attempts']}  Hints: {s['hint_count']}"
        )

    print_separator()

    choice = get_valid_choice(
        "  Your choice (1/2/3/4): ",
        list(DIFFICULTY_SETTINGS.keys())
    )

    return DIFFICULTY_SETTINGS[choice]


def play_round(player_name, settings):
    lo, hi = settings["range"]
    max_attempts = settings["max_attempts"]
    hints_remaining = settings["hint_count"]
    difficulty_name = settings["name"]

    # Random secret number generated within difficulty range
    secret_number = random.randint(lo, hi)

    attempts_used = 0
    hints_used = 0
    won = False

    clear_screen()
    print_banner()

    print(f"\n  Difficulty : {difficulty_name}")
    print(f"  Range      : {lo}  –  {hi}")
    print(f"  Attempts   : {max_attempts}")
    print(f"  Hints left : {hints_remaining}")

    print_separator()

    slow_print("  I've picked a secret number. Can you find it? 🔍\n")

    while attempts_used < max_attempts:
        remaining = max_attempts - attempts_used

        print(f"  Attempts remaining: {remaining}")

        guess = get_valid_integer(
            f"  Your guess ({lo}–{hi}): ",
            lo,
            hi
        )

        attempts_used += 1

        if guess == secret_number:
            won = True
            break

        elif guess < secret_number:
            print("  📈  Too LOW!")

        else:
            print("  📉  Too HIGH!")

        if hints_remaining > 0 and attempts_used < max_attempts:

            use_hint = get_valid_choice(
                f"  Use a hint? ({hints_remaining} left) [y/n]: ",
                ["y", "n"]
            )

            if use_hint == "y":
                hint_text = generate_hint(
                    secret_number,
                    guess,
                    attempts_used,
                    hints_remaining
                )

                if hint_text:
                    print(f"  {hint_text}")
                    hints_remaining -= 1
                    hints_used += 1

        print()

    print_separator()

    if won:
        score = calculate_score(
            max_attempts,
            attempts_used,
            hints_used,
            difficulty_name
        )

        rank = get_player_rank(score)

        slow_print(f"\n  🎉 CONGRATULATIONS, {player_name}!")

        print(f"  You guessed {secret_number} in {attempts_used} attempt(s).")
        print(f"  Score      : {score} points")
        print(f"  Leaderboard Rank : #{rank}")

        save_to_leaderboard(player_name, score, difficulty_name)

        return score

    else:
        slow_print(f"\n  💀 GAME OVER, {player_name}!")
        print(f"  The secret number was: {secret_number}")
        print("  Better luck next time!")

        return 0


# Displays overall session statistics
def display_session_stats(session_scores):
    print_separator()
    print("           📊  SESSION STATISTICS  📊")
    print_separator()

    rounds_played = len(session_scores)
    rounds_won = sum(1 for s in session_scores if s > 0)

    total_score = sum(session_scores)
    best_score = max(session_scores) if session_scores else 0

    win_rate = (
        rounds_won / rounds_played * 100
        if rounds_played > 0
        else 0
    )

    print(f"  Rounds Played  : {rounds_played}")
    print(f"  Rounds Won     : {rounds_won}")
    print(f"  Win Rate       : {win_rate:.1f}%")
    print(f"  Total Score    : {total_score}")
    print(f"  Best Score     : {best_score}")

    print_separator()


def main_menu():
    print_separator()
    print("  MAIN MENU")
    print_separator()

    print("  [1]  Play Game")
    print("  [2]  View Leaderboard")
    print("  [3]  How to Play")
    print("  [4]  Quit")

    print_separator()

    return get_valid_choice(
        "  Your choice (1/2/3/4): ",
        ["1", "2", "3", "4"]
    )


def how_to_play():
    print_separator()
    print("  📖  HOW TO PLAY")
    print_separator()

    print("  1. Choose a difficulty level.")
    print("  2. A secret number is randomly generated.")
    print("  3. Type your guess and press Enter.")
    print("  4. You will be told if your guess is too HIGH or too LOW.")
    print("  5. Use hints wisely — they cost score points.")
    print("  6. Guess the number before you run out of attempts!")

    print()
    print("  SCORING FORMULA:")
    print("    Score = (1000 - attempts×50 - hints×100) × difficulty_multiplier")
    print("    Multipliers → Easy:1  Medium:2  Hard:3  Expert:4")

    print_separator()

    input("  Press Enter to return to menu...")


def main():
    clear_screen()
    print_banner()

    print()

    slow_print("  Welcome to the Number Guessing Game!")

    print()

    player_name = input("  Enter your name: ").strip()

    if not player_name:
        player_name = "Player"

    # Stores scores of current game session
    session_scores = []

    while True:
        clear_screen()
        print_banner()

        print(f"\n  Welcome, {player_name}! 👋\n")

        choice = main_menu()

        if choice == "1":
            settings = choose_difficulty()

            score = play_round(player_name, settings)

            session_scores.append(score)

            print_separator()

            play_again = get_valid_choice(
                "  Play another round? [y/n]: ",
                ["y", "n"]
            )

            if play_again == "n":
                display_session_stats(session_scores)
                input("\n  Press Enter to return to menu...")

        elif choice == "2":
            clear_screen()
            print_banner()

            display_leaderboard()

            input("\n  Press Enter to return to menu...")

        elif choice == "3":
            clear_screen()
            print_banner()

            how_to_play()

        elif choice == "4":
            clear_screen()
            print_banner()

            if session_scores:
                display_session_stats(session_scores)

            slow_print("\n  Thanks for playing! Goodbye 👋\n")

            break

# Program starts execution from here
if __name__ == "__main__":
    main()