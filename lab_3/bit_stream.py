class BitStream:
    def __init__(self, file, mode):
        self.file = file
        self.mode = mode
        self.buffer = 0
        self.bit_pos = 0 

    def write_bit(self, bit: int):
        if self.mode != 'w':
            raise ValueError("BitStream відкрит не для запису")

        bit = 1 if bit else 0
        self.buffer = (self.buffer << 1) | bit
        self.bit_pos += 1

        if self.bit_pos == 8:
            self.file.write(bytes([self.buffer]))
            self.buffer = 0
            self.bit_pos = 0

    def read_bit(self) -> int:
        if self.mode != 'r':
            raise ValueError("BitStream відкрит не для читання")

        if self.bit_pos == 0:
            byte = self.file.read(1)
            if not byte:
                raise EOFError("Кінець файлу")
            self.buffer = byte[0]
            self.bit_pos = 8

        bit = (self.buffer >> (self.bit_pos - 1)) & 1
        self.bit_pos -= 1
        return bit

    def close(self):
        if self.mode == 'w' and self.bit_pos != 0:
            self.buffer <<= (8 - self.bit_pos)
            self.file.write(bytes([self.buffer]))
        self.file.close()


def WriteBitSequence(bs, data, bit_length):
    bit_index = 0
    for _ in range(bit_length):
        byte_index = bit_index // 8
        bit_in_byte = 7 - (bit_index % 8)
        bit = (data[byte_index] >> bit_in_byte) & 1

        bs.buffer = (bs.buffer << 1) | bit
        bs.bit_pos += 1

        if bs.bit_pos == 8:
            bs.file.write(bytes([bs.buffer]))
            bs.buffer = 0
            bs.bit_pos = 0

        bit_index += 1


def ReadBitSequence(bs, bit_length):
    result = []
    current_byte = 0
    bits_collected = 0

    for _ in range(bit_length):
        if bs.bit_pos == 0:
            byte = bs.file.read(1)
            if not byte:
                raise EOFError("Кінець файлу")
            bs.buffer = byte[0]
            bs.bit_pos = 8

        bit = (bs.buffer >> (bs.bit_pos - 1)) & 1
        bs.bit_pos -= 1

        current_byte = (current_byte << 1) | bit
        bits_collected += 1

        if bits_collected == 8:
            result.append(current_byte)
            current_byte = 0
            bits_collected = 0

    if bits_collected > 0:
        current_byte <<= (8 - bits_collected)
        result.append(current_byte)

    return bytes(result)
