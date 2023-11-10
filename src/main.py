from components.guard import Guard

# Instantiate the guard
guard = Guard.start(1, 2, 3.0)

answer = guard.ask("Hi, I'm a message!")
print(answer) # Hi, I'm a guard!

guard.stop()

