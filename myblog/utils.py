from markdown import markdown
from myblog.models import DBSession, Tags

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
