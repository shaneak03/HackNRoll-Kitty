# There is probably a smarter, more efficient way to do this with regex. This runs nearly instantly though, so no big deal.
import re



def getFilenameOfLine(line):
    topic = getTopic(line)
    return re.sub(r'[^A-Za-z0-9 -]+', '',  topic.lower())

def getTopic(stri):
    if "[" in stri:
        start = stri.index("[")+1
        end = stri.index("]")
        return stri[start:end]
    else:
        return removeTags(stri)

def capitalize(stri):
    words = stri.split(" ")
    result = ""
    for i in range(len(words)):
        if i >= 1:
            result = result+" "
        w = words[i]
        result = result+w[0].upper()+w[1:]
    return result
