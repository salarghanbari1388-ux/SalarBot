# referrals.py


referrals = {}

invited_by = {}



def add_referral(user_id, inviter_id):

    if user_id == inviter_id:
        return


    if user_id in invited_by:
        return


    invited_by[user_id] = inviter_id


    if inviter_id not in referrals:

        referrals[inviter_id] = 0


    referrals[inviter_id] += 1




def get_referrals(user_id):

    return referrals.get(
        user_id,
        0
    )



def referral_link(user_id):

    return (
        f"https://t.me/YOUR_BOT_USERNAME"
        f"?start={user_id}"
    )



def top_referrers():

    return sorted(
        referrals.items(),
        key=lambda x:x[1],
        reverse=True
  )
