import numpy as np

__all__ = ['add_list_elem_in_dict',
           'sort_dict',
           'calculate_delta',
           'sort_sub_list',
           'argsort_sub_list']


def add_list_elem_in_dict(dict, key, value):
    if key in dict:
        dict[key].append(value)
    else:
        dict[key] = [value]


def sort_dict(dictionary, key):
    sorted_idx = np.argsort(np.array(dictionary[key]))
    for k in dictionary:
        dictionary[k] = np.array(dictionary[k])[sorted_idx].tolist()
    return dictionary


def calculate_delta(data, timestamp, max_interval=1):
    valid_idx = [idx for idx, d_i in enumerate(data)
                 if d_i is not None and d_i == d_i]
    delta = [None] * valid_idx[0]
    for i in range(len(valid_idx) - 1):
        interval = valid_idx[i + 1] - valid_idx[i]
        if interval <= max_interval:
            delta += [(data[valid_idx[i + 1]] -
                       data[valid_idx[i]]) / interval] * interval
        else:
            delta += [None] * interval
    delta += [None] * (len(timestamp) - valid_idx[-1])
    return delta


def sort_sub_list(x: list, mask, idx):
    arr = np.array(x)
    arr[mask] = arr[mask][idx]
    return list(arr)


def argsort_sub_list(x: list, mask):
    arr = np.array(x)
    sort_idx = np.argsort(arr[mask])
    return sort_idx
