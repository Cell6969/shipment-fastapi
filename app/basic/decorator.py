from types import FunctionType


def log_call(func:FunctionType):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    
    return wrapper

@log_call
def helloFunction(name:str):
    print(f"hello world {name}")

helloFunction("aldo")