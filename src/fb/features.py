class FB_BASE:
    def check_contents_for_validation(self):
        raise NotImplemenedError
    def send_payloads(self):
        raise NotImplemenedError
class FB_POST(FB_BASE):
    pass
class FB_STORY(FB_BASE):
    pass
class FB_REEL(FB_BASE):
    pass

class FB_feature:

    def __init__(self):
        pass
    
    def set_feature(self,feature:Union[FB_POST, FB_STORY, FB_REEL]):
        pass
