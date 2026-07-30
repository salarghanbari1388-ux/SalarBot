import random

riddles = [
    {
        "question": "آن چیست که هرچه بیشتر از آن برداری، بزرگ‌تر می‌شود؟",
        "answer": "چاله"
    },
    {
        "question": "چه چیزی سر دارد ولی بدن ندارد؟",
        "answer": "سکه"
    },
    {
        "question": "چه چیزی همیشه جلوی توست ولی نمی‌توانی آن را ببینی؟",
        "answer": "آینده"
    }
]


def get_riddle():
    return random.choice(riddles)
