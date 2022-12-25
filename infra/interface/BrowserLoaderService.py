import Live
from typing import Dict

from protocol0.domain.lom.device.Sample.SampleNotFoundError import SampleNotFoundError
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.logging.Logger import Logger

AUDIO_FX = (
    "Amp",
    "Audio Effect Rack",
    "Auto Filter",
    "Auto Pan",
    "Beat Repeat",
    "Cabinet",
    "Chorus",
    "Compressor",
    "Corpus",
    "Dynamic Tube",
    "EQ Eight",
    "EQ Three",
    "Erosion",
    "External Audio Effect",
    "Filter Delay",
    "Flanger",
    "Frequency Shifter",
    "Gate",
    "Glue Compressor",
    "Grain Delay",
    "Limiter",
    "Looper",
    "Multiband Dynamics",
    "Overdrive",
    "Phaser",
    "Ping Pong Delay",
    "Redux",
    "Resonators",
    "Reverb",
    "Saturator",
    "Simple Delay",
    "Spectrum",
    "Tuner",
    "Utility",
    "Vinyl Distortion",
    "Vocoder",
    "Drum Buss",
    "Echo",
    "Pedal",
    "Channel EQ",
    "Delay",
)
MIDI_FX = (
    "Arpeggiator",
    "Chord",
    "MIDI Effect Rack",
    "Note Length",
    "Pitch",
    "Random",
    "Scale",
    "Velocity",
)
INSTRUMENTS = (
    "Analog",
    "Collision",
    "Drum Rack",
    "Electric",
    "External Instrument",
    "Impulse",
    "Instrument Rack",
    "Operator",
    "Sampler",
    "Simpler",
    "Tension",
    "Wavetable",
)


class BrowserLoaderService(object):
    def __init__(self, browser):
        # type: (Live.Browser.Browser) -> None
        self._browser = browser
        self._cached_browser_items = {}  # type: Dict[str, Dict[str, Live.Browser.BrowserItem]]

    def load_device(self, device_name):
        # type: (str) -> None
        """Loads a built-in Live device."""
        if device_name in MIDI_FX:
            self._do_load_item(self._get_item_for_category("midi_effects", device_name))
        elif device_name in INSTRUMENTS:
            self._do_load_item(self._get_item_for_category("instruments", device_name))
        elif device_name in AUDIO_FX:
            self._do_load_item(self._get_item_for_category("audio_effects", device_name))
        else:
            item = self._get_item_for_category("plugins", device_name)

            if item is None:
                raise Protocol0Warning("Couldn't load %s" % device_name)

            self._do_load_item(item, "Plugin")

    def load_sample(self, name):
        # type: (str) -> None
        """Loads items from the sample category."""
        self._do_load_item(self._get_item_for_category("samples", name), "Sample")

    def load_from_user_library(self, name):
        # type: (str) -> None
        """Loads items from the user library category"""
        self._do_load_item(self._get_item_for_category("user_library", name), "from User Library")

    def get_sample(self, sample_name):
        # type: (str) -> Live.Browser.BrowserItem
        self._cache_category("samples")
        return self._cached_browser_items["samples"].get(
            str(sample_name.decode("utf-8")), None
        )

    def _do_load_item(self, item, header="Device"):
        # type: (Live.Browser.BrowserItem, str) -> None
        """Handles loading an item and displaying load info in status bar."""
        # NB : activating this will hotswap drum rack pads if a drum rack is selected
        # ApplicationView.toggle_browse()
        if item and item.is_loadable:
            Logger.info("Loading %s: %s" % (header, item.name))
            # noinspection PyArgumentList
            self._browser.load_item(item)
            # ApplicationView.toggle_browse()
            # Scheduler.defer(partial(self._browser.load_item, item))
        else:
            raise Protocol0Error("Couldn't load %s item" % header)

    def _get_item_for_category(self, category, name):
        # type: (str, str) -> Live.Browser.BrowserItem
        """Returns the cached item for the category."""
        self._cache_category(category)
        item = self._cached_browser_items[category].get(name, None)
        if item is None:
            raise SampleNotFoundError(name)

        return item

    def _cache_category(self, category):
        # type: (str) -> None
        """This will cache an entire dict of items for the category if one doesn't
        already exist."""
        if category == "user_library" and self._cached_browser_items.get(category, False):
            self._cached_browser_items[category] = {}
        if not self._cached_browser_items.get(category, None):
            self._cached_browser_items[category] = {}
            self._get_children_for_item(
                getattr(self._browser, category), self._cached_browser_items[category]
            )

    def _get_children_for_item(self, item, i_dict, is_drum_rack=False):
        # type: (Live.Browser.BrowserItem, Dict[str, Live.Browser.BrowserItem], bool) -> None
        """Recursively builds dict of children items for the given item. This is needed
        to deal with children that are folders. If is_drum_rack, will only deal with
        racks in the root (not drum hits)."""
        for i in item.iter_children:
            if i.is_folder or not i.is_loadable:
                if is_drum_rack:
                    continue
                self._get_children_for_item(i, i_dict)
            elif not is_drum_rack or i.name.endswith(".adg"):
                i_dict[i.name] = i
