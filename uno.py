import tkinter as tk
from tkinter import simpledialog, messagebox
import random

# Constants
COLORS = ["Red", "Blue", "Green", "Yellow"]  # Uno card colors
SPECIALS = ["Skip", "Reverse", "Draw Two"]  # Special action cards
WILDS = ["Wild Change Color", "Wild Draw Four"]  # Wild cards
COLOR_CODES = {  # Colors mapped to their corresponding HEX codes
    "Red": "#FF6961", 
    "Blue": "#77DDFF", 
    "Green": "#77DD77", 
    "Yellow": "#FFD700", 
    "wild": "#000000",  # Black color for wild cards
}

def create_deck():
    """
    Create and shuffle a deck of Uno cards.
    
    Returns:
        list: A shuffled list of card dictionaries, each representing a card.
    """
    deck = []
    # Add number cards for each color
    for color in COLORS:
        for num in range(10):  # Add numbers 0-9
            deck.append({"color": color, "type": "number", "value": num})
            if num != 0:  # Add duplicate cards for numbers 1-9
                deck.append({"color": color, "type": "number", "value": num})   
        # Add special cards (Skip, Reverse, Draw Two)
        for special in SPECIALS:
            deck.extend([{"color": color, "type": "special", "value": special}] * 2)
    # Add wild cards (Wild Change Color, Wild Draw Four)
    for wild in WILDS:
        deck.extend([{"color": "wild", "type": "wild", "value": wild}] * 4)
    random.shuffle(deck)  # Shuffle the deck
    return deck

def valid_move(card, top_card):
    """
    Check if a card is a valid move based on the top card of the discard pile.

    Args:
        card (dict): The card the player wants to play.
        top_card (dict): The current top card on the discard pile.
    
    Returns:
        bool: True if the card is valid, False otherwise.
    """
    return (
        card["color"] == top_card["color"]
        or card["value"] == top_card["value"]
        or card["type"] == "wild"
    )

def draw_starting_card(deck):
    """
    Draw the first card for the discard pile, ensuring it is a number card.

    Args:
        deck (list): The deck of Uno cards.
    
    Returns:
        dict: A valid number card to start the discard pile.
    """
    card = deck.pop()
    # Continue drawing until a number card is found
    while card["type"] != "number":
        deck.append(card)
        random.shuffle(deck)
        card = deck.pop()
    return card

def create_card_button(frame, card, command, visible=True):
    """
    Create a button representing a card.

    Args:
        frame (tk.Frame): The parent frame to which the button belongs.
        card (dict): The card to represent with the button.
        command (function): The function to execute when the button is clicked.
        visible (bool): Whether the card's details are visible (current player).

    Returns:
        tk.Button: A configured button representing the card.
    """
    # Determine the text and colors for the button
    text = (
        "\n".join(card["value"].split()) if card["type"] != "number" else f"{card['value']}"
    )
    bg_color = COLOR_CODES[card["color"]] if visible else "#000000"  # Card color or black
    fg_color = "white" if visible else "#000000"  # Font color
    button = tk.Button(
        frame,
        text=text if visible else "",
        font=("Comic Sans MS", 9, "bold"),
        bg=bg_color,
        fg=fg_color,
        width=6,
        height=3,
        command=command if visible else None,
    )
    return button

def update_ui():
    """
    Update the user interface to reflect the current state of the game.
    Includes player hands, the discard pile, and the turn indicator.
    """
    global current_turn, hands, discard_pile

    # Update each player's frame
    for player, frame in enumerate(player_frames):
        # Clear all current widgets in the frame
        for widget in frame.winfo_children():
            widget.destroy()

        # Add player label
        player_label = tk.Label(
            frame,
            text=f"Player {player + 1}",
            font=("Comic Sans MS", 10, "bold"),
            bg="#87CEEB",
        )
        player_label.grid(row=0, column=0, columnspan=5, pady=5)

        # Add card buttons for each card in the player's hand
        for idx, card in enumerate(hands[player]):
            row, col = divmod(idx, 5)  # Arrange cards in rows and columns
            visible = player == current_turn  # Cards are visible only for the current player
            command = lambda i=idx, p=player: play_card(p, i)
            card_button = create_card_button(frame, card, command, visible=visible)
            card_button.grid(row=row + 1, column=col, padx=2, pady=2)

    # Update the discard pile label
    top_card = discard_pile[-1]
    discard_label.config(
        text="\n".join(top_card["value"].split()) if top_card["type"] != "number" else f"{top_card['value']}",
        bg=COLOR_CODES[top_card["color"]] if top_card["type"] != "wild" else "#000000",
        fg="yellow" if top_card["type"] == "wild" else "white",
    )

    # Update the turn indicator
    turn_label.config(text=f"Player {current_turn + 1}'s Turn")

def position_elements():
    """
    Position player frames, the discard pile, and game buttons on the window.
    The layout changes based on the number of players.
    """
    global player_frames, discard_label, draw_button, skip_button

    # Define positions for each number of players
    positions = {
        2: [(0.5, 0.75), (0.5, 0.25)],  # Player 1 bottom, Player 2 top
        3: [(0.5, 0.75), (0.25, 0.5), (0.75, 0.5)],  # Add Player 3 on left
        4: [(0.5, 0.75), (0.25, 0.5), (0.5, 0.25), (0.75, 0.5)],  # Add Player 4 on right
    }

    # Place each player's frame
    for i, frame in enumerate(player_frames):
        frame.place(relx=positions[n_players][i][0], rely=positions[n_players][i][1], anchor="center")

    # Position the discard pile and action buttons
    discard_label.place(relx=0.5, rely=0.5, anchor="center")
    draw_button.place(relx=0.4, rely=0.5, anchor="center")
    skip_button.place(relx=0.6, rely=0.5, anchor="center")
def play_card(player, card_idx):
    """
    Play a card from the player's hand.

    Args:
        player (int): The player attempting to play the card.
        card_idx (int): The index of the card in the player's hand.

    Returns:
        None
    """
    global current_turn, discard_pile, hands, deck

    # Ensure the correct player is making the move
    if player != current_turn:
        messagebox.showwarning("Invalid Move", "It's not your turn!")
        return

    card = hands[player][card_idx]  # The card being played
    top_card = discard_pile[-1]  # The top card on the discard pile

    # Validate the move
    if not valid_move(card, top_card):
        messagebox.showwarning("Invalid Move", "You can't play that card!")
        return

    # Remove the card from the player's hand and add it to the discard pile
    hands[player].pop(card_idx)
    discard_pile.append(card)

    # Check for a win condition (player has no cards left)
    if not hands[player]:
        messagebox.showinfo("Game Over", f"Player {player + 1} wins!")
        root.quit()
        return

    # Handle special or wild cards
    if card["type"] == "special":
        handle_special_card(card)
    elif card["type"] == "wild":
        handle_wild_card(card)

    # Move to the next turn
    current_turn = (current_turn + direction) % n_players
    update_ui()

def handle_special_card(card):
    """
    Handle the effects of special action cards (Skip, Reverse, Draw Two).

    Args:
        card (dict): The special card being played.

    Returns:
        None
    """
    global current_turn, hands, deck, direction, n_players

    if card["value"] == "Skip":
        # Skip the next player's turn
        current_turn = (current_turn + 1) % n_players
    elif card["value"] == "Reverse":
        # Reverse the direction of play
        global direction
        direction *= -1
    elif card["value"] == "Draw Two":
        # Make the next player draw two cards
        next_player = (current_turn + direction) % n_players
        for _ in range(2):
            if deck:
                hands[next_player].append(deck.pop())
            else:
                messagebox.showinfo("Deck", "Deck is empty!")

def handle_wild_card(card):
    """
    Handle the effects of wild cards (Wild Change Color, Wild Draw Four).

    Args:
        card (dict): The wild card being played.

    Returns:
        None
    """
    global discard_pile

    # Prompt the player to choose a color
    color = simpledialog.askstring("Wild Card", "Choose a color (Red, Blue, Green, Yellow):")
    while color not in COLORS:
        color = simpledialog.askstring("Wild Card", "Invalid color. Choose again (Red, Blue, Green, Yellow):")
    card["color"] = color  # Update the card's color
    discard_pile[-1] = card  # Update the discard pile with the updated card

    if card["value"] == "Wild Draw Four":
        # Make the next player draw four cards
        next_player = (current_turn + direction) % n_players
        for _ in range(4):
            if deck:
                hands[next_player].append(deck.pop())
            else:
                messagebox.showinfo("Deck", "Deck is empty!")

def draw_card():
    """
    Allow the current player to draw a card from the deck.

    Returns:
        None
    """
    global current_turn, hands, deck

    if deck:
        # Add a card from the deck to the player's hand
        hands[current_turn].append(deck.pop())
        update_ui()
    else:
        messagebox.showinfo("Deck", "The deck is empty!")

def skip_turn():
    """
    Skip the current player's turn and move to the next player.

    Returns:
        None
    """
    global current_turn
    current_turn = (current_turn + 1) % n_players
    update_ui()

# Main Game Setup
root = tk.Tk()  # Create the main application window
root.title("UNO Game")
root.geometry("1920x1080")
root.configure(bg="#87CEEB")

# Initialize the deck and deal cards
deck = create_deck()
n_players = simpledialog.askinteger("Players", "Enter number of players (2-4):", minvalue=2, maxvalue=4)
hands = [[deck.pop() for _ in range(5)] for _ in range(n_players)]  # Each player starts with 5 cards
discard_pile = [draw_starting_card(deck)]  # Initialize the discard pile
current_turn = 0  # Start with player 1
direction = 1  # Direction of play (1 for clockwise, -1 for counterclockwise)

# Create player frames
player_frames = []
for i in range(n_players):
    frame = tk.Frame(root, bg="#87CEEB")
    player_frames.append(frame)

# Create labels and buttons for the UI
turn_label = tk.Label(root, text="", font=("Comic Sans MS", 16), bg="#87CEEB", fg="black")
turn_label.pack()

discard_label = tk.Label(root, text="", font=("Comic Sans MS", 14), width=15, height=4, relief="raised", bd=4)

draw_button = tk.Button(root, text="Draw Card", font=("Comic Sans MS", 12), bg="#FFD700", command=draw_card)
skip_button = tk.Button(root, text="Skip Turn", font=("Comic Sans MS", 12), bg="#FF6961", command=skip_turn)

# Position elements on the window
position_elements()

# Update the UI to reflect the initial game state
update_ui()

# Start the main event loop
root.mainloop()
