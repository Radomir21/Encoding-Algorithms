import encode_base64
import sys

reverse_alphabet = {ch: i for i, ch in enumerate(encode_base64.alphabet )}

def print_invalid_char(line, pos, ch):
    print(f"Рядок {line}, символ {pos:02d}: Некоректний вхідний символ ('{ch}')")
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

    data_lines = []
    for idx, line in enumerate(lines, start=1):

        if line.lstrip().startswith("-"):
            continue

        if line.strip() == "":
            continue

        data_lines.append((idx, line))

    if not data_lines:
        print("Немає даних для декодування")
        sys.exit(0)

    last_real_line_index = data_lines[-1][0]

    for idx, line in data_lines:

        if "-" in line:
            pos = line.index("-") + 1
            print_invalid_char(idx, pos, "-")

        if idx != last_real_line_index and len(line) != 76:
            print_length_error(idx, len(line))

        if "=" in line and idx != last_real_line_index:
            pos = line.index("=") + 1
            print_padding_error(idx, pos)

        part = decode_line(line, idx)
        decoded.extend(part)

    for check_idx in range(last_real_line_index + 1, len(lines)):
        line = lines[check_idx]
        if not line.startswith("-") and line.strip():
            print_after_end_warning()

    with open(output_file, "wb") as f:
        f.write(decoded)

    print(f"Файл успішно декодовано -> {output_file}")



if __name__ == "__main__":

    #decode_file("input.base64", "decoded_file.txt")
    input_file = input("Введи ім'я закодованого файла: ").strip()

    if input_file.endswith(".base64"):
        suggested = 'output.base64'
        print(f"Запропоноване ім'я вихідного файла: {suggested}")
        answer = input("Використати це ім'я? (y/n): ").strip().lower()

        if answer == "y":
            output_file = suggested
        else:
            output_file = input("Введи ім'я вихідного файла: ").strip()
    else:
        output_file = input("Введи ім'я вихідного файла: ").strip()

    decode_file(input_file, output_file)