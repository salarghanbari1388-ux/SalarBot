from datetime import datetime, timedelta


vip_users = {}
free_questions = {}
vip_requests = []

FREE_LIMIT = 3

# شماره کارت خودت را اینجا بگذار
CARD_NUMBER = "0000-0000-0000-0000"


def is_vip(user_id):

    if user_id in vip_users:
        if datetime.now() < vip_users[user_id]:
            return True

        del vip_users[user_id]

    return False



def activate_vip(user_id):

    vip_users[user_id] = datetime.now() + timedelta(days=7)



def use_free_question(user_id):

    today = datetime.now().date()

    if user_id not in free_questions:
        free_questions[user_id] = {
            "count": FREE_LIMIT,
            "date": today
        }

    data = free_questions[user_id]

    if data["date"] != today:
        data["count"] = FREE_LIMIT
        data["date"] = today

    if data["count"] > 0:
        data["count"] -= 1
        return True

    return False



def add_vip_request(user_id, photo_id):

    vip_requests.append({
        "user_id": user_id,
        "photo": photo_id,
        "status": "pending"
    })



def get_vip_requests():

    return vip_requests



def approve_vip(index):

    request = vip_requests[index]

    activate_vip(request["user_id"])

    request["status"] = "approved"



def reject_vip(index):

    vip_requests[index]["status"] = "rejected"
