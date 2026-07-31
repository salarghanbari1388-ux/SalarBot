from database import add_score

def open_treasure(user_id):
    reward = 10
    add_score(user_id, reward)
    return reward
