import random

#random
x = random.random()
print(x)   

#randint
x = random.randint(1, 10)
print(x)

#choise
students = ["Ali", "Dana", "Aruzhan", "Nursultan"]
x = random.choice(students)
print(x)

#shuffle
numbers = [1, 2, 3, 4, 5]
random.shuffle(numbers)
print(numbers)