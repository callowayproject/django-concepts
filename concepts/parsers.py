from taggit.utils import parse_tags

def default(value):
    if isinstance(value, (list, tuple)):
        return list(set(value))
    else:
        return parse_tags(value)

def json_parser(value):
    from django.utils import simplejson
    
    if value:
        if isinstance(value, (list, tuple)):
            return list(set(value))
        else:
            return simplejson.loads(value)
    return value
