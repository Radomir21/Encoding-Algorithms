def bwt_encode_block(block: bytes):
    n = len(block)
    if n == 0:
        return b"", 0

    rotations = list(range(n))

    rotations.sort(key=lambda i: block[i:] + block[:i])

    primary_index = rotations.index(0)

    L = bytes(block[(i - 1) % n] for i in rotations)
    return L, primary_index


def bwt_decode_block(L: bytes, primary_index: int):

    n = len(L)
    if n == 0:
        return b""

    counts = [0] * 256
    rank = [0] * n
    for i, ch in enumerate(L):
        counts[ch] += 1
        rank[i] = counts[ch] - 1

    first_pos = [0] * 256
    total = 0
    for c in range(256):
        if counts[c] > 0:
            first_pos[c] = total
            total += counts[c]

    res = bytearray(n)
    idx = primary_index
    for k in range(n - 1, -1, -1):
        ch = L[idx]
        res[k] = ch
        idx = first_pos[ch] + rank[idx]

    return bytes(res)


def bwt_encode(data: bytes, block_size: int = 4096):

    out = bytearray()
    indices = []

    for start in range(0, len(data), block_size):
        block = data[start:start + block_size]
        L, idx = bwt_encode_block(block)
        out.extend(L)
        indices.append(idx)

    return bytes(out), indices


def bwt_decode(data: bytes, indices, block_size: int = 4096):

    out = bytearray()
    pos = 0
    block_id = 0

    while pos < len(data):
        block = data[pos:pos + block_size]
        idx = indices[block_id]
        out.extend(bwt_decode_block(block, idx))
        pos += block_size
        block_id += 1

    return bytes(out)
