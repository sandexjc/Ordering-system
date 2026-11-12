"""

Draw a QR picture for a text string.
The result is an SVG document. The text is stored as bytes with error
correction level M, which can recover about 15 percent of a damaged
picture. Versions 1 through 10 hold up to 213 bytes. 


"""

# Level M, versions 1-10: (recovery bytes in one block, number of blocks).
_RECOVERY_M = {
    1: (10, 1),
    2: (16, 1),
    3: (26, 1),
    4: (18, 2),
    5: (24, 2),
    6: (16, 4),
    7: (18, 4),
    8: (22, 4),
    9: (22, 5),
    10: (26, 5),
}
# Bytes left for the message once those recovery blocks are set aside.
_DATA_BYTES_M = {
    1: 16,
    2: 28,
    3: 44,
    4: 64,
    5: 86,
    6: 108,
    7: 124,
    8: 154,
    9: 182,
    10: 216,
}
# Centers of the small alignment markers. Corners that sit on a finder are skipped.
_ALIGNMENT = {
    1: (),
    2: (6, 18),
    3: (6, 22),
    4: (6, 26),
    5: (6, 30),
    6: (6, 34),
    7: (6, 22, 38),
    8: (6, 24, 42),
    9: (6, 26, 46),
    10: (6, 28, 50),
}
# Finder-like streaks. A mask that paints these on its own is a poor choice.
_FINDER_SHAPES = (
    (1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0),
    (0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1),
)

_QUIET_MODULES = 4
_BYTE_MODE = 0b0100
_PAD_BYTES = (0xEC, 0x11)
_FIELD_POLYNOMIAL = 0x11D
_FORMAT_POLYNOMIAL = 0x537
_FORMAT_XOR = 0x5412
_VERSION_POLYNOMIAL = 0x1F25

_RECOVERY_GENERATORS = {}


def _build_field():
    # Powers of the QR Galois field, so recovery math is a table lookup.
    exponent = [0] * 512
    logarithm = [0] * 256
    value = 1
    for power in range(255):
        exponent[power] = value
        logarithm[value] = power
        value <<= 1
        if value & 0x100:
            value ^= _FIELD_POLYNOMIAL
    for power in range(255, 512):
        exponent[power] = exponent[power - 255]
    return exponent, logarithm


_EXPONENT, _LOGARITHM = _build_field()


def qr_svg(text):
    # Return an SVG document whose QR picture encodes text.
    if not isinstance(text, str):
        raise TypeError("QR text must be a string.")
    if text == "":
        raise ValueError("QR text is empty.")
    return _svg(_matrix(text.encode("utf-8")))


def _matrix(data):
    # Dark and light modules for data. The quiet zone is added by the SVG.
    version = _version_for(len(data))
    size = 21 + 4 * (version - 1)
    dark = [[False] * size for _ in range(size)]
    taken = [[False] * size for _ in range(size)]

    # Fixed patterns tell a scanner where the code sits and which version it is.
    _draw_finders(dark, taken, size)
    _draw_alignments(dark, taken, version)
    _draw_timing(dark, taken, size)
    dark[size - 8][8] = True
    taken[size - 8][8] = True
    _reserve_format(taken, size)
    if version >= 7:
        _reserve_version(taken, size)

    module_count = _module_count(version)
    free_modules = sum(not cell for row in taken for cell in row)
    if free_modules != module_count:
        raise RuntimeError("QR matrix does not match the version size.")

    # The message and its recovery bytes, as bits that fill every free module.
    codewords = _message_codewords(data, version)
    bits = _codeword_bits(_interleave(codewords, version), version)
    if len(bits) != module_count:
        raise RuntimeError("QR data does not fill the version.")
    _place_bits(dark, taken, bits)
    if version >= 7:
        _draw_version(dark, version, size)

    # Pick a mask, then write the format bits that name it. Those bits stay unmasked.
    mask = _chosen_mask(dark, taken, size)
    masked = _apply_mask(dark, taken, mask, size)
    _draw_format(masked, mask, size)
    return masked


def _version_for(byte_count):
    # Smallest version whose data capacity can hold byte_count.
    for version, data_bytes in _DATA_BYTES_M.items():
        count_bits = 8 if version <= 9 else 16
        header_bits = 4 + count_bits
        if byte_count <= (data_bytes * 8 - header_bits) // 8:
            return version
    raise ValueError("QR text is too long.")


def _module_count(version):
    # Modules available for the message, after finders, timing, and format areas.
    count = (16 * version + 128) * version + 64
    if version >= 2:
        markers = version // 7 + 2
        count -= (25 * markers - 10) * markers - 55
        if version >= 7:
            count -= 36
    return count


def _multiply(left, right):
    if left == 0 or right == 0:
        return 0
    return _EXPONENT[_LOGARITHM[left] + _LOGARITHM[right]]


def _recovery_generator(length):
    # Polynomial that produces `length` recovery bytes.
    cached = _RECOVERY_GENERATORS.get(length)
    if cached is not None:
        return cached
    generator = [1]
    for power in range(length):
        product = [0] * (len(generator) + 1)
        for index, coef in enumerate(generator):
            product[index] ^= coef
            product[index + 1] ^= _multiply(coef, _EXPONENT[power])
        generator = product
    _RECOVERY_GENERATORS[length] = generator
    return generator


def _recovery_bytes(data, length):
    # Each step uses the running remainder, which earlier steps have already changed.
    generator = _recovery_generator(length)
    remainder = list(data) + [0] * length
    for index in range(len(data)):
        coef = remainder[index]
        if coef == 0:
            continue
        for shift, factor in enumerate(generator[1:], start=1):
            remainder[index + shift] ^= _multiply(factor, coef)
    return remainder[-length:]


def _message_codewords(data, version):
    # Byte-mode header, the text, then the pad bytes that fill this version.
    bits = _bits(_BYTE_MODE, 4)
    count_width = 8 if version <= 9 else 16
    bits += _bits(len(data), count_width)
    for byte in data:
        bits += _bits(byte, 8)

    capacity = _DATA_BYTES_M[version] * 8
    bits += [0] * min(4, capacity - len(bits))
    if len(bits) % 8:
        bits += [0] * (8 - len(bits) % 8)
    pad_index = 0
    while len(bits) < capacity:
        bits += _bits(_PAD_BYTES[pad_index % 2], 8)
        pad_index += 1

    codewords = []
    for index in range(0, len(bits), 8):
        value = 0
        for bit in bits[index:index + 8]:
            value = (value << 1) | bit
        codewords.append(value)
    return codewords


def _bits(value, width):
    return [(value >> shift) & 1 for shift in range(width - 1, -1, -1)]


def _interleave(data, version):
    # Weave the blocks so one stain does not erase a whole block.
    recovery_length, block_count = _RECOVERY_M[version]
    short_length = len(data) // block_count
    short_blocks = block_count - (len(data) % block_count)
    blocks = []
    offset = 0
    for index in range(block_count):
        length = short_length if index < short_blocks else short_length + 1
        block = data[offset:offset + length]
        offset += length
        blocks.append((block, _recovery_bytes(block, recovery_length)))
    if offset != len(data):
        raise RuntimeError("QR blocks do not cover the data.")

    stream = []
    for index in range(short_length + 1):
        for block, _recovery in blocks:
            if index < len(block):
                stream.append(block[index])
    for index in range(recovery_length):
        for _block, recovery in blocks:
            stream.append(recovery[index])
    return stream


def _codeword_bits(codewords, version):
    bits = []
    for word in codewords:
        bits += _bits(word, 8)
    # A few versions need empty bits so the stream ends on the module grid.
    bits += [0] * (_module_count(version) % 8)
    return bits


def _draw_finders(dark, taken, size):
    # Three bullseye markers, each with a white module of separation.
    for top, left in ((0, 0), (0, size - 7), (size - 7, 0)):
        for row in range(7):
            for col in range(7):
                border = row in (0, 6) or col in (0, 6)
                center = 2 <= row <= 4 and 2 <= col <= 4
                dark[top + row][left + col] = border or center
                taken[top + row][left + col] = True
        for row in range(-1, 8):
            for col in range(-1, 8):
                if 0 <= row <= 6 and 0 <= col <= 6:
                    continue
                y = top + row
                x = left + col
                if 0 <= y < size and 0 <= x < size:
                    dark[y][x] = False
                    taken[y][x] = True


def _draw_alignments(dark, taken, version):
    positions = _ALIGNMENT[version]
    last = positions[-1] if positions else None
    for row in positions:
        for col in positions:
            if (row, col) in ((6, 6), (6, last), (last, 6)):
                continue
            for y in range(row - 2, row + 3):
                for x in range(col - 2, col + 3):
                    distance = max(abs(y - row), abs(x - col))
                    dark[y][x] = distance != 1
                    taken[y][x] = True


def _draw_timing(dark, taken, size):
    # Alternating row and column that a scanner uses to count modules.
    for index in range(size):
        if not taken[6][index]:
            dark[6][index] = index % 2 == 0
            taken[6][index] = True
        if not taken[index][6]:
            dark[index][6] = index % 2 == 0
            taken[index][6] = True


def _reserve_format(taken, size):
    # Keep the format cells empty until the mask has been chosen.
    for index in range(9):
        taken[8][index] = True
        taken[index][8] = True
    for index in range(8):
        taken[8][size - 1 - index] = True
        taken[size - 1 - index][8] = True


def _reserve_version(taken, size):
    for index in range(18):
        y = size - 11 + index % 3
        x = index // 3
        taken[y][x] = True
        taken[x][y] = True


def _place_bits(dark, taken, bits):
    # Walk two columns at a time, up then down, and skip the timing column.
    size = len(dark)
    bit_index = 0
    upward = True
    col = size - 1
    while col > 0:
        if col == 6:
            col -= 1
        rows = range(size - 1, -1, -1) if upward else range(size)
        for row in rows:
            for x in (col, col - 1):
                if taken[row][x]:
                    continue
                dark[row][x] = bool(bits[bit_index])
                bit_index += 1
        upward = not upward
        col -= 2
    if bit_index != len(bits):
        raise RuntimeError("QR data was not placed.")


def _format_bits(mask):
    # Level M is zero in the high bits. The mask number is the low three bits.
    remainder = mask
    for _ in range(10):
        remainder = (remainder << 1) ^ (_FORMAT_POLYNOMIAL if remainder >> 9 & 1 else 0)
    return ((mask << 10) | (remainder & 0x3FF)) ^ _FORMAT_XOR


def _version_bits(version):
    remainder = version
    for _ in range(12):
        remainder = (remainder << 1) ^ (_VERSION_POLYNOMIAL if remainder >> 11 & 1 else 0)
    return (version << 12) | (remainder & 0xFFF)


def _draw_format(dark, mask, size):
    # Two copies of the same 15 bits: by the top-left finder, and along the far edges.
    bits = _format_bits(mask)
    positions = [(8, col) for col in (0, 1, 2, 3, 4, 5, 7, 8)]
    positions += [(row, 8) for row in (7, 5, 4, 3, 2, 1, 0)]
    positions += [(size - 1 - row, 8) for row in range(7)]
    positions += [(8, size - 8 + col) for col in range(8)]
    for index, (row, col) in enumerate(positions):
        dark[row][col] = bool((bits >> (14 - (index % 15))) & 1)


def _draw_version(dark, version, size):
    bits = _version_bits(version)
    for index in range(18):
        bit = bool((bits >> index) & 1)
        y = size - 11 + index % 3
        x = index // 3
        dark[y][x] = bit
        dark[x][y] = bit


def _mask_inverts(mask, row, col):
    # True when this mask flips the data module at row, col.
    if mask == 0:
        return (row + col) % 2 == 0
    if mask == 1:
        return row % 2 == 0
    if mask == 2:
        return col % 3 == 0
    if mask == 3:
        return (row + col) % 3 == 0
    if mask == 4:
        return (row // 2 + col // 3) % 2 == 0
    if mask == 5:
        return (row * col) % 2 + (row * col) % 3 == 0
    if mask == 6:
        return ((row * col) % 2 + (row * col) % 3) % 2 == 0
    return ((row + col) % 2 + (row * col) % 3) % 2 == 0


def _apply_mask(dark, taken, mask, size):
    masked = [row[:] for row in dark]
    for row in range(size):
        for col in range(size):
            if taken[row][col]:
                continue
            if _mask_inverts(mask, row, col):
                masked[row][col] = not masked[row][col]
    return masked


def _chosen_mask(dark, taken, size):
    # Eight masks exist. Keep the one with the fewest awkward streaks.
    best_mask = 0
    best_score = None
    for mask in range(8):
        masked = _apply_mask(dark, taken, mask, size)
        _draw_format(masked, mask, size)
        score = _penalty(masked)
        if best_score is None or score < best_score:
            best_score = score
            best_mask = mask
    return best_mask


def _penalty(matrix):
    size = len(matrix)
    score = 0
    for row in matrix:
        score += _line_penalty(row)
        score += _finder_penalty(row)
    for col in range(size):
        column = [matrix[row][col] for row in range(size)]
        score += _line_penalty(column)
        score += _finder_penalty(column)
    for row in range(size - 1):
        for col in range(size - 1):
            color = matrix[row][col]
            same_block = (
                color == matrix[row][col + 1]
                and color == matrix[row + 1][col]
                and color == matrix[row + 1][col + 1]
            )
            if same_block:
                score += 3
    dark_modules = sum(sum(row) for row in matrix)
    balance = abs(dark_modules * 100 // (size * size) - 50) // 5
    return score + balance * 10


def _line_penalty(line):
    # Five or more modules of one color in a row are hard to scan.
    score = 0
    run = 1
    for index in range(1, len(line)):
        if line[index] == line[index - 1]:
            run += 1
            continue
        if run >= 5:
            score += 3 + run - 5
        run = 1
    if run >= 5:
        score += 3 + run - 5
    return score


def _finder_penalty(line):
    values = tuple(1 if cell else 0 for cell in line)
    width = len(_FINDER_SHAPES[0])
    score = 0
    for index in range(len(values) - width + 1):
        if values[index:index + width] in _FINDER_SHAPES:
            score += 40
    return score


def _svg(matrix):
    # White margin of four modules around the code, then one square per dark module.
    size = len(matrix)
    span = size + _QUIET_MODULES * 2
    squares = []
    for row, line in enumerate(matrix):
        for col, dark in enumerate(line):
            if dark:
                squares.append("M%d %dh1v1h-1z" % (col + _QUIET_MODULES, row + _QUIET_MODULES))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'shape-rendering="crispEdges">'
        '<rect width="%d" height="%d" fill="#fff"/>'
        '<path fill="#000" d="%s"/></svg>'
    ) % (span, span, span, span, "".join(squares))


def _check_tables():
    # Fail at import if a copied size table no longer matches the version rules.
    for version, expected in _DATA_BYTES_M.items():
        recovery_length, block_count = _RECOVERY_M[version]
        got = _module_count(version) // 8 - recovery_length * block_count
        if got != expected:
            raise RuntimeError("QR version %s data size is wrong." % version)
    if _format_bits(0) != 0x5412:
        raise RuntimeError("QR format bits are wrong.")
    if _version_bits(7) != 0x07C94:
        raise RuntimeError("QR version bits are wrong.")


_check_tables()
