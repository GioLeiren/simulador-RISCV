#Giovanni Minari Zanetti - 202014280
import numpy as np

mem = np.zeros(16384, dtype=np.uint8)

def sb(reg,kte,byte):
    address = reg + kte
    mem[address] = byte & 0xFF

def sw(reg,kte,word):
    byte0 = word & 0xFF
    sb(reg,kte,byte0)
    byte1 = (word >> 8) & 0xFF
    sb(reg,kte+1,byte1)
    byte2 = (word >> 16) & 0xFF
    sb(reg,kte+2,byte2)
    byte3 = (word >> 24) & 0xFF
    sb(reg,kte+3,byte3)
    
def lb(reg,kte):
    address = reg + kte
    byte = np.int8(mem[address])
    if byte < 0:
        word = (1 << 32) + byte
        return word
    else:
        return byte

def lbu(reg,kte):
    address = reg + kte
    byte = np.uint8(mem[address])
    word = 0x00FF & byte
    return  word

def lw(reg,kte):
    address = reg + kte
    byte0 = np.uint8(mem[address])
    byte1 = np.uint8(mem[address+1])
    byte2 = np.uint8(mem[address+2])
    byte3 = np.uint8(mem[address+3])
    word = (byte3 << 24) | (byte2 << 16) | (byte1 << 8) | byte0
    return np.uint32(word)