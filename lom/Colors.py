from a_protocol_0.consts import GROUP_PROPHET_NAME, GROUP_MINITAUR_NAME


class Colors(object):
    ARM = 14
    DISABLED = 13

    @staticmethod
    def has(key):
        # type: (str) -> bool
        return hasattr(Colors, key)


setattr(Colors, GROUP_PROPHET_NAME, 23)
setattr(Colors, GROUP_MINITAUR_NAME, 69)
