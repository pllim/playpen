import matplotlib.pyplot as plt
import numpy as np


def read_SIF(filename, height, width):
    with open('space_image_format.txt') as fin:
        data = fin.read().split()[0]

    a = np.array([int(d) for d in data])
    n_layers = int(a.size / (height * width))

    # z (layers), y (rows), x (cols)
    return a.reshape(n_layers, height, width)


def flatten_SIF(data):
    """Color of pixel is the first non-transparent layer.
    0=black, 1=white, 2=transparent
    """
    result = np.zeros(data[0].shape) + 2
    for z in range(data.shape[0]):  # Drill down the layers
        mask = result == 2
        result[mask] = data[z][mask]
    return result.astype(int)


def part_1(debug=True):
    im = read_SIF('space_image_format.txt', 6, 25)
    min_zero = im.size + 1
    z_min_zero = -1
    for z in range(im.shape[0]):
        mask = im[z] == 0
        n_zero = np.count_nonzero(mask)
        if n_zero < min_zero:
            min_zero = n_zero
            z_min_zero = z
    if debug:
        print(f'Layer index with fewest zeroes: {z_min_zero}')
    n_one = np.count_nonzero(im[z_min_zero] == 1)
    n_two = np.count_nonzero(im[z_min_zero] == 2)
    return n_one * n_two


def part_2():
    data = read_SIF('space_image_format.txt', 6, 25)
    im = flatten_SIF(data)
    plt.imshow(im)
    plt.show()


if __name__ == '__main__':
    # Part 1
    # print(part_1())

    # Part 2
    part_2()
