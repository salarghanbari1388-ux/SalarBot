current_answers = {}


def save_answer(user_id, answer):
    current_answers[user_id] = answer


def check_answer(user_id, text):
    if user_id not in current_answers:
        return False

    return text.strip() == current_answers[user_id]
