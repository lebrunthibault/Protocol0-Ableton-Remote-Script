from os import listdir
from os.path import isfile, join, isdir

import Live

from a_protocol_0.consts import SAMPLE_PATH
from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument


class InstrumentSimpler(AbstractInstrument):
    def action_show(self):
        # type: () -> None
        pass

    def _do_load_item(self, item, header='Device'):
        """ Handles loading an item and displaying load info in status bar. """
        if item and item.is_loadable:
            self.song.view.selected_track.view.device_insert_mode = Live.Track.DeviceInsertMode.default
            self.parent.show_message('Loading %s: %s' % (header, item.name))
            self.browser.load_item(item)

    def _get_item_for_category(self, category, item):
        """ Returns the cached item for the category. """
        self._cache_category(category)
        return self._cached_browser_items[category].get(item, None)

    def _cache_category(self, category):
        """ This will cache an entire dict of items for the category if one doesn't
        already exist. """
        if category == 'user_library' and self._cached_browser_items.get(category, None):
            self._cached_browser_items[category] = {}
        if not self._cached_browser_items.get(category, None):
            self._cached_browser_items[category] = {}
            self._get_children_for_item(getattr(self.browser, category), self._cached_browser_items[category])
        return

    def _get_children_for_item(self, item, i_dict, is_drum_rack=False):
        """ Recursively builds dict of children items for the given item. This is needed
        to deal with children that are folders. If is_drum_rack, will only deal with
        racks in the root (not drum hits). """
        for i in item.iter_children:
            if i.is_folder or not i.is_loadable:
                if is_drum_rack:
                    continue
                self._get_children_for_item(i, i_dict)
            elif not is_drum_rack or i.name.endswith('.adg'):
                i_dict[i.name] = i

    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> None
        sample_path = join(SAMPLE_PATH, self.track.base_name)
        if not isdir(sample_path):
            raise Exception("the track name does not correspond with a sample directory")

        samples = [f for f in listdir(sample_path) if isfile(join(sample_path, f)) and f.endswith(".wav")]
        current_sample = self.track.devices[0].name + ".wav"

        if current_sample in samples:
            next_sample_index = samples.index(current_sample) + 1 if go_next else samples.index(current_sample) - 1
        else:
            next_sample_index = 0
        next_sample = samples[next_sample_index % len(samples)]

        self._do_load_item(self._get_item_for_category('samples', next_sample), 'Sample')
