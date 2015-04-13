VERSION = (1, 0, 0, 'alpha', 0)


# Inspired by: https://github.com/fabric/fabric/blob/master/fabric/version.py
def get_version():
    branch = "%s.%s" % (VERSION[0], VERSION[1])
    tertiary = VERSION[2]
    type_ = VERSION[3]
    final = (type_ == "final")
    type_num = VERSION[4]
    firsts = "".join([x[0] for x in type_.split()])
    v = branch
    if (tertiary or final):
        v += "." + str(tertiary)
    if not final:
        v += firsts
        if type_num:
            v += str(type_num)
    return v
