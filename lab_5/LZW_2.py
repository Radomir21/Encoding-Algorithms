import struct
from bit_stream import BitStream
from BWT import bwt_encode, bwt_decode
from MTF import mtf_encode, mtf_decode

MAGIC = b"RAD2" 


FLAG_BWT = 1
FLAG_MTF = 2


def write_uint8(f, x):
    f.write(bytes([x & 0xFF]))


def read_uint8(f):
    b = f.read(1)
    if not b:
        raise EOFError("Неочікуваний кінець файлу (читання заголовку)")
    return b[0]


def write_bits_fixed(bs, value, bit_count):
    for i in range(bit_count):
        bs.write_bit((value >> i) & 1)


def read_bits_fixed(bs, bit_count):
    value = 0
    for i in range(bit_count):
        bit = bs.read_bit()
        value |= (bit << i)
    return value



def write_header_lb5(out_f, max_bits, overflow_mode, flags, block_size, bwt_indices):

    out_f.write(MAGIC)

    write_uint8(out_f, max_bits)
    mode_byte = 0 if overflow_mode == "freeze" else 1
    write_uint8(out_f, mode_byte)

    write_uint8(out_f, flags)
    out_f.write(struct.pack("<I", block_size))

    num_blocks = len(bwt_indices) if (flags & FLAG_BWT) else 0
    out_f.write(struct.pack("<I", num_blocks))

    if flags & FLAG_BWT:
        for idx in bwt_indices:
            out_f.write(struct.pack("<I", idx))


def read_header(in_f):
    magic = in_f.read(len(MAGIC))
    if magic != MAGIC:
        raise ValueError("Це не LZW файл (невірний MAGIC)")

    max_bits = read_uint8(in_f)
    mode_byte = read_uint8(in_f)

    if max_bits < 9 or max_bits > 16:
        raise ValueError(f"Некоректне max_bits={max_bits} (очікується 9..16)")

    overflow_mode = "freeze" if mode_byte == 0 else "reset"

    flags = read_uint8(in_f)
    block_size = struct.unpack("<I", in_f.read(4))[0]
    num_blocks = struct.unpack("<I", in_f.read(4))[0]

    indices = []
    if flags & FLAG_BWT:
        raw = in_f.read(num_blocks * 4)
        if len(raw) != num_blocks * 4:
            raise ValueError("Пошкоджений файл: не вистачає BWT-індексів")
        indices = list(struct.unpack("<" + "I" * num_blocks, raw))

    return max_bits, overflow_mode, flags, block_size, indices


def lzw_compress_bytes(data: bytes, fout, max_bits=16, overflow_mode="reset"):
    max_dict_size = 1 << max_bits  # FIX

    bs = BitStream(fout, "w")
    try:
        dictionary = {bytes([i]): i for i in range(256)}
        next_code = 256

        w = b""

        for byte_val in data:
            k = bytes([byte_val])
            wk = w + k

            if wk in dictionary:
                w = wk
            else:
                if w:
                    write_bits_fixed(bs, dictionary[w], max_bits)

                if next_code < max_dict_size:
                    dictionary[wk] = next_code
                    next_code += 1
                else:
                    if overflow_mode == "reset":
                        dictionary = {bytes([i]): i for i in range(256)}
                        next_code = 256
                

                w = k

        if w:
            write_bits_fixed(bs, dictionary[w], max_bits)

    finally:
        bs.close()


def lzw_decompress_bytes(fin, max_bits=16, overflow_mode="reset"):

    max_dict_size = 1 << max_bits
    bs = BitStream(fin, "r")

    dictionary = {i: bytes([i]) for i in range(256)}
    next_code = 256

    out = bytearray()

    try:
        try:
            prev_code = read_bits_fixed(bs, max_bits)
        except EOFError:
            return b""

        if prev_code not in dictionary:
            raise ValueError("Пошкоджені дані: перший код не в словнику")

        w = dictionary[prev_code]
        out.extend(w)

        while True:
            try:
                code = read_bits_fixed(bs, max_bits)
            except EOFError:
                break

            if code in dictionary:
                entry = dictionary[code]
            elif code == next_code:
                entry = w + w[:1]
            else:
                raise ValueError(f"Пошкоджені дані: зустріли невірний код {code}")

            out.extend(entry)

            if next_code < max_dict_size:
                dictionary[next_code] = w + entry[:1]
                next_code += 1
            else:
                if overflow_mode == "reset":
                    dictionary = {i: bytes([i]) for i in range(256)}
                    next_code = 256

            w = entry

    finally:
        bs.close()

    return bytes(out)


def lzw_compress(input_path, output_path=None, max_bits=16, overflow_mode="reset",
                 use_bwt=False, use_mtf=False, block_size=4096):

    if output_path is None:
        output_path = input_path + ".lzw"

    with open(input_path, "rb") as fin:
        data = fin.read()

    flags = 0
    bwt_indices = []

    if use_bwt:
        flags |= FLAG_BWT
        data, bwt_indices = bwt_encode(data, block_size=block_size)

    if use_mtf:
        flags |= FLAG_MTF
        data = mtf_encode(data)

    with open(output_path, "wb") as fout:
        write_header_lb5(
            fout, max_bits=max_bits, overflow_mode=overflow_mode,
            flags=flags, block_size=block_size, bwt_indices=bwt_indices
        )

        lzw_compress_bytes(data, fout, max_bits=max_bits, overflow_mode=overflow_mode)

    return output_path


def lzw_decompress(input_path, output_path=None):
    if output_path is None:
        if input_path.endswith(".lzw"):
            output_path = input_path[:-4]
        else:
            output_path = input_path + ".out"

    with open(input_path, "rb") as fin:
        max_bits, overflow_mode, flags, block_size, bwt_indices = read_header(fin)

        data = lzw_decompress_bytes(fin, max_bits=max_bits, overflow_mode=overflow_mode)

    if flags & FLAG_MTF:
        data = mtf_decode(data)

    if flags & FLAG_BWT:
        data = bwt_decode(data, bwt_indices, block_size=block_size)

    with open(output_path, "wb") as fout:
        fout.write(data)

    return output_path
