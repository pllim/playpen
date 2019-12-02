def process_opcode(opcode_in):
    opcode_list = opcode_in.copy()
    n = len(opcode_list)
    i = 0

    while i < n:
        cur_opcode = opcode_list[i]

        if cur_opcode == 99:
            break
        elif cur_opcode == 1:  # sum
            opcode_list[opcode_list[i + 3]] = (
                opcode_list[opcode_list[i + 1]] +
                opcode_list[opcode_list[i + 2]])
            i += 4
        elif cur_opcode == 2:  # multiply
            opcode_list[opcode_list[i + 3]] = (
                opcode_list[opcode_list[i + 1]] *
                opcode_list[opcode_list[i + 2]])
            i += 4
        else:
            raise ValueError(f'Unsupported opcode={cur_opcode}')

    return opcode_list


def find_noun_verb(answer=19690720):
    for noun in range(100):
        for verb in range(100):
            opcode_list = [1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,1,9,19,1,19,5,23,1,13,23,27,1,27,6,31,2,31,6,35,2,6,35,39,1,39,5,43,1,13,43,47,1,6,47,51,2,13,51,55,1,10,55,59,1,59,5,63,1,10,63,67,1,67,5,71,1,71,10,75,1,9,75,79,2,13,79,83,1,9,83,87,2,87,13,91,1,10,91,95,1,95,9,99,1,13,99,103,2,103,13,107,1,107,10,111,2,10,111,115,1,115,9,119,2,119,6,123,1,5,123,127,1,5,127,131,1,10,131,135,1,135,6,139,1,10,139,143,1,143,6,147,2,147,13,151,1,5,151,155,1,155,5,159,1,159,2,163,1,163,9,0,99,2,14,0,0]  # noqa
            opcode_list[1] = noun
            opcode_list[2] = verb
            opcode_out = process_opcode(opcode_list)
            if opcode_out[0] == answer:
                return noun, verb


if __name__ == '__main__':
    # Part 1
    # opcode_in = [1, 1, 1, 4, 99, 5, 6, 0, 99]  # test
    # opcode_in = [1,12,2,3,1,1,2,3,1,3,4,3,1,5,0,3,2,1,9,19,1,19,5,23,1,13,23,27,1,27,6,31,2,31,6,35,2,6,35,39,1,39,5,43,1,13,43,47,1,6,47,51,2,13,51,55,1,10,55,59,1,59,5,63,1,10,63,67,1,67,5,71,1,71,10,75,1,9,75,79,2,13,79,83,1,9,83,87,2,87,13,91,1,10,91,95,1,95,9,99,1,13,99,103,2,103,13,107,1,107,10,111,2,10,111,115,1,115,9,119,2,119,6,123,1,5,123,127,1,5,127,131,1,10,131,135,1,135,6,139,1,10,139,143,1,143,6,147,2,147,13,151,1,5,151,155,1,155,5,159,1,159,2,163,1,163,9,0,99,2,14,0,0]  # noqa
    # opcode_list = process_opcode(opcode_in)
    # print(opcode_in)
    # print(opcode_list)

    # Part 2
    noun, verb = find_noun_verb()
    print(f'{noun}, {verb}, {100 * noun + verb}')
