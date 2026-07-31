from datetime import datetime, timedelta

start_date = datetime.now()
base_prize = 300000
extra_prize = 0

def current_prize():
    return base_prize + extra_prize

def add_new_members(count):
    global extra_prize
    extra_prize += (count // 60) * 100000

def days_left():
    end = start_date + timedelta(days=14)
    remain = end - datetime.now()
    return max(0, remain.days)

def can_receive_reward(invites):
    return invites >= 10

def reset_competition():
    global start_date, extra_prize
    start_date = datetime.now()
    extra_prize = 0
