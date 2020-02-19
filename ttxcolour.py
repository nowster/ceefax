
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

MOSAICBLACK   = 0x10
MOSAICRED     = 0x11
MOSAICGREEN   = 0x12
MOSAICYELLOW  = 0x13
MOSAICBLUE    = 0x14
MOSAICMAGENTA = 0x15
MOSAICCYAN    = 0x16
MOSAICWHITE   = 0x17

CONCEAL    = 0x18
CONTIGUOUS = 0x19
SEPARATED  = 0x1a
ESC        = 0x1b
BLACK_BACK = 0x1c
NEW_BACK   = 0x1d
HOLD       = 0x1e
RELEASE    = 0x1f

AK = ALPHABLACK
AR = ALPHARED
AG = ALPHAGREEN
AY = ALPHAYELLOW
AB = ALPHABLUE
AM = ALPHAMAGENTA
AC = ALPHACYAN
AW = ALPHAWHITE

MK = MOSAICBLACK
MR = MOSAICRED
MG = MOSAICGREEN
MY = MOSAICYELLOW
MB = MOSAICBLUE
MM = MOSAICMAGENTA
MC = MOSAICCYAN
MW = MOSAICWHITE

def colour(value):
    return chr(ESC) + chr(value + 0x40)
def char(value):
    return chr(value + 0x2400)
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
