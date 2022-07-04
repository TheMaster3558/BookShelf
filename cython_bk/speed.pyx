import sys


cdef get_max(dict population, greater_than):
    cdef str greatest_key = ''
    cdef int greatest_value = 0

    cdef str k
    cdef int v
    for k, v in population.items():
        if v > greatest_value and v > greater_than:
            greatest_key, greatest_value = k, v

    return greatest_key
