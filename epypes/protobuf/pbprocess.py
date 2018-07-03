
def add_attribute(pb_message, key, val):

    attr = pb_message.attributes.entries.add()

    attr.key = key

    if type(val) == str:
        attr.type = 1
        attr.str_val = val
    elif type(val) == float:
        attr.type = 2
        attr.double_val = val
    elif type(val) == int:
        attr.type = 3
        attr.int_val = val
    else:
        raise Exception('Wrong value type')


def copy_downstream_attributes(pb_message_prev, pb_message):

    ds_attributes = pb_message_prev.attributes.entries
    pb_message.attributes.entries.extend(ds_attributes)


def get_attributes_dict(attr_entries):

    attr_dict = dict()
    for entry in attr_entries:

        if entry.type == 1:
            val = entry.str_val
        elif entry.type == 2:
            val = entry.double_val
        else:
            val = entry.int_val

        attr_dict[entry.key] = val

    return attr_dict
