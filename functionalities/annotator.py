class MatchAnnotator(object):
    def __init__(self, name, output_dir="Output") -> None:
        assert output_dir is not None, "Output directory was not given."

        self.output_dir = output_dir
        self.name = name

        # Image-specific attributes
        self.img_path = None  # Path to the last file being annotated
        self.scale_factor = None  # Scale factor of the last file being annotated
        self.clicks = []  # [[x_0, y_0], [x_1, y_1], ... ]
        self.last_click_id = -1

    def new_image(self, path, scale_factor):
        self.img_path = path
        self.scale_factor = scale_factor
        self.clicks = []
        self.last_click_id = -1

    def add_click(self, x, y):
        self.clicks.append({"x": x, "y": y})

    def reset_all_annotations(self):
        self.clicks = []
        self.last_click_id = -1
