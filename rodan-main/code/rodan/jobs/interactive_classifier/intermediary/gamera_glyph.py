import uuid
from rodan.jobs.interactive_classifier.intermediary.run_length_image import \
    RunLengthImage


class GameraGlyph(object):
    def __init__(self, class_name, rle_image, ncols, nrows, ulx, uly,
                 id_state_manual, confidence,  gid=0):
        if gid == 0:
            self._id = uuid.uuid4().hex
        else:
            self._id = gid
        self._class_name = class_name
        self._image = rle_image
        self._ncols = ncols
        self._nrows = nrows
        self._ulx = ulx
        self._uly = uly
        self._id_state_manual = id_state_manual
        self._confidence = confidence
        self._is_training = False #default
        # Generate multiple internal image representations
        self._run_length_image = RunLengthImage(ulx=self._ulx,
                                                uly=self._uly,
                                                width=self._ncols,
                                                height=self._nrows,
                                                run_length_data=self._image)
        self._image_b64 = self._run_length_image.get_base64_image()
        self._gamera_image = self._run_length_image.get_gamera_image()
        if self.is_manual_id():
            self._gamera_image.classify_manual(self._class_name)

    def is_manual_id(self):
        return self._id_state_manual is True

    def get_gamera_image(self):
        return self._gamera_image

    def classify_manual(self, class_name):
        self._class_name = str(class_name)
        self._confidence = 1.0
        self.get_gamera_image().classify_manual(self._class_name)
        self._id_state_manual = True

    def is_id(self, id_name):
        return self._id == id_name

    def classify_automatic(self, class_name, confidence):
        self._class_name = str(class_name)
        self._confidence = confidence
        self._id_state_manual = False

    def to_dict(self):
        return {
            "id": self._id,
            "class_name": self._class_name,
            "image": self._image,
            "image_b64": self._image_b64,
            "ncols": self._ncols,
            "nrows": self._nrows,
            "ulx": self._ulx,
            "uly": self._uly,
            "id_state_manual": self.is_manual_id(),
            "confidence": self._confidence,
            "is_training": self._is_training
        }
