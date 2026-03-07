from functools import reduce

# 1. Use map() and filter() on lists
numbers = [1, 2, 3, 4, 5, 6]

# map(): square each number
squared = list(map(lambda x: x**2, numbers))
print("Squared numbers:", squared)

# filter(): keep only even numbers
evens = list(filter(lambda x: x % 2 == 0, numbers))
print("Even numbers:", evens)


# 2. Aggregate with reduce()
sum_numbers = reduce(lambda a, b: a + b, numbers)
print("Sum of numbers:", sum_numbers)


# 3. Use enumerate() and zip()
names = ["Ali", "Dana", "Aruzhan"]
scores = [85, 90, 78]

# enumerate()
print("\nStudents with index:")
for index, name in enumerate(names):
    print(index, name)

# zip()
print("\nNames and scores:")
for name, score in zip(names, scores):
    print(name, "-", score)


# 4. Type checking and conversions
value = "123"

# type checking
print("\nType of value:", type(value))

# conversions
num = int(value)
print("Converted to int:", num)

float_num = float(num)
print("Converted to float:", float_num)

str_num = str(float_num)
print("Converted back to string:", str_num)
