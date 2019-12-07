import io
import os
import sys
from collections import defaultdict
from itertools import permutations
from advent_code_2019_day05 import process_opcode

OPCODE = [3,8,1001,8,10,8,105,1,0,0,21,34,59,76,101,114,195,276,357,438,99999,3,9,1001,9,4,9,1002,9,4,9,4,9,99,3,9,102,4,9,9,101,2,9,9,102,4,9,9,1001,9,3,9,102,2,9,9,4,9,99,3,9,101,4,9,9,102,5,9,9,101,5,9,9,4,9,99,3,9,102,2,9,9,1001,9,4,9,102,4,9,9,1001,9,4,9,1002,9,3,9,4,9,99,3,9,101,2,9,9,1002,9,3,9,4,9,99,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,99,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,1,9,4,9,99,3,9,102,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,2,9,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,2,9,9,4,9,3,9,101,2,9,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,2,9,9,4,9,3,9,101,2,9,9,4,9,3,9,101,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,2,9,9,4,9,99]  # noqa
#OPCODE = [3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5]  # TEST 1 # noqa
#OPCODE = [3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10]  # TEST 2 # noqa


def process_opcode_with_feedback(
        opcode_list, i_list=0, inbuf=None, outbuf=sys.stdout, ibuf=sys.stdout,
        debug=False):
    n = len(opcode_list)

    def _get_val(mode, idx):
        if mode == 0:  # position mode
            val = opcode_list[opcode_list[idx]]
        elif mode == 1:  # immediate mode
            val = opcode_list[idx]
        else:
            raise ValueError(f'Invalid parameter mode={mode}')
        return val

    while i_list < n:
        instruction = opcode_list[i_list]
        if debug:
            print(f'instructions={instruction}')

        cur_opcode = instruction % 100  # 2 right-most digits
        pars = list(map(int, [c for c in str(int(instruction / 100))]))
        n_pars = len(pars)
        max_pars = 3
        if n_pars < max_pars:  # leading zeroes
            for i in range(max_pars - n_pars):
                pars.insert(0, 0)

        if cur_opcode == 99:
            outbuf.write('exit' + os.linesep)
            if debug:
                print('***** EXIT *****')
            break
        elif cur_opcode == 1:  # sum
            x1 = _get_val(pars[2], i_list + 1)
            x2 = _get_val(pars[1], i_list + 2)
            opcode_list[opcode_list[i_list + 3]] = x1 + x2
            i_list += 4
        elif cur_opcode == 2:  # multiply
            x1 = _get_val(pars[2], i_list + 1)
            x2 = _get_val(pars[1], i_list + 2)
            opcode_list[opcode_list[i_list + 3]] = x1 * x2
            i_list += 4
        elif cur_opcode == 3:  # input
            if inbuf is None:
                x = input('Enter input (int): ')
            else:
                x = inbuf.readline()
                if debug:
                    print(f'input={x}')
            opcode_list[opcode_list[i_list + 1]] = int(x)
            i_list += 2
        elif cur_opcode == 4:  # output
            x1 = _get_val(pars[2], i_list + 1)
            if debug:
                print(f'output={x1}')
            outbuf.write(str(x1) + os.linesep)
            i_list += 2
            ibuf.write(str(i_list) + os.linesep)
        elif cur_opcode == 5:  # jump if true
            x1 = _get_val(pars[2], i_list + 1)
            x2 = _get_val(pars[1], i_list + 2)
            if x1 != 0:
                i_list = x2
            else:
                i_list += 3
        elif cur_opcode == 6:  # jump if false
            x1 = _get_val(pars[2], i_list + 1)
            x2 = _get_val(pars[1], i_list + 2)
            if x1 == 0:
                i_list = x2
            else:
                i_list += 3
        elif cur_opcode == 7:  # less than
            x1 = _get_val(pars[2], i_list + 1)
            x2 = _get_val(pars[1], i_list + 2)
            if x1 < x2:
                opcode_list[opcode_list[i_list + 3]] = 1
            else:
                opcode_list[opcode_list[i_list + 3]] = 0
            i_list += 4
        elif cur_opcode == 8:  # equal
            x1 = _get_val(pars[2], i_list + 1)
            x2 = _get_val(pars[1], i_list + 2)
            if x1 == x2:
                opcode_list[opcode_list[i_list + 3]] = 1
            else:
                opcode_list[opcode_list[i_list + 3]] = 0
            i_list += 4
        else:
            raise ValueError(f'Unsupported opcode={cur_opcode}')


# TODO: Algorithm is unstable.
def amplify_with_feedback(sequence, signal='0', debug=True):
    ACS_A = OPCODE.copy()
    ACS_B = OPCODE.copy()
    ACS_C = OPCODE.copy()
    ACS_D = OPCODE.copy()
    ACS_E = OPCODE.copy()
    MEMORY = defaultdict(list)
    I_LIST = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
    # ACS_A = ACS_B = ACS_C = ACS_D = ACS_E = OPCODE.copy()
    all_amps = ('A', 'B', 'C', 'D', 'E')

    def _feedback_loop(debug):
        nonlocal ACS_A, ACS_B, ACS_C, ACS_D, ACS_E, MEMORY, I_LIST

        for amp_name in all_amps:
            mem = MEMORY[amp_name]
            MEMORY[amp_name] = []  # pop
            last_signal = mem[-1]
            in_str = os.linesep.join(mem) + os.linesep
            a_in = io.StringIO()
            a_in.write(in_str)
            a_in.seek(0)
            a_out = io.StringIO()
            a_list = io.StringIO()
            if debug:
                print(f'amp={amp_name} i_list={I_LIST[amp_name]} in=\n{in_str}')

            if amp_name == 'A':
                next_amp = 'B'
                try:
                    process_opcode_with_feedback(
                        ACS_A, i_list=I_LIST[amp_name], inbuf=a_in,
                        outbuf=a_out, ibuf=a_list, debug=debug)
                except Exception:  # Move on to next in sequence
                    pass
            elif amp_name == 'B':
                next_amp = 'C'
                try:
                    process_opcode_with_feedback(
                        ACS_B, i_list=I_LIST[amp_name], inbuf=a_in,
                        outbuf=a_out, ibuf=a_list, debug=debug)
                except Exception:  # Move on to next in sequence
                    pass
            elif amp_name == 'C':
                next_amp = 'D'
                try:
                    process_opcode_with_feedback(
                        ACS_C, i_list=I_LIST[amp_name], inbuf=a_in,
                        outbuf=a_out, ibuf=a_list, debug=debug)
                except Exception:  # Move on to next in sequence
                    pass
            elif amp_name == 'D':
                next_amp = 'E'
                try:
                    process_opcode_with_feedback(
                        ACS_D, i_list=I_LIST[amp_name], inbuf=a_in,
                        outbuf=a_out, ibuf=a_list, debug=debug)
                except Exception:  # Move on to next in sequence
                    pass
            elif amp_name == 'E':
                next_amp = 'A'
                try:
                    process_opcode_with_feedback(
                        ACS_E, i_list=I_LIST[amp_name], inbuf=a_in,
                        outbuf=a_out, ibuf=a_list, debug=debug)
                except Exception:  # Move on to next in sequence
                    pass
            else:
                raise ValueError(f'Invalid amp={amp_name}')

            a_out.seek(0)
            signal = a_out.readline().strip()
            a_list.seek(0)
            I_LIST[amp_name] = int(a_list.readline().strip())
            if signal.startswith('exit'):
                if amp_name == 'E':
                    signal = last_signal
                    if debug:
                        print(f'exited: signal={signal}')
                    break
                else:
                    continue  # ???
            else:
                MEMORY[next_amp].append(signal)
                if debug:
                    print(f'next mem={MEMORY[next_amp]} next signal={signal}')
        return signal

    max_iter = 10  # DEBUG
    i = 0
    halted = False
    MEMORY['A'] += [str(sequence[0]), signal]
    MEMORY['B'].append(str(sequence[1]))
    MEMORY['C'].append(str(sequence[2]))
    MEMORY['D'].append(str(sequence[3]))
    MEMORY['E'].append(str(sequence[4]))
    while not halted:
        if debug:
            print(f'iter={i}')
        try:
            signal = _feedback_loop(debug)
        except Exception as exc:
            halted = True
            if debug:
                print(f'{exc}')
        i += 1
        if debug and i >= max_iter:
            halted = True

    return int(signal)


def amplify_no_feedback(sequence, signal='0', debug=True):
    SOFTWARE = {'A': OPCODE.copy(), 'B': OPCODE.copy(), 'C': OPCODE.copy(),
                'D': OPCODE.copy(), 'E': OPCODE.copy()}
    mapping = dict(zip(sequence, SOFTWARE))

    for seq in sequence:
        in_str = str(seq) + os.linesep + signal + os.linesep
        a_in = io.StringIO()
        a_in.write(in_str)
        a_in.seek(0)
        a_out = io.StringIO()
        amp_name = mapping[seq]
        if debug:
            print(f'amp={amp_name} seq={seq}')
            print(f'in=\n{in_str}')
        process_opcode(
            SOFTWARE[amp_name], inbuf=a_in, outbuf=a_out, debug=debug)
        a_out.seek(0)
        signal = a_out.readline()
        if debug:
            print(f'next signal={signal}')

    return int(signal)


def find_max_amp(phases, feedback=False, debug=False):
    max_amp = 0
    for sequence in set(permutations(phases)):
        if feedback:
            amp = amplify_with_feedback(sequence, debug=debug)
        else:
            amp = amplify_no_feedback(sequence, debug=debug)
        if amp > max_amp:
            max_amp = amp
    return max_amp


if __name__ == '__main__':
    # Part 1 (no feedback loop)
    # print(find_max_amp(range(5)))

    # Part 2
    print(find_max_amp(range(5, 10), feedback=True, debug=True))
    # print(amplify_with_feedback((9, 8, 7, 6, 5), debug=True))  # TEST 1: 5 iters  # noqa
    # print(amplify_with_feedback((9, 7, 8, 5, 6), debug=True))  # TEST 2: 10 iters  # noqa
