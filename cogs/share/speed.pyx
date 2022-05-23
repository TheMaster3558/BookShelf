def get_max(dict population):
    cdef str greatest_key = ''
    cdef int greatest_value = 0

    cdef str k
    cdef int v

    for k, v in population.items():
        if v > greatest_value:
            greatest_key, greatest_value = k, v

    return greatest_key
