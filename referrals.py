from config import BOT_USERNAME

referrals = {}
invited_by = {}

def add_referral(user_id, inviter_id):
    if user_id == inviter_id or user_id in invited_by:
        return
    invited_by[user_id] = inviter_id
    referrals[inviter_id] = referrals.get(inviter_id, 0) + 1

def get_referrals(user_id):
    return referrals.get(user_id, 0)

def referral_link(user_id):
    return f"https://t.me/{BOT_USERNAME}?start={user_id}"

def top_referrers():
    return sorted(referrals.items(), key=lambda x: x[1], reverse=True)
