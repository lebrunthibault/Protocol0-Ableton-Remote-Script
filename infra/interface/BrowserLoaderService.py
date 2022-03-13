from functools import partial

from typing import Dict

import Live
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.logging.Logger import Logger

AUDIO_FX = (u'Amp', u'Audio Effect Rack', u'Auto Filter', u'Auto Pan', u'Beat Repeat',
            u'Cabinet', u'Chorus', u'Compressor', u'Corpus', u'Dynamic Tube', u'EQ Eight',
            u'EQ Three', u'Erosion', u'External Audio Effect', u'Filter Delay', u'Flanger',
            u'Frequency Shifter', u'Gate', u'Glue Compressor', u'Grain Delay', u'Limiter',
            u'Looper', u'Multiband Dynamics', u'Overdrive', u'Phaser', u'Ping Pong Delay',
            u'Redux', u'Resonators', u'Reverb', u'Saturator', u'Simple Delay', u'Spectrum',
            u'Tuner', u'Utility', u'Vinyl Distortion', u'Vocoder', u'Drum Buss',
            u'Echo', u'Pedal', u'Channel EQ', u'Delay')
MIDI_FX = (u'Arpeggiator', u'Chord', u'MIDI Effect Rack', u'Note Length', u'Pitch',
           u'Random', u'Scale', u'Velocity')
INSTRUMENTS = (u'Analog', u'Collision', u'Drum Rack', u'Electric', u'External Instrument',
               u'Impulse', u'Instrument Rack', u'Operator', u'Sampler', u'Simpler',
               u'Tension', u'Wavetable')


class BrowserLoaderService(object):
    def __init__(self, browser):
        # type: (Live.Browser.Browser) -> None
        self._browser = browser
        self._cached_browser_items = {}

    def load_device(self, device_name):
        # type: (str) -> None
        """ Loads a built in Live device. """
        if device_name in MIDI_FX:
            self._do_load_item(self._get_item_for_category('midi_effects', device_name))
        elif device_name in INSTRUMENTS:
            self._do_load_item(self._get_item_for_category('instruments', device_name))
        elif device_name in AUDIO_FX:
            self._do_load_item(self._get_item_for_category('audio_effects', device_name))

    def load_from_user_library(self, name):
        # type: (str) -> None
        """ Loads items from the user library category """
        self._do_load_item(self._get_item_for_category('user_library', name), 'from User Library')

    def _do_load_item(self, item, header='Device'):
        # type: (Live.Browser.BrowserItem, str) -> None
        """ Handles loading an item and displaying load info in status bar. """
        if item and item.is_loadable:
            Logger.info('Loading %s: %s' % (header, item.name))
            Scheduler.defer(partial(self._browser.load_item, item))

    def _get_item_for_category(self, category, item):
        # type: (str, str) -> Live.Browser.BrowserItem
        """ Returns the cached item for the category. """
        self._cache_category(category)
        return self._cached_browser_items[category].get(item, None)

    def _cache_category(self, category):
        # type: (str) -> None
        """ This will cache an entire dict of items for the category if one doesn't
        already exist. """
        if category == 'user_library' and self._cached_browser_items.get(category, None):
            self._cached_browser_items[category] = {}
        if not self._cached_browser_items.get(category, None):
            self._cached_browser_items[category] = {}
            self._get_children_for_item(getattr(self._browser, category), self._cached_browser_items[category])

    def _get_children_for_item(self, item, i_dict, is_drum_rack=False):
        # type: (Live.Browser.BrowserItem, Dict[str, Live.Browser.BrowserItem], bool) -> None
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
