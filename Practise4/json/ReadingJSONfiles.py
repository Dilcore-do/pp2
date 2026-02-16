import json

with open("data.json", "r") as file:
    data = json.load(file)

print(data)
print(data["name"])
print(data["age"])