from protocol0.domain.enums.AbstractEnum import AbstractEnum


class TrackSearchKeywordEnum(AbstractEnum):
    KICK = "KICK"
    SNARE = "SNARE"
    CLAP = "CLAP"
    RIDE = "RIDE"
    HAT = "HAT"
    CRASH = "CRASH"
    BASS = "BASS"
    SERUM = "SERUM"
    PROPHET = "PROPHET"
    PIANO = "PIANO"
    MASTER = "MASTER"

    @property
    def search_value(self):
        # type: () -> str
        return self.value.lower().strip()
