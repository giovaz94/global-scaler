from components.guard import Guard


import time

if __name__ == '__main__':
    guard = Guard.start(1, 1, sleep=2)
    time.sleep(3)
    print("Sending message to Guard")
    response = guard.ask("Hello Guard")
    print(response)
