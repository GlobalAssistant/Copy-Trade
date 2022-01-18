# a =4
# print(int(a))
# print(type(a))
import json
from datetime import datetime, timezone
from dateutil import parser

a = {}
a["aa"] = 5
a["bb"] = "pp"
a["cc"] = 4
a["date"] = str(datetime.now(timezone.utc))

# b = str(a)

print(a, type(a))
# print(b, type(b))
r=json.dumps(a, indent=4, sort_keys=True, default=str)

# r = json.dumps(a)
print("r", r, type(r))
c = json.loads(r)
print(c, type(c))
print(c["aa"], type(c["aa"]))

dt = parser.parse(c["date"])
print("dt", dt, type(dt))
