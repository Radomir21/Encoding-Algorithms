from  bit_stream import BitStream, WriteBitSequence, ReadBitSequence

with open("t2.bin", "wb") as f:
    bs = BitStream(f, 'w')
    WriteBitSequence(bs, bytes([0b10100000]), 3)   # 101
    WriteBitSequence(bs, bytes([0b01000000]), 2)   # 01
    bs.close()

with open("t2.bin", "rb") as f:
    bs = BitStream(f, 'r')
    b = ReadBitSequence(bs, 5)
    bs.close()

with open("t3.bin", "wb") as f:
    bs = BitStream(f, 'w')
    WriteBitSequence(bs, bytes([0xAA]), 8)   # 10101010
    WriteBitSequence(bs, bytes([0x55]), 8)   # 01010101
    bs.close()

with open("t3.bin", "rb") as f:
    bs = BitStream(f, 'r')
    b = ReadBitSequence(bs, 16)
    bs.close()

with open("t4.bin", "wb") as f:
    bs = BitStream(f, 'w')
    WriteBitSequence(bs, bytes([0b11110000]), 4)   # 1111
    WriteBitSequence(bs, bytes([0b00001111]), 4)   # 0000
    WriteBitSequence(bs, bytes([0b10101010]), 8)
    bs.close()

with open("t4.bin", "rb") as f:
    bs = BitStream(f, 'r')
    b1 = ReadBitSequence(bs, 6)
    b2 = ReadBitSequence(bs, 10)
    bs.close()

with open("t5.bin", "wb") as f:
    bs = BitStream(f, 'w')
    WriteBitSequence(bs, bytes([0xF0]), 8)
    WriteBitSequence(bs, bytes([0x0F]), 8)
    WriteBitSequence(bs, bytes([0xAA]), 8)
    bs.close()

with open("t5.bin", "rb") as f:
    bs = BitStream(f, 'r')
    b1 = ReadBitSequence(bs, 5)
    b2 = ReadBitSequence(bs, 7)
    b3 = ReadBitSequence(bs, 12)
    bs.close()