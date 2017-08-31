
def add_timestamp(pb_message, t, description):

    timestamp = pb_message.timestamps.entries.add()
    timestamp.unixtime = t
    timestamp.description = description

def copy_downstream_timestamps(pb_message_prev, pb_message):

    ds_timestamps = pb_message_prev.timestamps.entries
    pb_message.timestamps.entries.extend(ds_timestamps)

def timestamp_entries_to_dict(ts_entries):

    ts_dict = dict()
    for entry in ts_entries:
        ts_dict[entry.description] = entry.unixtime

    return  ts_dict



