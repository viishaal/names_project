import math
import untangle

a="Hello"
print a.lower()

a = [ 1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.,
      	0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,
        0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,
        0.,  0.,  0.,  0.]

print len(a)

print (ord('z') - ord('a'))
print int(math.ceil(26.0/3))

st = """<?xml version="1.0" encoding="utf-8"?>\
<response>\
<name_detail>\
<name>Andrew</name>\
<gender>m</gender>\
<usages>\
<usage>\
<usage_code>eng</usage_code>\
<usage_full>English</usage_full>\
<usage_gender>m</usage_gender>\
</usage>\
<usage>\
<usage_code>eng-bibl</usage_code>\
<usage_full>Biblical</usage_full>\
<usage_gender>m</usage_gender>\
</usage>\
</usages>\
</name_detail>\
</response>"""

obj = untangle.parse(st)
if hasattr(obj.response, "name_detail"):
	print "hello"

print st.__contains__("Biblical")
print obj.response.name_detail.usages.usage[1].usage_code.cdata
print obj.response.name_detail.usages.usage[1].usage_full.cdata












