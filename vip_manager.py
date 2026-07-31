from datetime import datetime, timedelta
from config import VIP_DAYS, FREE_LIMIT

vip_users = {}
free_questions = {}
vip_requests = []

def is_vip(user_id):
    if user_id in vip_users:
        if datetime.now() < vip_users[user_id]:
            return True
        del vip_users[user_id]
    return False

def activate_vip(user_id):
    vip_users[user_id] = datetime.now() + timedelta(days=VIP_DAYS)

def use_free_question(user_id):
    today = datetime.now().date()
    if user_id not in free_questions:
        free_questions[user_id] = {"count": FREE_LIMIT, "date": today}
    
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
        "status": "pending",
        "time": datetime.now()
    })

def get_vip_requests():
    return vip_requests

def approve_vip(index):
    if 0 <= index < len(vip_requests):
        req = vip_requests[index]
        activate_vip(req["user_id"])
        req["status"] = "approved"

def reject_vip(index):
    if 0 <= index < len(vip_requests):
        vip_requests[index]["status"] = "rejected"
