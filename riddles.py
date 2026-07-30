from questions import questions
import random


def get_riddle():
    riddle = random.choice(questions)

    return {
        "id": riddle["id"],
        "question": riddle["question"],
        "answer": riddle["answer"],
        "level": riddle["level"]
    }
