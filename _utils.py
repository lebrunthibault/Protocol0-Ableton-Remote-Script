import traceback

def print_except(func):
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            args[0].canonical_parent.log_message(traceback.format_exc())

    return inner