from database import add_score


current_answers = {}


def save_answer(user_id, answer):
    current_answers[user_id] = answer


def check_answer(user_id, text):
    if user_id not in current_answers:
        return False

    correct = current_answers[user_id]

    if text.strip() == correct:
        add_score(user_id, 10)
        del current_answers[user_id]
        return True

    return False
