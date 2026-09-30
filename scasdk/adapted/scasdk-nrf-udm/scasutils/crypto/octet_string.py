class OctetString:

    def __init__(self, data=None):
        if data is None:
            self.m_data = bytearray()
        else:
            self.m_data = bytearray(data)

    def append(self, v):
        if isinstance(v, OctetString):
            self.m_data.extend(v.data())
        else:
            self.m_data.append(v)

    def append_utf8(self, v):
        utf8_bytes = v.encode('utf-8')
        self.m_data.extend(utf8_bytes)

    def append_octet(self, v):
        self.m_data.append(v)

    def append_octet2(self, v):
        self.m_data.extend([v >> 8, v & 0xFF])

    def append_octet3(self, v):
        self.m_data.extend([v >> 16, (v >> 8) & 0xFF, v & 0xFF])

    def append_octet4(self, v):
        self.m_data.extend([v >> 24, (v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF])

    def append_octet8(self, v):
        self.m_data.extend([v >> 56, (v >> 48) & 0xFF, (v >> 40) & 0xFF, (v >> 32) & 0xFF, (v >> 24) & 0xFF, (v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF])

    def append_padding(self, length):
        self.m_data.extend([0] * length)

    def data(self):
        return bytes(self.m_data)

    def length(self):
        return len(self.m_data)

    def get(self, index):
        return self.m_data[index]

    def get2(self, index):
        return (self.m_data[index] << 8) | self.m_data[index + 1]

    def get3(self, index):
        return (self.m_data[index] << 16) | (self.m_data[index + 1] << 8) | self.m_data[index + 2]

    def get4(self, index):
        return (self.m_data[index] << 24) | (self.m_data[index + 1] << 16) | (self.m_data[index + 2] << 8) | self.m_data[index + 3]

    def get8(self, index):
        return (self.m_data[index] << 56) | (self.m_data[index + 1] << 48) | (self.m_data[index + 2] << 40) | (self.m_data[index + 3] << 32) | (self.m_data[index + 4] << 24) | (self.m_data[index + 5] << 16) | (self.m_data[index + 6] << 8) | self.m_data[index + 7]

    def to_hex_string(self):
        return ''.join(format(byte, '02x') for byte in self.m_data)

    def copy(self):
        return OctetString(self.m_data[:])

    def sub_copy1(self, index):
        return OctetString(self.m_data[index:])

    def sub_copy(self, index, length):
        return OctetString(self.m_data[index:index + length])

    def __eq__(self, other):
        return self.m_data == other.m_data

    def __ne__(self, other):
        return self.m_data != other.m_data

    @staticmethod
    def empty():
        return OctetString()

    @staticmethod
    def from_hex(hex_string):
        hex_bytes = bytes.fromhex(hex_string)
        return OctetString(hex_bytes)

    @staticmethod
    def from_ascii(ascii_string):
        return OctetString(ascii_string.encode('ascii'))

    @staticmethod
    def from_array(arr):
        return OctetString(arr)

    @staticmethod
    def from_spare(length):
        return OctetString([0] * length)

    @staticmethod
    def from_octet(value):
        return OctetString([value])

    @staticmethod
    def from_octet2(value):
        return OctetString([value >> 8, value & 0xFF])

    @staticmethod
    def from_octet4(value):
        return OctetString([value >> 24, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])

    @staticmethod
    def from_octet8(value):
        return OctetString([value >> 56, (value >> 48) & 0xFF, (value >> 40) & 0xFF, (value >> 32) & 0xFF, (value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])

    @staticmethod
    def concat(a, b):
        return OctetString(a.m_data + b.m_data)
