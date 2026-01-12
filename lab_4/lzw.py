from bit_stream import BitStream

MAGIC = b"RADOMYR21"


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
        bit = bs.read_bit()  # може кинути EOFError
        value |= (bit << i)
    return value


def write_header(out_f, max_bits, overflow_mode):
    out_f.write(MAGIC)
    write_uint8(out_f, max_bits)

    mode_byte = 0 if overflow_mode == "freeze" else 1
    write_uint8(out_f, mode_byte)


def read_header(in_f):
    magic = in_f.read(4)
    if magic != MAGIC:
        raise ValueError("Це не LZW файл (невірний MAGIC)")

    max_bits = read_uint8(in_f)
    mode_byte = read_uint8(in_f)

    if max_bits < 9 or max_bits > 16:
        raise ValueError(f"Некоректне max_bits={max_bits} (очікується 9..16)")

    overflow_mode = "freeze" if mode_byte == 0 else "reset"
    return max_bits, overflow_mode


def lzw_compress(input_path, output_path=None, max_bits=16, overflow_mode="reset"):
    max_dict_size = 2^max_bits

    if output_path is None:
        output_path = input_path + ".lzw"

    with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
        write_header(fout, max_bits, overflow_mode)
        bs = BitStream(fout, "w")

        dictionary = {bytes([i]): i for i in range(256)}
        next_code = 256

        w = b""

        while True:
            chunk = fin.read(4096)
            if not chunk:
                break

            for byte_val in chunk:
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

        bs.close()

    return output_path


def lzw_decompress(input_path, output_path=None):
    if output_path is None:
        if input_path.endswith(".lzw"):
            output_path = input_path[:-4]
        else:
            output_path = input_path + ".out"

    with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
        max_bits, overflow_mode = read_header(fin)
        max_dict_size = 1 << max_bits

        bs = BitStream(fin, "r")

        dictionary = {i: bytes([i]) for i in range(256)}
        next_code = 256

        try:
            prev_code = read_bits_fixed(bs, max_bits)
        except EOFError:
            return output_path

        if prev_code not in dictionary:
            raise ValueError("Пошкоджені дані: перший код не в словнику")

        w = dictionary[prev_code]
        fout.write(w)

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

            fout.write(entry)

            if next_code < max_dict_size:
                dictionary[next_code] = w + entry[:1]
                next_code += 1
            else:
                if overflow_mode == "reset":
                    dictionary = {i: bytes([i]) for i in range(256)}
                    next_code = 256

            w = entry

        bs.close()

    return output_path
