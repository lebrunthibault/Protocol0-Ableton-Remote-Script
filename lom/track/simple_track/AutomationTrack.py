from collections import OrderedDict

import Live

from _Framework.SubjectSlot import subject_slot_group
from _Framework.Util import find_if
from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.utils.decorators import defer, debounce
from a_protocol_0.utils.utils import find_last


class AutomationTrack(SimpleTrack):
    def __init__(self, *a, **k):
        super(AutomationTrack, self).__init__(*a, **k)
        self.push2_selected_main_mode = 'clip'
        self.push2_selected_matrix_mode = 'note'
        self.push2_selected_instrument_mode = 'split_melodic_sequencer'

    def _added_track_init(self):
        """ this can be called once, when the Live track is created """
        if self.group_track is None:
            raise "An automation track should always be grouped"
        [self.delete_device(d) for d in self.devices]
        self.output_routing_type = find_if(lambda r: r.attached_object == self.group_track._track,
                                            self.available_output_routing_types)
        self.parent.defer(lambda: setattr(self, "output_routing_channel", find_last(lambda r: "lfotool" in r.display_name.lower(),
                                                                    self.available_output_routing_channels)))
        if len(self.clips) == 0:
            self._create_base_clips()

    @defer
    def _create_base_clips(self):
        velocity_patterns = OrderedDict()
        velocity_patterns["dry"] = lambda i: 127
        velocity_patterns["half-silent"] = lambda i: 0 if i < 4 else 127
        velocity_patterns["half-reversed"] = lambda i: 127 if i < 4 else 0
        velocity_patterns["quarter-silent"] = lambda i: 0 if i < 2 else 127

        for i, (clip_name, vel_predicate) in enumerate(velocity_patterns.items()):
            self.create_clip(slot_number=i, name=clip_name, bar_count=1, notes_callback=self._fill_equal_notes, note_count=8, vel_predicate=vel_predicate)

        self.clip_slots[0]._has_clip_listener._callbacks.append(lambda: self.play())

    def _fill_equal_notes(self, clip, note_duration, note_count, vel_predicate):
        return [Note(pitch=vel_predicate(step), start=step * note_duration, duration=note_duration, clip=clip) for step in range(note_count)]

    @subject_slot_group("notes")
    def _clip_notes_listener(self, clip):
        # type: (Live.Clip.Clip) -> None
        self._map_notes(self.get_clip(clip))

    @debounce(2)
    def _map_notes(self, clip):
        # type: (Clip) -> None
        notes = clip.get_notes()
        if len(notes) == 0 or clip._is_updating_notes:
            return
        if len(clip.notes_changed(notes, ["start", "duration", "pitch"])) == 0:
            [setattr(note, "pitch", note.velocity) for (_, note) in clip.notes_changed(notes, ["velocity"])]
            clip._notes = notes  # no change should be triggered now
            return

        Note.auto_sync_enabled = False
        filtered_notes = []
        last_note = None
        for note in notes:
            if len(filtered_notes) == 0:
                filtered_notes.append(note)
                continue

            last_note = filtered_notes[-1]

            # do not allow chords
            if note.start == last_note.start:
                continue

            if note.start - last_note.start != last_note.duration:
                last_note.duration = note.start - last_note.start

            filtered_notes.append(note)

        last_note = filtered_notes[-1]
        if clip.length - last_note.start != last_note.duration:
            last_note.duration = clip.length - last_note.start

        [setattr(note, "pitch", note.velocity) for note in filtered_notes]
        clip.replace_all_notes(filtered_notes)
        Note.auto_sync_enabled = True
