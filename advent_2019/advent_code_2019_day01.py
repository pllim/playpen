import numpy as np


def module_mass(mass):
    fuel_mass = np.floor(mass / 3) - 2
    if fuel_mass <= 0:
        return 0
    return fuel_mass + module_mass(fuel_mass)


def sum_of_masses(filename='masses.txt'):
    ans = 0.0
    with open(filename) as fin:
        for line in fin:
            row = line.split()
            mass = int(row[0])
            ans += module_mass(mass)
    return ans


if __name__ == '__main__':
    print(sum_of_masses())
