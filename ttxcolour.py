
ALPHABLACK   = 0x00
ALPHARED     = 0x01
ALPHAGREEN   = 0x02
ALPHAYELLOW  = 0x03
ALPHABLUE    = 0x04
ALPHAMAGENTA = 0x05
ALPHACYAN    = 0x06
ALPHAWHITE   = 0x07

FLASH         = 0x08
STEADY        = 0x09
END_BOX       = 0x0a
START_BOX     = 0x0b
NORMAL_SIZE   = 0x0c
DOUBLE_HEIGHT = 0x0d
DOUBLE_WIDTH  = 0x0e
DOUBLE_SIZE   = 0x0f

MK = 0x10
MR = 0x11
MG = 0x12
MY = 0x13
MB = 0x14
MM = 0x15
MC = 0x16
MW = 0x17

CONCEAL = 0x18
CONTIGUOUS = 0x19
SEPARATED  = 0x1a
ESC        = 0x1b
BLACK_BACK = 0x1c
NEW_BACK   = 0x1d
HOLD       = 0x1e
RELEASE    = 0x1f

def colour(value):
    return chr(ESC) + chr(value + 0x40)

def red():
    return colour(ALPHARED)
def green():
    return colour(ALPHAGREEN)
def yellow():
    return colour(ALPHAYELLOW)
def blue():
    return colour(ALPHABLUE)
def magenta():
    return colour(ALPHAMAGENTA)
def cyan():
    return colour(ALPHACYAN)
def white():
    return colour(ALPHAWHITE)
