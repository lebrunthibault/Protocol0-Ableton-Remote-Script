import traceback

from ClyphX_Pro.clyphx_pro.user_actions._Song import Song


def print_except(func):
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            err = "ScriptError: " + str(e)
            args[0].canonical_parent.log_message(traceback.format_exc())
            args[0].canonical_parent.clyphx_pro_component.trigger_action_list('push msg "%s"' % err)

    return inner


def init_song(func):
    def decorate(self, *args, **kwargs):
        try:
            # tracks = [track for track in self.song().tracks if track != self.song().master_track and track not in self.song().return_tracks]
            # self.log(len(tracks))
            self._song = Song(self.song())
            func(self, *args, **kwargs)
        except Exception as e:
            err = "ScriptError: " + str(e)
            self.canonical_parent.log_message(traceback.format_exc())
            self.canonical_parent.clyphx_pro_component.trigger_action_list('push msg "%s"' % err)

    return decorate


def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:  # there's probably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate
