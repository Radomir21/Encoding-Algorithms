class BitStream:
    def __init__(self, file, mode: str):
        self.file = file
        self.mode = mode
        self.buffer = 0     
        self.bit_pos = 0     

    def write_bit(self, bit: int):
        if self.mode != 'w':
            raise ValueError("BitStream відкрит не для запису")

        bit = 1 if bit else 0
        # LSB-first: перший біт кладемо в позицію 0, далі 1,2,...
        self.buffer |= (bit << self.bit_pos)
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
            self.bit_pos = 0

        bit = (self.buffer >> self.bit_pos) & 1
        self.bit_pos += 1

        if self.bit_pos == 8:
            self.bit_pos = 0

        return bit

    def close(self):
        if self.mode == 'w' and self.bit_pos != 0:
            self.file.write(bytes([self.buffer]))
        self.file.close()


def WriteBitSequence(bs: BitStream, data: bytes, bit_length: int):
    for bit_index in range(bit_length):
        byte_index = bit_index // 8
        bit_in_byte = bit_index % 8         
        bit = (data[byte_index] >> bit_in_byte) & 1
        bs.write_bit(bit)


def ReadBitSequence(bs: BitStream, bit_length: int) -> bytes:
    result = bytearray()
    current_byte = 0
    bits_collected = 0

    for _ in range(bit_length):
        bit = bs.read_bit()                  
        current_byte |= (bit << bits_collected)
        bits_collected += 1

        if bits_collected == 8:
            result.append(current_byte)
            current_byte = 0
            bits_collected = 0

    if bits_collected > 0:
        result.append(current_byte)

    return bytes(result)
