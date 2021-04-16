# we need this because the device name is stored as string in the track name
# we could instead enforce one device per automation track and remove this
class DeviceType:
    ABLETON_DEVICE = "d"
    RACK_DEVICE = "r"
    PLUGIN_DEVICE = "p"
