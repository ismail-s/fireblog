from markdown import markdown
import ago
from myblog.models import DBSession, Tags

LENGTH_OF_EACH_POST_TO_INCLUDE_IN_ALL_POST_VIEW = 1000

def to_markdown(input_text):
    '''Basic wrapper around the markdown library.
    
    Basically, it means that we state the extensions we
    use only once-here.'''
    extensions = ['markdown.extensions.codehilite',
                'markdown.extensions.fenced_code']
    res = markdown(input_text, extensions = extensions)
    return res

def append_tags_from_string_to_tag_object(tag_string, tag_object):
    tags_on_tag_object = [] # This is to be a list of tags on the tag_object
    for tag in tag_object:
        tags_on_tag_object.append(tag.tag)
    new_tag_list = tag_string.split(',')
    new_tag_list = [x.strip() for x in new_tag_list]
    new_tag_list = list(set(new_tag_list))

    # 1. Add the tag if it needs to be added.
    for tag in new_tag_list:
        # If the tag exists already, we get the object from DBSession.
        # If it doesn't, then we create a new tag object.
        if not tag:
            continue
        if tag in tags_on_tag_object:
            continue

        # 1.1 Get a tag object.
        existing_tag = DBSession.query(Tags).filter_by(tag = tag).first()
        if not existing_tag:
            tag_obj = Tags(tag = tag)
            DBSession.add(tag_obj)
        else:
            tag_obj = existing_tag

        # 1.2 Update the post with the tag object
        tag_object.append(tag_obj)

    # 2. Remove tags that need to be removed
    for tag in tags_on_tag_object:
        if tag not in new_tag_list:
            tag_object.remove(DBSession.query(Tags).filter_by(tag=tag).first())

def turn_tag_object_into_string_for_forms(tag_object):
    tags = [t.tag for t in tag_object]
    tags.sort()
    tags = ', '.join(tags)
    return tags

def create_post_list_from_posts_obj(post_obj):
    l = LENGTH_OF_EACH_POST_TO_INCLUDE_IN_ALL_POST_VIEW
    res = []
    code_styles = False  # Is true if we need to include pygments css
    # in the page
    for post in post_obj:
        to_append = {}
        to_append["name"] = post.name
        to_append["html"] = to_markdown(post.markdown[:l] + '\n\n...')
        to_append["date"] = ago.human(post.created, precision = 1)
        res.append(to_append)
        if not code_styles and 'class="codehilite"' in post.html:
            code_styles = True
    return res, code_styles