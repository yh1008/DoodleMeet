str = "2-4A0r7-4k-7nvdh-"

words= str.split("-")

print(words)

str=""

for w in words:
	str=str+w

str = str.upper()
str= str[::-1]

print str

parts = [str[i:i+4] for i in range(0, len(str), 4)]

print parts
str=""
for p in parts:
	str=str+p
	str=str+"-"

str = str[:-1]
str = str[::-1]
print str