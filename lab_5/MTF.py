def mtf_encode(data: bytes):
    alphabet = list(range(256))
    out = bytearray()

    for b in data:
        pos = alphabet.index(b)
        out.append(pos)
        alphabet.pop(pos)
        alphabet.insert(0, b)

    return bytes(out)


def mtf_decode(data: bytes):
    alphabet = list(range(256))
    out = bytearray()

    for pos in data:
        b = alphabet[pos]
        out.append(b)
        alphabet.pop(pos)
        alphabet.insert(0, b)

    return bytes(out)
