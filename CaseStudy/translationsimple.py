# Control Flow
def exists(tree, a):
    return (f"{a} has to occur")

def absence(tree , a):
    return (f"{a} must not occur")

def loop(tree, a):
    return (f"{a} must be part of a loop")
    
def directly_follows(tree, a, b):
    return (f"{a} must directly follow {b}")

def leads_to(tree, a, b):
    return (f"{a} must lead to {b}")

def precedence(tree, a, b):
    return (f"{a} must precede {b}")

def leads_to_absence(tree, a, b):
    return (f"{a} must lead to the absence of {b}")

def precedence_absence(tree, a, b):
    return (f"{a} must precede the absence of {b}")

def parallel(tree, a, b):
    return (f"{a} must be parallel to {b}")

# Resource
def executed_by_identify(tree, resource):
    return (f"{resource} is executing")

def executed_by(tree, a, resource):
    return (f"{resource} must execute {a}")

def executed_by_return(tree, a):
    return (f"The resource that executes {a}")

# Time
def timed_alternative(tree, a, b, time):
    return (f"If {a} takes longer than {time} seconds, {b} must be executed instead")

def min_time_between(tree, a, b, time, c=None):
    if c is not None:
        return (f"The time between {a} and {b} must be at least {time} seconds, otherwise {c} must be executed")
    else:
        return (f"The time between {a} and {b} must be at least {time} seconds")

def max_time_between(tree, a, b, time, c=None):
    if c is not None:
        return (f"The time between {a} and {b} must be at most {time} seconds, otherwise {c} must be executed")
    else:
        return (f"The time between {a} and {b} must be at most {time} seconds")

def by_due_date(tree, a, timestamp, c=None):
    if c is not None:
        return (f"{a} must be completed by {timestamp}, otherwise {c} must be executed")
    else:
        return (f"{a} must be completed by {timestamp}")
    
def recurring(tree, a, t):
    return (f"{a} must recur every {t}")

# Data
def send_exist(tree, data):
    return (f"Send {data} data object")

def receive_exist(tree, data):
    return (f"Receive {data} data object")

def activity_sends(tree, a, data):
    return (f"{a} must send {data} data object")

def activity_receives(tree, a, data):
    return (f"{a} must receive {data} data object")

def condition_directly_follows(tree, condition, a):
    return (f"If {condition}, {a} must directly follow")

def condition_eventually_follows(tree, condition, a, scope="branch"):
    return (f"If {condition}, {a} must eventually follow")

def data_leads_to_absence(tree, condition, a):
    return (f"If {condition}, {a} must not occur")

# Failure
def failure_eventually_follows(tree, a, b):
    return (f"If {a} fails to execute, {b} must eventually follow")

def failure_directly_follows(tree, a, b):
    return (f"If {a} fails to execute, {b} must directly follow")