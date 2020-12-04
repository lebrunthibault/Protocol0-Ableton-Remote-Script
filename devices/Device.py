import Live

from a_protocol_0.lom.AbstractObject import AbstractObject


class Device(AbstractObject):
    def __init__(self, device, *a, **k):
        super(Device, self).__init__(*a, **k)
        self._device = device
        self.name = device.name
        self._browser = Live.Application.get_application().browser
        self._cached_browser_items = {}

    def _do_load_item(self, item, header='Device'):
        """ Handles loading an item and displaying load info in status bar. """
        if item and item.is_loadable:
            self.song._view.selected_track.view.device_insert_mode = Live.Track.DeviceInsertMode.default
            self.parent.show_message('Loading %s: %s' % (header, item.name))
            self._browser.load_item(item)

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
            self._get_children_for_item(getattr(self._browser, category), self._cached_browser_items[category])
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
