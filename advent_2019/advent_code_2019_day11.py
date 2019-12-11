import io
import os
import sys
from collections import defaultdict

OPCODE = [3,8,1005,8,338,1106,0,11,0,0,0,104,1,104,0,3,8,1002,8,-1,10,1001,10,1,10,4,10,108,1,8,10,4,10,102,1,8,28,1,108,6,10,1,3,7,10,3,8,1002,8,-1,10,1001,10,1,10,4,10,108,1,8,10,4,10,1001,8,0,58,2,5,19,10,1,1008,7,10,2,105,6,10,1,1007,7,10,3,8,1002,8,-1,10,1001,10,1,10,4,10,1008,8,0,10,4,10,101,0,8,97,1006,0,76,1,106,14,10,2,9,9,10,1006,0,74,3,8,102,-1,8,10,101,1,10,10,4,10,108,1,8,10,4,10,1002,8,1,132,1006,0,0,2,1104,15,10,3,8,1002,8,-1,10,1001,10,1,10,4,10,1008,8,0,10,4,10,1001,8,0,162,1,1005,13,10,3,8,1002,8,-1,10,101,1,10,10,4,10,108,1,8,10,4,10,101,0,8,187,1,1,15,10,2,3,9,10,1006,0,54,3,8,102,-1,8,10,101,1,10,10,4,10,108,0,8,10,4,10,102,1,8,220,1,104,5,10,3,8,102,-1,8,10,101,1,10,10,4,10,1008,8,0,10,4,10,102,1,8,247,1,5,1,10,1,1109,2,10,3,8,1002,8,-1,10,101,1,10,10,4,10,1008,8,0,10,4,10,1001,8,0,277,1006,0,18,3,8,1002,8,-1,10,101,1,10,10,4,10,108,1,8,10,4,10,101,0,8,301,2,105,14,10,1,5,1,10,2,1009,6,10,1,3,0,10,101,1,9,9,1007,9,1054,10,1005,10,15,99,109,660,104,0,104,1,21101,0,47677546524,1,21101,0,355,0,1105,1,459,21102,936995299356,1,1,21101,0,366,0,1106,0,459,3,10,104,0,104,1,3,10,104,0,104,0,3,10,104,0,104,1,3,10,104,0,104,1,3,10,104,0,104,0,3,10,104,0,104,1,21101,0,206312807515,1,21102,1,413,0,1105,1,459,21101,206253871296,0,1,21102,424,1,0,1106,0,459,3,10,104,0,104,0,3,10,104,0,104,0,21102,1,709580554600,1,21102,1,447,0,1105,1,459,21101,0,868401967464,1,21101,458,0,0,1106,0,459,99,109,2,22102,1,-1,1,21102,1,40,2,21101,0,490,3,21102,480,1,0,1106,0,523,109,-2,2105,1,0,0,1,0,0,1,109,2,3,10,204,-1,1001,485,486,501,4,0,1001,485,1,485,108,4,485,10,1006,10,517,1101,0,0,485,109,-2,2105,1,0,0,109,4,2101,0,-1,522,1207,-3,0,10,1006,10,540,21102,0,1,-3,21201,-3,0,1,21202,-2,1,2,21101,0,1,3,21101,0,559,0,1105,1,564,109,-4,2106,0,0,109,5,1207,-3,1,10,1006,10,587,2207,-4,-2,10,1006,10,587,21202,-4,1,-4,1105,1,655,21201,-4,0,1,21201,-3,-1,2,21202,-2,2,3,21102,606,1,0,1105,1,564,22102,1,1,-4,21102,1,1,-1,2207,-4,-2,10,1006,10,625,21102,1,0,-1,22202,-2,-1,-2,2107,0,-3,10,1006,10,647,22101,0,-1,1,21101,0,647,0,106,0,522,21202,-2,-1,-2,22201,-4,-2,-4,109,-5,2106,0,0]  # noqa


# A modified version of the same function in Day 9.
def process_opcode(opcode_in, i_list=0, inbuf=None, outbuf=sys.stdout,
                   ibuf=sys.stdout, panels=[], cur_panel=[], debug=False):
    opcode_list = opcode_in.copy()
    extra_memory = defaultdict(int)  # Store memory beyond max index
    n = len(opcode_list)
    rel_base = 0
    track_output_order = 0
    direction = 'up'

    def _get_actual_idx(mode, idx):
        if mode == 0:  # position mode
            if idx >= n:
                idx_mem = extra_memory[idx]
            else:
                idx_mem = opcode_list[idx]
        elif mode == 1:  # immediate mode
            idx_mem = idx
        elif mode == 2:  # relative mode
            if idx >= n:
                idx_mem = extra_memory[idx] + rel_base
            else:
                idx_mem = opcode_list[idx] + rel_base
        else:
            raise ValueError(f'Invalid parameter mode={mode}')
        return idx_mem

    def _get_val(mode, idx):
        idx_mem = _get_actual_idx(mode, idx)
        if idx_mem >= n:
            val = extra_memory[idx_mem]
            if debug:
                print(f'getting extra_memory[{idx_mem}] = {val}')
        else:
            val = opcode_list[idx_mem]
            if debug:
                print(f'getting opcode_list[{idx_mem}] = {val}')
        return val

    def _put_val(idx, val):
        nonlocal opcode_list, extra_memory
        if idx < 0:
            raise ValueError(f'Invalid memory index={idx}')
        elif idx >= n:
            if debug:
                print(f'before _put_val: extra_memory[{idx}]={extra_memory[idx]}')  # noqa
            extra_memory[idx] = val
            if debug:
                print(f'after _put_val: extra_memory[{idx}]={extra_memory[idx]}')  # noqa
        else:
            if debug:
                print(f'before _put_val: opcode_list[{idx}]={opcode_list[idx]}')  # noqa
            opcode_list[idx] = val
            if debug:
                print(f'after _put_val: opcode_list[{idx}]={opcode_list[idx]}')

    while i_list < n:
        instruction = opcode_list[i_list]
        if debug:
            print(f'\ni_list={i_list}, instructions={instruction}')

        cur_opcode = instruction % 100  # 2 right-most digits
        pars = list(map(int, [c for c in str(int(instruction / 100))]))
        n_pars = len(pars)
        max_pars = 3
        if n_pars < max_pars:  # leading zeroes
            for i in range(max_pars - n_pars):
                pars.insert(0, 0)

        if cur_opcode == 99:
            outbuf.write('exit' + os.linesep)
            outbuf.seek(0)
            if debug:
                print('***** EXIT *****')
            break
        elif cur_opcode == 1:  # sum
            x1 = _get_val(pars[2], i_list + 1)
            x2 = _get_val(pars[1], i_list + 2)
            x3 = _get_actual_idx(pars[0], i_list + 3)
            if debug:
                print(f'{x1} + {x2} -> addr {x3}')
            _put_val(x3, x1 + x2)
            i_list += 4
        elif cur_opcode == 2:  # multiply
            x1 = _get_val(pars[2], i_list + 1)
            x2 = _get_val(pars[1], i_list + 2)
            x3 = _get_actual_idx(pars[0], i_list + 3)
            if debug:
                print(f'{x1} * {x2} -> addr {x3}')
            _put_val(x3, x1 * x2)
            i_list += 4
        elif cur_opcode == 3:  # input
            if inbuf is None:
                x = input('Enter input (int): ')
            else:
                x = inbuf.readline().strip()
                if not x:  # Maybe from OPCODE=4
                    x = outbuf.readline().strip()
                    outbuf.seek(0)
            x = int(x)
            x1 = _get_actual_idx(pars[2], i_list + 1)
            if debug:
                print(f'input={x} -> addr {x1}')
            _put_val(x1, x)
            i_list += 2
        elif cur_opcode == 4:  # output
            x1 = _get_val(pars[2], i_list + 1)
            if debug:
                print(f'output={x1} str={str(x1)}')
            outbuf.write(str(x1) + os.linesep)
            outbuf.seek(0)
            i_list += 2
            ibuf.write(str(i_list) + os.linesep)
            ibuf.seek(0)
            if track_output_order == 0:  # color of paint
                # TODO: Need dict to track panel colors? Maybe panels can be dict
                track_output_order = 1
                panels.append(tuple(cur_panel))
                if debug:
                    print(f'painted {cur_panel} color={x1}')
                    # input('Paused:')
            else:  # 1; direction
                track_output_order = 0
                if debug:
                    print(f'direction={direction} cur_panel={cur_panel}')
                if x1 == 0:  # left
                    if debug:
                        print('turning left')
                    if direction == 'up':
                        cur_panel[1] -= 1
                        direction = 'left'
                    elif direction == 'right':
                        cur_panel[0] += 1
                        direction = 'up'
                    elif direction == 'left':
                        cur_panel[0] -= 1
                        direction = 'down'
                    else:  # down
                        cur_panel[1] += 1
                        direction = 'right'
                elif x1 == 1:  # right
                    if debug:
                        print('turning right')
                    if direction == 'up':
                        cur_panel[1] += 1
                        direction = 'right'
                    elif direction == 'right':
                        cur_panel[0] -= 1
                        direction = 'down'
                    elif direction == 'left':
                        cur_panel[0] += 1
                        direction = 'up'
                    else:  # down
                        cur_panel[1] -= 1
                        direction = 'left'
                if debug:
                    print(f'after turn and move 1, cur_panel={cur_panel}')
                    # input('Paused:')
        elif cur_opcode == 5:  # jump if true
            x1 = _get_val(pars[2], i_list + 1)
            x2 = _get_val(pars[1], i_list + 2)
            if x1 != 0:
                i_list = x2
                if debug:
                    print(f'jumping to {i_list}')
            else:
                i_list += 3
                if debug:
                    print(f'not jumping -> {i_list}')
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
            x3 = _get_actual_idx(pars[0], i_list + 3)
            if debug:
                print(f'{x1} < {x2} ? -> addr {x3}')
            if x1 < x2:
                _put_val(x3, 1)
            else:
                _put_val(x3, 0)
            i_list += 4
        elif cur_opcode == 8:  # equal
            x1 = _get_val(pars[2], i_list + 1)
            x2 = _get_val(pars[1], i_list + 2)
            x3 = _get_actual_idx(pars[0], i_list + 3)
            if debug:
                print(f'{x1} == {x2} ? -> addr {x3}')
            if x1 == x2:
                _put_val(x3, 1)
            else:
                _put_val(x3, 0)
            i_list += 4
        elif cur_opcode == 9:  # relative mode
            x1 = _get_val(pars[2], i_list + 1)
            rel_base += x1
            if debug:
                print(f'par={opcode_list[i_list + 1]}, rel_mode={x1}, new rel_base={rel_base}')  # noqa
            i_list += 2
        else:
            raise ValueError(f'Unsupported opcode={cur_opcode}')

    return opcode_list


def hull_painter(debug=False):
    """
    0 = black
    1 = white
    """
    global OPCODE

    i_count = 0
    max_iter = 10000
    i_list = 0
    a_in = io.StringIO()
    a_in.write('0\n')  # Black
    a_in.seek(0)
    a_out = io.StringIO()
    a_list = io.StringIO()
    painted_panels = []
    cur_panel = [0, 0]  # (y, x)
    exited = False

    # Do not need the loop in Part 1 but saving for Part 2, just in case.
    while not exited and i_count < max_iter:
        process_opcode(OPCODE, i_list=i_list, inbuf=a_in, outbuf=a_out,
                       ibuf=a_list, panels=painted_panels, cur_panel=cur_panel,
                       debug=debug)
        signal = a_out.readline().strip()
        if signal.startswith('exit'):
            exited = True
            break
        a_out.seek(0)
        a_in.seek(0)
        a_in.write(signal + os.linesep)
        a_in.seek(0)
        i_list = int(a_list.readline().strip())
        a_list.seek(0)
        i_count += 1

    return painted_panels


if __name__ == '__main__':
    # Part 1
    panels = hull_painter(debug=False)
    print(len(set(panels)))
