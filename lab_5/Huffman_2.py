# huffman_lb5.py
import heapq
import struct

from bit_stream import BitStream
from BWT import bwt_encode, bwt_decode
from MTF import mtf_encode, mtf_decode

MAGIC = b"RAD2"  

FLAG_BWT = 1
FLAG_MTF = 2


def make_node(freq, symbol=None, left=None, right=None):
    return [freq, symbol, left, right]


def is_leaf(node):
    return node[1] is not None


def build_frequency_table(data):
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    return freq


def build_huffman_tree(freq):
    heap = []
    uid = 0

    for sym in range(256):
        f = freq[sym]
        if f > 0:
            heap.append((f, uid, make_node(f, sym)))
            uid += 1

    heapq.heapify(heap)

    if len(heap) == 0:
        return None
    if len(heap) == 1:
        return heap[0][2]

    while len(heap) > 1:
        f1, _, n1 = heapq.heappop(heap)
        f2, _, n2 = heapq.heappop(heap)
        parent = make_node(f1 + f2, None, n1, n2)
        heapq.heappush(heap, (f1 + f2, uid, parent))
        uid += 1

    return heap[0][2]


def build_code_table(root):
    codes = {}
    if root is None:
        return codes

    if is_leaf(root):
        codes[root[1]] = "0"
        return codes

    def dfs(node, path):
        if is_leaf(node):
            codes[node[1]] = path
            return
        if node[2] is not None:
            dfs(node[2], path + "0")
        if node[3] is not None:
            dfs(node[3], path + "1")

    dfs(root, "")
    return codes


def write_freq_table(fout, freq):
    for f in freq:
        fout.write(struct.pack("<I", f))


def read_freq_table(fin):
    raw = fin.read(1024)
    if len(raw) != 1024:
        raise ValueError("Нет таблицы частот (1024 байта).")
    return list(struct.unpack("<256I", raw))


def _write_header(fout, flags: int, block_size: int, bwt_indices):

    fout.write(MAGIC)
    fout.write(struct.pack("<B", flags))
    fout.write(struct.pack("<I", block_size))

    num_blocks = len(bwt_indices) if bwt_indices is not None else 0
    fout.write(struct.pack("<I", num_blocks))

    if flags & FLAG_BWT:
        for idx in bwt_indices:
            fout.write(struct.pack("<I", idx))


def _read_header(fin):
    magic = fin.read(4)
    if magic != MAGIC:
        raise ValueError("Некорректный формат архива (MAGIC не совпадает).")

    flags = struct.unpack("<B", fin.read(1))[0]
    block_size = struct.unpack("<I", fin.read(4))[0]
    num_blocks = struct.unpack("<I", fin.read(4))[0]

    indices = []
    if flags & FLAG_BWT:
        raw = fin.read(num_blocks * 4)
        if len(raw) != num_blocks * 4:
            raise ValueError("Повреждён архив: не хватает BWT-индексов.")
        indices = list(struct.unpack("<" + "I" * num_blocks, raw))

    return flags, block_size, indices


def encode_file(input_path, output_path=None, use_bwt=False, use_mtf=False, block_size=4096):

    if output_path is None:
        output_path = input_path + ".huff2"

    with open(input_path, "rb") as f:
        data = f.read()

    flags = 0
    bwt_indices = None


    if use_bwt:
        flags |= FLAG_BWT
        data, bwt_indices = bwt_encode(data, block_size=block_size)

    if use_mtf:
        flags |= FLAG_MTF
        data = mtf_encode(data)

  
    freq = build_frequency_table(data)
    root = build_huffman_tree(freq)
    codes = build_code_table(root)

    with open(output_path, "wb") as fout:
   
        _write_header(fout, flags, block_size, bwt_indices)


        write_freq_table(fout, freq)


        bs = BitStream(fout, "w")
        try:
            for b in data:
                code = codes[b]
                for ch in code:
                    bs.write_bit(1 if ch == "1" else 0)
        finally:
            bs.close()

    return output_path


def decode_file(input_path, output_path=None):

    if output_path is None:
        if input_path.endswith(".h5"):
            output_path = input_path[:-3]
        else:
            output_path = input_path + ".out"

    with open(input_path, "rb") as fin:
   
        flags, block_size, bwt_indices = _read_header(fin)

        freq = read_freq_table(fin)
        total = sum(freq)
        root = build_huffman_tree(freq)

        if total == 0:
            with open(output_path, "wb") as fout:
                fout.write(b"")
            return output_path

        if root is None:
            raise ValueError("Архив битый: дерево не построилось.")

        bs = BitStream(fin, "r")
        decoded = bytearray()

        if is_leaf(root):
            decoded.extend([root[1]] * total)
        else:
            node = root
            written = 0
            while written < total:
                bit = bs.read_bit()
                node = node[3] if bit == 1 else node[2]
                if node is None:
                    raise ValueError("Архив битый: неверный битовый поток.")
                if is_leaf(node):
                    decoded.append(node[1])
                    written += 1
                    node = root

        bs.close()

    data = bytes(decoded)

    if flags & FLAG_MTF:
        data = mtf_decode(data)

    if flags & FLAG_BWT:
        data = bwt_decode(data, bwt_indices, block_size=block_size)

    with open(output_path, "wb") as fout:
        fout.write(data)

    return output_path
