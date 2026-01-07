alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+\\"

def ensure_valid_comment(comment: str) -> str:

    if not comment.startswith("-"):
        raise ValueError("Коментар повинен починатися зі знака '-'")

    if len(comment) > 76:
        raise ValueError("Коментар занадто довгий (макс 76 символів)")


def split_lines_76(encoded: str) -> str:

    lines = []
    for i in range(0, len(encoded), 76):
        line = encoded[i:i+76]
        if len(line) == 0:
            continue
        if len(line) > 76:
            raise ValueError("Довжина рядка перевищує 76 символів")
        lines.append(line)
    return lines


def encode_bytes(data: bytes) -> str:

    encoded_str = ''
    for i in range(0, len(data), 3):
        triple = data[i:i+3]
        bytes = list(triple)
        padding = 3 - len(bytes)
        bytes += [0] * padding

        x_1, x_2, x_3 = bytes

        y_1 = x_1 >> 2
        y_2 = ((x_1 & 0b11) << 4) | (x_2 >> 4)
        y_3 = ((x_2 & 0b1111) << 2) | (x_3 >> 6)
        y_4 = x_3 & 0b111111

        block = [alphabet[y_1], alphabet[y_2], alphabet[y_3] if len(triple) > 1 else '=', alphabet[y_4] if len(triple) > 2 else '=']
          
        encoded_str += "".join(block)
    
    return encoded_str

def encode_file(input_file, output_file=None,comment=None):
    
    if output_file is None:
        output_file = input_file + ".base64"

    with open(input_file, "rb") as file:
        data = file.read()

    encode_str = encode_bytes(data)
    lines = split_lines_76(encode_str)

    with open(output_file, "w", encoding="ASCII") as file:
        if comment is not None:
            ensure_valid_comment(comment)
            file.write(comment + "\n")

        for line in lines:
            file.write(line + "\n")

    print(f"Файл успішно закодовано -> {output_file}")



if __name__ == "__main__":
    
    input_file = input("Введи ім'я вхідного файла: ").strip()
    output_file = input("Введи ім'я вихідного файла (або Enter): ").strip()
    output_file = output_file if output_file else None

    encode_file(input_file, output_file, comment="-my comments")



   




    








        