active_riddles = {}


def save_riddle(user_id, answer):
    active_riddles[user_id] = answer


def check_answer(user_id, answer):
    correct = active_riddles.get(user_id)

    if correct and answer.strip() == correct:
        return True

    return False
