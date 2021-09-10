
class Bounce:
    def __init__(self):
        self.idx = 0
        self.dest = 1

    def __call__(self, buffer):
        buffer_len = len(buffer)

        for idx in range(buffer_len):
            buffer[idx] = idx == self.idx

        self.idx += self.dest
        if self.idx == 0:
            self.dest = 1
        elif self.idx == (buffer_len - 1):
            self.dest = -1


class Chaser:
    def __init__(self):
        self.step = 0

    def __call__(self, buffer):
        buffer_len = len(buffer)
        step = self.step
        for idx in range(buffer_len):
            buffer[buffer_len - 1 - idx] = not bool((step - idx) % 3)

        self.step = (step + 1) % buffer_len


class Snake:
    def __init__(self, length=28, slither=-2):
        self.step = 0
        self.start = 0
        self.len = length
        self.slither = slither

    def __call__(self, buffer):
        buffer_len = len(buffer)

        start = self.start
        end = start + self.len

        for idx in range(buffer_len):
            buffer[idx] = (start <= idx < end)

        if end == self.slither:
            self.start = buffer_len
        else:
            self.start -= 1

