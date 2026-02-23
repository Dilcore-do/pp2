#The findall() function returns a list containing all matches.
import re

#Return a list containing every occurrence of "ai":
txt = "The rain in Spain"
x = re.findall("ai", txt)
print(x)


"""
The search() function searches the string for a match, and returns a Match object if there is a match.

If there is more than one match, only the first occurrence of the match will be returned:
"""
import re

txt = "The rain in Spain"
x = re.search("\s", txt)

print("The first white-space character is located in position:", x.start())

#The split() function returns a list where the string has been split at each match:

txt = "The rain in Spain"
x = re.split("\s", txt)
print(x)

#The sub() function replaces the matches with the text of your choice:

txt = "The rain in Spain"
x = re.sub("\s", "9", txt)
print(x)
