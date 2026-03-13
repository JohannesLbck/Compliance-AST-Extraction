# Control Flow
def exists(tree, a):
    return (f"Activity \"{a}\" has to occur")

def absence(tree, a):
    return (f"Activity \"{a}\" must not occur")

def loop(tree, a):
    return (f"Activity \"{a}\" must be part of a loop")

def directly_follows(tree, a, b):
    return (f"Activity \"{a}\" must directly follow activity \"{b}\"")

def leads_to(tree, a, b):
    return (f"Activity \"{a}\" must lead to activity \"{b}\"")

def precedence(tree, a, b):
    return (f"Activity \"{a}\" must precede activity \"{b}\"")

def leads_to_absence(tree, a, b):
    return (f"Activity \"{a}\" must lead to the absence of activity \"{b}\"")

def precedence_absence(tree, a, b):
    return (f"Activity \"{a}\" must precede the absence of activity \"{b}\"")

def parallel(tree, a, b):
    return (f"Activity \"{a}\" must be parallel to activity \"{b}\"")

# Resource
def executed_by_identify(tree, resource):
    return (f"Activity must be executed by resource \"{resource}\"")

def executed_by(tree, a, resource):
    return (f"Activity \"{a}\" must be executed by resource \"{resource}\"")

def executed_by_return(tree, a):
    return (f"The resource that executes activity \"{a}\"")

# Time
def timed_alternative(tree, a, b, time):
    return (f"If activity \"{a}\" takes longer than {time}, activity \"{b}\" must be executed instead")

def min_time_between(tree, a, b, time, c=None):
    if c is not None:
        return (f"The time between activity \"{a}\" and \"{b}\" must be at least {time}, otherwise activity \"{c}\" must be executed")
    else:
        return (f"The time between activity \"{a}\" and \"{b}\" must be at least {time}")

def max_time_between(tree, a, b, time, c=None):
    if c is not None:
        return (f"The time between activity \"{a}\" and \"{b}\" must be at most {time}, otherwise activity \"{c}\" must be executed")
    else:
        return (f"The time between activity \"{a}\" and \"{b}\" must be at most {time}")

def by_due_date(tree, a, timestamp, c=None):
    if c is not None:
        return (f"Activity \"{a}\" must be completed by {timestamp}, otherwise activity \"{c}\" must be executed")
    else:
        return (f"Activity \"{a}\" must be completed by {timestamp}")
    
def recurring(tree, a, t):
    return (f"Activity \"{a}\" must recur every {t}")

# Data
def send_exist(tree, data):
    return (f"Activity that sends \"{data}\"")

def receive_exist(tree, data):
    return (f"Activity that receives \"{data}\"")

def activity_sends(tree, a, data):
    return (f"Activity \"{a}\" sends \"{data}\"")

def activity_receives(tree, a, data):
    return (f"Activity \"{a}\" receives \"{data}\"")

def condition_directly_follows(tree, condition, a):
    return (f"If \"{condition}\", \"{a}\" must directly follow")

def condition_eventually_follows(tree, condition, a, scope="branch"):
    if scope == "branch":
        return (f"If and only if \"{condition}\", \"{a}\" must eventually follow")
    else:
        return (f"If \"{condition}\", \"{a}\" must eventually follow")

def data_leads_to_absence(tree, condition, a):
    return (f"If \"{condition}\", \"{a}\" must not occur")

# Failure
def failure_eventually_follows(tree, a, b):
    return (f"If activity \"{a}\" fails to execute, activity \"{b}\" must eventually follow")

def failure_directly_follows(tree, a, b):
    return (f"If activity \"{a}\" fails to execute, activity \"{b}\" must directly follow")