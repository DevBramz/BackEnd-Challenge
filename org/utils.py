# Taking input from user
inputString = "Geeksforgeeks"

l = len(inputString)
newString = ""

# looping through the string
for i in range(0, len(inputString)):
	if l < 3:
		break
	else:
		if i in (0, 1, l-2, l-1):
			newString = newString + inputString[i]
		else:
			continue

# Printing New String
print("Input string : " + inputString)
print("New String : " + newString)
