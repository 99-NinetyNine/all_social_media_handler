
from base.constants import (
    TEXT_LENGTH_MISMTACH,
    IMAGE_SIZE_MISMTACH,
    VIDEO_LENGTH_MISTACH,
    VIDEO_SIZE_MISTACH,
)
class mom_LongTextRejected(Exception):
    """ If user has provided longer text than supported thorow this error"""
    
    def __init__(self, message=TEXT_LENGTH_MISMTACH):
        self.message = message
        super().__init__(self.message)

class mom_ImageSizeRejected(Exception):
    """ If user has provided bigger image than supported thorow this error"""
    
    def __init__(self, message=IMAGE_SIZE_MISMTACH):
        self.message = message
        super().__init__(self.message)