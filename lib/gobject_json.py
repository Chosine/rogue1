import simplejson


def valid_json(input):
    """ Return true/false depending on whether input is valid JSON """
    is_valid = False
    try:
        simplejson.loads(input)
        is_valid = True
    except:
        pass

    return is_valid


def extract_object(json_input):
    """
    Given either an old-style or new-style Proposal JSON string, extract the
    actual object used (ignore old-style multi-dimensional array and unused
    string for obj