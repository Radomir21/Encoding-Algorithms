import encode_base64
import sys

reverse_alphabet = {ch: i for i, ch in enumerate(encode_base64.alphabet )}

def print_invalid_char(line, pos, ch):
    print(f"Рядок {line}, символ {pos:02d}: Некоректний вхідний символ (`{ch}`)")
    sys.exit(0)

def print_padding_error(line, pos):
    print(f"Рядок {line}, символ {pos:02d}: Неправильне використання паддінгу")
    sys.exit(0)

def print_length_error(line, length):
    print(f"Рядок {line}: Некоректна довжина рядка ({length})")
    sys.exit(0)

def print_after_end_warning():
    print("Наявні дані після кінця повідомлення")
    sys.exit(0)

# Декодування одного рядка (без коментаря)
def decode_line(line: str, line_num: int) -> bytes:

    if len(line) % 4 != 0:
        print_length_error(line_num, len(line))

    if "=" in line:
        eq_index = line.index("=")
        if line.rstrip("=") != line[:eq_index]:
            print_padding_error(line_num, eq_index + 1)

    for i, ch in enumerate(line, start=1):
        if ch == "=":
            continue
        if ch not in reverse_alphabet:
            print_invalid_char(line_num, i, ch)

    result = bytearray()

    for i in range(0, len(line), 4):
        block = line[i:i+4]
        y = []
        padding = block.count("=")

        for ch in block:
            y.append(0 if ch == "=" else reverse_alphabet[ch])

        x1 = (y[0] << 2) | (y[1] >> 4)
        x2 = ((y[1] & 0b1111) << 4) | (y[2] >> 2)
        x3 = ((y[2] & 0b11) << 6) | y[3]

        if padding == 0:
            result.extend([x1, x2, x3])
        elif padding == 1:
            result.extend([x1, x2])
        elif padding == 2:
            result.extend([x1])
        else:
            print_padding_error(line_num, i+1)

    return bytes(result)


def decode_file(input_file, output_file):
    decoded = bytearray()

    with open(input_file, "r", encoding="ascii") as f:
        lines = f.read().splitlines()

    last_data_line = None

    for idx, line in enumerate(lines, start=1):

        if line.startswith("-"):
            continue

        if line.strip() == "":
            continue

        if len(line) != 76 and idx != len(lines):
            print_length_error(idx, len(line))

        if "=" in line and idx != len(lines):
            pos = line.index("=") + 1
            print_padding_error(idx, pos)

        part = decode_line(line, idx)
        decoded.extend(part)

        last_data_line = idx

    if last_data_line is not None:
        for extra in range(last_data_line + 1, len(lines)):
            if not lines[extra].startswith("-") and lines[extra].strip():
                print_after_end_warning()
                break

    with open(output_file, "wb") as f:
        f.write(decoded)

    print(f"Файл успішно декодовано -> {output_file}")


if __name__ == "__main__":

    decode_file("output.base64", "decode_file.txt")
