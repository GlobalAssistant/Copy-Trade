# a =4
# print(int(a))
# print(type(a))
import json

a = {}
a["aa"] = 5
a["bb"] = "pp"
a["cc"] = 4

# b = str(a)

print(a, type(a))
# print(b, type(b))

r = json.dumps(a)
print("r", r, type(r))
c = json.loads(r)
print(c, type(c))
print(c["aa"], type(c["aa"]))
