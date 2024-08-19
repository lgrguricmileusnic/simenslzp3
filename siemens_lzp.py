from typing import Tuple

FW_PREAMBLE_SIZE = 0x90 # size of the firwmare preamble
FW_HEADER = b"A00000" # firmware section header
FW_ENDIANNESS = "little" # firmware endianness
FW_CHUNK_SIZE = 0x10000  # 64kB


def _binary(n: int, ms_first=True):
    """Generates binary digits of passed integer, starting from the most significant ones.
    :param n: integer for which digits will be generated
    """
    if (ms_first):
        for i in reversed(range(8)):
            yield n >> i & 0x01
    else:
        for i in range(8):
            yield n >> i & 0x01

def lzp_hash(context: bytes) -> int:
    """Calculates hash with lzp3 hash function.

    :param context: Bytes which will be hashed.
    :returns: hash(context)
    """
    context = int.from_bytes(context, "big")
    return ((context >> 15) ^ context) & 0xFFFF


def _read_bytes(i: int, size: int, src: bytes) -> Tuple[int, bytes]:
    """Reads size bytes from src starting from i and increases index i accordingly.

    :param i: start index
    :param size: number of bytes to read
    :param src: source
    :return: a 2 element tuple consisting of new i value and read bytes
    """
    rd = src[i: i + size]
    i += len(rd)
    return i, rd


def decompress_chunk(chunk: bytes) -> bytes:
    """Decompresses passed chunk. Assumed resulting chunk size is 64kB.

    :param chunk: chunk to be decompressed
    :return: decompressed chunk
    """
    
    # initialise hash table dict and output buffer
    hash_table = {}
    output = b""
    i = 0

    # read and output initial context
    i, context = _read_bytes(i, 4, chunk)
    output += context

    # hash intial context and update hash table
    hsh = lzp_hash(context)
    hash_table[hsh] = len(output)

    # loop while output is smaller than the maximum chunk size (64KB) and there is input data left
    while len(output) < FW_CHUNK_SIZE and i < len(chunk):
        # read mask byte and convert to binary string representation 
        i, mask = _read_bytes(i, 1, chunk)
        mask = mask[0]
        # for each bit in mask
        for b in _binary(mask):
            # read next octet from input
            i, current = _read_bytes(i, 1, chunk)
            # if there is no octet left, replace with 0xFF
            if len(current) < 1:
                current = b"\xFF"
                b = 0 # if no byte was read, set current byte to 0xFF and output it (padding)
            # get current context, length of output and current context hash
            context = output[-4:]
            loutput = len(output)
            hsh = lzp_hash(context)
            if b == 0:
                # current octet is a literal, output literal
                output += current
            else:
                # current octet is a match length, convert to integer value, and output match
                length = int.from_bytes(current, FW_ENDIANNESS)
                # get last occurence of context
                offset = hash_table[hsh]
                # output match
                for j in range(offset, offset + length):
                    output += output[j].to_bytes(1, FW_ENDIANNESS)
            
            #update 
            hash_table[hsh] = loutput
    
    
    # trim output to maximum chunk size
    if len(output) > FW_CHUNK_SIZE:
        output = output[:FW_CHUNK_SIZE]

    return output


def decompress(data: bytes) -> Tuple[int, bytes]:
    """Decompress data larger then one chunk size (64kB).

    :param data: data to decompress
    :return: a 2 element tuple containing number of read bytes from passed data and decompressed output
    """
    nread = 0 # number of read octets from input data
    output = b"" # output buffer
    while True:
        # read compressed chunk size
        nread, chunk_size_bytes = _read_bytes(nread, 4, data)
        if len(chunk_size_bytes) < 4:
            break
        chunk_size = int.from_bytes(chunk_size_bytes, FW_ENDIANNESS)
        # read compressed chunk
        nread, chunk = _read_bytes(nread, chunk_size, data)
        if len(chunk) < chunk_size:
            break
        # decompress chunk, skip first 2 bytes (unknown content)
        output += decompress_chunk(chunk[2:])
 
    return nread, output


def decompress_upddata(data: bytes) -> Tuple[bool, bytes]:
    """Wrapper for decompress() function. Prepares update file data for decompression.

    :param data: update file data
    :return: a two element tuple containing a boolean value and decompressed firmware from update file.
             Boolean is true if decompression was successful.
    """
    # retrieve offset where firmware section starts and the size of the compressed firmware section
    start_index, firmware_size, _ = extract_A0000_info(data)
    if start_index == -1:
        return False, b""
    firmware = data[start_index: start_index + firmware_size]

    # decompress firmware
    read_bytes, output = decompress(firmware)

    # if decompressor passed through the whole section, decompression is considered a success, return output
    return read_bytes == firmware_size, output


def extract_A0000_info(data: bytes) -> Tuple[int, int, int]:
    """Extracts firmware size, crc and start offset from update file data.

    :param data: update file data
    :return: a three element tuple containing start offset, size and crc32 value, or (-1, -1, 0) on failiure
    """
    # slice preamble from firmware
    fw_preamble = data[:FW_PREAMBLE_SIZE]
    # find indexes of the first and second occurrence of the firmware header"""

    # find offset at which A00000 metadata starts
    info_index = fw_preamble.find(FW_HEADER) - 8
    # find offset where A00000 section starts
    fw_start_index = fw_preamble.find(FW_HEADER, info_index + 9) + len(FW_HEADER)
    if info_index == -1 or fw_start_index == -1:
        return -1, -1, 0
    # read size and crc (4 bytes each, located before the first occurrence of the firmware header)
    firmware_size = int.from_bytes(fw_preamble[info_index: info_index + 4], FW_ENDIANNESS)
    firmware_crc = int.from_bytes(fw_preamble[info_index + 4: info_index + 8], FW_ENDIANNESS)
    return fw_start_index, firmware_size, firmware_crc
