

def copy_input_splitter(payload, n_parallel):
    return tuple((payload for i in range(n_parallel)))

def elementwise_input_splitter(payload, n_parallel):

    sz_rest = n_parallel - len(payload) #should be >= 0

    if sz_rest < 0:
        raise Exception('Number of elements in the payload is greater than the number of parallel tasks')

    return tuple(payload) + tuple(None for i in range(sz_rest))

def equal_input_splitter(payload, n_parallel):
    input_size = len(payload)
    if input_size <= n_parallel:
        return elementwise_input_splitter(payload, n_parallel)

    chunk_size = input_size // n_parallel

    almost_all_chunks = tuple(payload[i * chunk_size:(i + 1) * chunk_size] for i in range(n_parallel - 1))
    last_chunk = (payload[chunk_size * (n_parallel - 1):],)

    return almost_all_chunks + last_chunk

def split_payload_and_build_tokens(payload, input_splitter, n_parallel, payload_index=None):

    def build_new_token(token, payload_part, payload_index):
        return tuple(payload_part if i is payload_index else el for i, el in enumerate(token))

    if payload_index is None:
        token_parts = input_splitter(payload, n_parallel)
    else:
        payload = payload[payload_index]
        payload_parts = input_splitter(payload, n_parallel)
        token_parts = tuple(build_new_token(payload, payload_part, payload_index) for payload_part in payload_parts)

    return token_parts
