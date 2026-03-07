import shutil
import os

# 1. Create a text file and write sample data
with open("sample.txt", "w") as file:
    file.write("Hello, this is the first line.\n")
    file.write("This is the second line.\n")

print("File created and data written.\n")

# 2. Read and print file contents
print("Reading file contents:")
with open("sample.txt", "r") as file:
    content = file.read()
    print(content)

# 3. Append new lines and verify content
with open("sample.txt", "a") as file:
    file.write("This line was appended later.\n")
    file.write("Another appended line.\n")

print("\nAfter appending new lines:")
with open("sample.txt", "r") as file:
    print(file.read())

# 4. Copy and back up files using shutil
shutil.copy("sample.txt", "sample_backup.txt")
print("\nBackup file created: sample_backup.txt")

# 5. Delete files safely
if os.path.exists("sample_backup.txt"):
    os.remove("sample_backup.txt")
    print("Backup file deleted safely.")
else:
    print("File does not exist.")