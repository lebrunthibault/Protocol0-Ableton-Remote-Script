import json
from functools import wraps
from pydoc import locate, classname

from typing import Any, Optional

from protocol0.application.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.domain.enums.AbstractEnum import AbstractEnum
from protocol0.domain.enums.SongDataEnum import SongDataEnum
from protocol0.domain.lom.song.SongDataError import SongDataError
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.utils import class_attributes
from protocol0.infra.System import System
from protocol0.my_types import Func, T

SYNCHRONIZABLE_CLASSE_NAMES = set()


def song_synchronizable_class(cls):
    # type: (T) -> T
    SYNCHRONIZABLE_CLASSE_NAMES.add(classname(cls, ""))
    return cls


def save_song_data(func):
    # type: (Func) -> Func
    @wraps(func)
    def decorate(*a, **k):
        # type: (Any, Any) -> None
        res = func(*a, **k)
        from protocol0 import Protocol0
        Protocol0.SELF.songDataManager.save()
        return res

    return decorate


class SongDataManager(AbstractControlSurfaceComponent):
    DEBUG = False

    SELECTED_SCENE_INDEX = None  # type: Optional[int]
    SELECTED_TRACK_INDEX = None  # type: Optional[int]
    LAST_MANUALLY_STARTED_SCENE_INDEX = None  # type: Optional[int]
    LAST_MANUALLY_STARTED_SCENE_BAR_POSITION = 0

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SongDataManager, self).__init__(*a, **k)
        self.restore_data()

    def save_song_and_tracks(self):
        # type: () -> None
        self.save()
        for track in self.song.simple_tracks:
            self.parent.trackDataManager.save(track=track)
        System.get_instance().save_set()

    def save(self):
        # type: () -> None
        for cls_fqdn in SYNCHRONIZABLE_CLASSE_NAMES:
            cls = locate(cls_fqdn)
            self.store_class_data(cls)

        # can happen on record e.g.
        if self.song.selected_scene:
            self.song.set_data(SongDataEnum.SELECTED_SCENE_INDEX.name, self.song.selected_scene.index)
        if self.song.selected_track:
            self.song.set_data(SongDataEnum.SELECTED_TRACK_INDEX.name, self.song.selected_track.index)

        self.song.set_data(SongDataEnum.MIDI_RECORDING_QUANTIZATION_CHECKED.name, self.song.midi_recording_quantization_checked)

        from protocol0.domain.lom.scene.Scene import Scene

        if Scene.LAST_MANUALLY_STARTED_SCENE:
            self.song.set_data(SongDataEnum.LAST_MANUALLY_STARTED_SCENE_INDEX.name, Scene.LAST_MANUALLY_STARTED_SCENE.index)
            self.song.set_data(SongDataEnum.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION.name, Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION)

    def store_class_data(self, cls):
        # type: (Any) -> None
        attributes = class_attributes(cls)
        self.song.set_data(classname(cls, ""), attributes)

    def restore_data(self):
        # type: () -> None
        try:
            self._restore_data()
        except SongDataError as e:
            self.parent.log_error(str(e))
            self.parent.log_info("setting %s song data to {}")
            self.clear()
            raise Protocol0Warning("Inconsistent song data please save the set")

    def _restore_data(self):
        # type: () -> None
        if len(list(SYNCHRONIZABLE_CLASSE_NAMES)) == 0:
            self.parent.log_error("no song synchronizable class detected")
            return

        for cls_fqdn in SYNCHRONIZABLE_CLASSE_NAMES:
            self._restore_synchronizable_class_data(cls_fqdn)

        SongDataManager.SELECTED_SCENE_INDEX = self.song.get_data(SongDataEnum.SELECTED_SCENE_INDEX.name, None)
        SongDataManager.SELECTED_TRACK_INDEX = self.song.get_data(SongDataEnum.SELECTED_TRACK_INDEX.name, None)
        SongDataManager.LAST_MANUALLY_STARTED_SCENE_INDEX = self.song.get_data(SongDataEnum.LAST_MANUALLY_STARTED_SCENE_INDEX.name, None)
        SongDataManager.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION = self.song.get_data(SongDataEnum.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION.name, None)

        self.song.midi_recording_quantization_checked = self.song.get_data(SongDataEnum.MIDI_RECORDING_QUANTIZATION_CHECKED.name, False)

    def _restore_synchronizable_class_data(self, cls_fqdn):
        # type: (str) -> None
        cls = locate(cls_fqdn)
        if not cls:
            self.parent.log_error("Couldn't locate %s" % cls_fqdn)
            return
        class_data = self.song.get_data(cls_fqdn, {})
        if self.DEBUG:
            self._log(cls_fqdn, class_data)
        if not isinstance(class_data, dict):
            raise SongDataError("%s song data : expected dict, got %s" % (cls_fqdn, class_data))

        for key, value in class_data.items():
            if AbstractEnum.is_json_enum(value):
                try:
                    value = AbstractEnum.from_json_dict(value)
                except Protocol0Error as e:
                    raise SongDataError(e)
            if not hasattr(cls, key):
                self.parent.log_warning("Invalid song data, attribute does not exist %s.%s" % (cls.__name__, key))
                continue
            if isinstance(getattr(cls, key), AbstractEnum) and not isinstance(value, AbstractEnum):
                raise SongDataError("inconsistent AbstractEnum value for %s.%s : got %s" % (cls_fqdn, key, value))
            setattr(cls, key, value)

    def _log(self, key, value):
        # type: (str, Any) -> None
        self.parent.log_info("song data of %s: %s" % (key, json.dumps(value, indent=4, sort_keys=True)))

    def clear(self):
        # type: () -> None
        for cls_fqdn in SYNCHRONIZABLE_CLASSE_NAMES:
            self.parent.log_info("Clearing song data of %s" % cls_fqdn)
            self.song.set_data(cls_fqdn, {})