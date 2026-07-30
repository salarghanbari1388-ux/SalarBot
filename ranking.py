from database import users


def ranking_text():
    if not users:
        return "🏆 هنوز بازیکنی وجود ندارد."

    players = sorted(
        users.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    text = "🏆 رتبه‌بندی بازیکنان:\n\n"

    for i, player in enumerate(players[:10], start=1):
        text += (
            f"{i}️⃣ {player['username']} "
            f"➜ {player['score']} امتیاز\n"
        )

    return text
