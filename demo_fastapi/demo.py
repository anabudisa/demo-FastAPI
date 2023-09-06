import numpy as np


def foo(x):
    """
    Sort the array x in ascending way.
    :param x: numpy.ndarray
    :return: numpy.ndarray, sorted x
    """
    return np.sort(x)


if __name__ == "__main__":
    a = np.array([1, 395, 82, 148, 8, 384629, 44])
    print(f"Initial array: {a=}")
    print("Sorted array: ", foo(a))
