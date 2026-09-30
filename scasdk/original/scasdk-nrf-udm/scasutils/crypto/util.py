def xor(s1, s2):
    """
    Exclusive-Or of two byte arrays

    Args:
        s1 (bytes): first set of bytes
        s2 (bytes): second set of bytes
    Returns:
        (bytes) s1 ^ s2
    Raises:
        ValueError if s1 and s2 lengths don't match
    """
    if len(s1) != len(s2):
        raise ValueError('Input not equal length: %d %d' % (len(s1), len(s2)))
    return bytes(a ^ b for a, b in zip(s1, s2))


def rotate(input_s, bytes_):
    """
    Rotate a string by a number of bytes

    Args:
        input_s (bytes): the input string
        bytes_ (int): the number of bytes to rotate by
    Returns:
        (bytes) s1 rotated by n bytes
    """
    return bytes(
        input_s[(i + bytes_) % len(input_s)] for i in range(
            len(
                input_s,
            ),
        )
    )