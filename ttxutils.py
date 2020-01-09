
def nextpage(page):
    if type(page) is str:
        page = int(page, 16)
    while True:
        page += 1
        if (page & 0x0f) <= 9:
            return page

def decode(text):
    return text.replace("€", "\x1B").replace("¬", "\x7F")

def hexdiff(a, b):
    return ( 1 + int(f"{a:x}") - int(f"{b:x}") )
