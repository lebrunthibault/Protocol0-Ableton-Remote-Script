import traceback

from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song
from ClyphX_Pro.clyphx_pro.user_actions.utils.log import log_ableton


def print_except(func):
    def decorate(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            err = "ScriptError: " + str(e)
            args[0].canonical_parent.log_message(traceback.format_exc())
            args[0].canonical_parent.clyphx_pro_component.trigger_action_list('push msg "%s"' % err)

    return decorate


def init_song(func):
    def decorate(self, *args, **kwargs):
        try:
            if func.__name__ != "create_actions":
                self._my_song = Song(self._song)
                if not self._my_song.current_action_name:
                    self._my_song.current_action_name = func.__name__
                self.current_track = self.get_abstract_track(args[0]["track"]) if "get_abstract_track" in dir(
                    self) and isinstance(args[0], dict) and "track" in args[0] else None
            func(self, *args, **kwargs)
        except Exception as e:
            err = "ScriptError: " + str(e)
            self.canonical_parent.log_message(traceback.format_exc())
            self.canonical_parent.clyphx_pro_component.trigger_action_list('push msg "%s"' % err)

    return decorate


def unarm_other_tracks(func):
    def decorate(self, *args, **kwargs):
        try:
            if func.__name__ != "create_actions":
                self.unarm_other_tracks = True
                self._my_song.current_action_name = func.__name__
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
