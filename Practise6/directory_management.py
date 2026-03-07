import os
import shutil

# 1. Create nested directories
os.makedirs("project/data/files", exist_ok=True)
print("Nested directories created: project/data/files")

# 2. List files and folders
print("\nFiles and folders in current directory:")
items = os.listdir(".")
for item in items:
    print(item)

# 3. Find files by extension
print("\nSearching for .txt files:")
for file in os.listdir("."):
    if file.endswith(".txt"):
        print(file)

# 4. Move and copy files between directories
# Create example file
with open("example.txt", "w") as f:
    f.write("This is an example file.")

# Copy file
shutil.copy("example.txt", "project/data/files/example_copy.txt")
print("\nFile copied to project/data/files")

# Move file
shutil.move("example.txt", "project/example_moved.txt")
print("File moved to project/example_moved.txt")