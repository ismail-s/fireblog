"""
Events that are fired off by views. Subscribers to these views get
notified when the event is fired.
"""

class RenderingPost(object):
    """This is an event that gets fired when a post is being viewed.
    Subscribers can add html sections to self.sections and these will be
    put below the post on the webpage.
    """

    def __init__(self, post, request):
        self.post = post
        self.request = request
        self.sections = []
