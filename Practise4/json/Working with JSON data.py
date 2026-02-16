import json

with open("sample-data.json", "r") as file:
    data = json.load(file)

for student in data["students"]:
    print(student["name"], "-", student["grade"])

total = 0
for student in data["students"]:
    total += student["grade"]

average = total / len(data["students"])
print("Орташа балл:", average)