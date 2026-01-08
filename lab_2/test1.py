with open("test.bin", "rb") as f:
    print([hex(b) for b in f.read()])
