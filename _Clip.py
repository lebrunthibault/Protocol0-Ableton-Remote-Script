class Clip:
    def __init__(self, clip, index):
        self.clip = clip
        self.index = index

    @property
    def length(self):
        return self.clip.length

    @property
    def name(self):
        return self.clip.name
