class NextSceneStartedEvent(object):
    """
        Only emitted when a Scene.next_scene starts
        Keeps the memory of the previously selected scene
        (so that firing a scene doesn't change the selected scene)
    """
    def __init__(self, selected_scene_index):
        # type: (int) -> None
        self.selected_scene_index = selected_scene_index
