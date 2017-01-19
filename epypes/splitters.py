

def copy_input_splitter(token, n_parallel):
    return tuple((token for i in range(n_parallel)))

def elementwise_input_splitter(token, n_parallel):

    sz_rest = n_parallel - len(token) #should be >= 0

    if sz_rest < 0:
        raise Exception('Number of elements in the token is greater than the number of parallel tasks')

    return tuple(token) + tuple(None for i in range(sz_rest))

def equal_input_splitter(token, n_parallel):
    input_size = len(token)
    if input_size <= n_parallel:
        return elementwise_input_splitter(token, n_parallel)

    chunk_size = input_size // n_parallel

    almost_all_chunks = tuple(token[i*chunk_size:(i+1)*chunk_size] for i in range(n_parallel-1))
    last_chunk = (token[chunk_size*(n_parallel-1):],)

    return almost_all_chunks + last_chunk