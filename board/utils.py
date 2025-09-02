import random

def generate_unique_nickname(board, base_nickname):
    """
    Generate a unique nickname for the given board by appending a suffix if needed.
    """
    existing_names = board.active_users.values_list('nickname', flat=True)

    if base_nickname not in existing_names:
        return base_nickname

    counter = 2
    while True:
        new_nickname = f"{base_nickname} ({counter})"
        if new_nickname not in existing_names:
            return new_nickname
        counter += 1

def random_color():
    # Pick from a readable palette instead of completely random RGB
    colors = [
        "#FF5733", "#33FF57", "#3357FF",
        "#F1C40F", "#9B59B6", "#1ABC9C"
    ]
    return random.choice(colors)
