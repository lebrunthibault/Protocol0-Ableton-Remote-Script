import os
from functools import partial

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.LoadDeviceCommand import LoadDeviceCommand
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Config import Config
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class DrumsTrack(NormalGroupTrack):
    DEFAULT_NAME = "Drums"

    def __init__(self, base_group_track):
        # type: (SimpleTrack) -> None
        super(DrumsTrack, self).__init__(base_group_track)
        self.categories = [d.lower() for d in os.listdir(Config.SAMPLE_PATH) if not d.startswith("_")]

    @property
    def computed_base_name(self):
        # type: () -> str
        return self.DEFAULT_NAME

    def add_track(self, name):
        # type: (str) -> Sequence
        name = name.lower()
        if name not in self.categories:
            raise Protocol0Warning("Cannot fin category for drum track %s" % name)

        Logger.dev("adding track %s" % name)

        self.is_folded = False

        selected_scene_index = SongFacade.selected_scene().index
        seq = Sequence()
        seq.add(partial(self._song.create_midi_track, self.sub_tracks[-1].index))
        seq.add(partial(CommandBus.dispatch, LoadDeviceCommand(DeviceEnum.SIMPLER.name)))
        seq.defer()
        seq.add(partial(self._on_track_added, name, selected_scene_index))
        return seq.done()

    def _on_track_added(self, name, selected_scene_index):
        # type: (str, int) -> None
        SongFacade.selected_track().volume -= 15
        SongFacade.selected_track().instrument.preset_list.set_selected_category(name)
        SongFacade.selected_track().instrument.scroll_presets(True)
        SongFacade.selected_track().clip_slots[selected_scene_index].create_clip()
        # DomainEventBus.notify(SongStateUpdatedEvent())
