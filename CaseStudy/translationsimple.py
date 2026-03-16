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
    return (f"{a} must be executed by {resource}")

def executed_by_return(tree, a):
    return (f"The resource that executes {a}")

# Time
def timed_alternative(tree, a, b, time):
    return (f"If {a} takes longer than {time}, {b} must be executed instead")

def min_time_between(tree, a, b, time, c=None):
    if c is not None:
        return (f"The time between {a} and {b} must be at least {time}, otherwise {c} must be executed")
    else:
        return (f"The time between {a} and {b} must be at least {time}")

def max_time_between(tree, a, b, time, c=None):
    if c is not None:
        return (f"The time between {a} and {b} must be at most {time}, otherwise {c} must be executed")
    else:
        return (f"The time between {a} and {b} must be at most {time}")

def by_due_date(tree, a, timestamp, c=None):
    if c is not None:
        return (f"{a} must be completed by {timestamp}, otherwise {c} must be executed")
    else:
        return (f"{a} must be completed by {timestamp}")
    
def recurring(tree, a, t):
    return (f"{a} must recur every {t}")

# Data
def send_exist(tree, data):
    return (f"Send {data}")

def receive_exist(tree, data):
    return (f"Receive {data}")

def activity_sends(tree, a, data):
    return (f"{a} must send {data}")

def activity_receives(tree, a, data):
    return (f"{a} must receive {data}")

def condition_directly_follows(tree, condition, a):
    return (f"If {condition}, {a} must directly follow")

def condition_eventually_follows(tree, condition, a, scope="branch"):
    if scope == "branch":
        return (f"If and only if {condition}, {a} must eventually follow")
    else:
        return (f"If {condition}, {a} must eventually follow")

def data_leads_to_absence(tree, condition, a):
    return (f"If {condition}, {a} must not occur")

# Failure
def failure_eventually_follows(tree, a, b):
    return (f"If {a} fails to execute, {b} must eventually follow")

def failure_directly_follows(tree, a, b):
    return (f"If {a} fails to execute, {b} must directly follow")