# support.py

support_messages = []


ADMIN_ID = 8646600079



def add_support_message(user_id, text):

    support_messages.append({
        "user_id": user_id,
        "text": text,
        "status": "open"
    })



def get_support_messages():

    return support_messages



def close_support(index):

    support_messages[index]["status"] = "closed"
