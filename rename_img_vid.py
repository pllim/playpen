"""Rename some files. For example:

* PXL_YYYYMMDD_nnn.jpg becomes IMG_YYYYMMDD_nnn.jpg
* PXL_YYYYMMDD_nnn.NIGHT.jpg becomes IMG_YYYYMMDD_nnn.jpg
* PXL_YYYYMMDD_nnn.MP.jpg becomes IMG_YYYYMMDD_nnn_MV.jpg
* PXL_YYYYMMDD_nnn.mp4 becomes VID_YYYYMMDD_nnn.mp4

Usage::

    python rename_img_vid.py "D:\\My\\Windows\\Path" -v

"""
import glob
import os

__all__ = []


def undo_pxl(path, verbose=False):
    pxl_prefix = 'PXL_'
    for filetype, new_prefix in (('*.jpg', 'IMG_'), ('*.mp4', 'VID_')):
        for filepath in glob.iglob(os.path.join(path, filetype)):
            filename = os.path.basename(filepath)
            if filename.startswith(pxl_prefix):
                newname = os.path.join(
                    path, filename.replace(pxl_prefix, new_prefix))
                if not os.path.exists(newname):
                    os.rename(filepath, newname)
                    if verbose:
                        print(f'{filepath} -> {newname}')


def rename_suffix(path, from_suffix='.MP.jpg', to_suffix='_MV.jpg',
                  verbose=False):
    for filepath in glob.iglob(os.path.join(path, f'*{from_suffix}')):
        newname = filepath.replace(from_suffix, to_suffix)
        if not os.path.exists(newname):
            os.rename(filepath, newname)
            if verbose:
                print(f'{filepath} -> {newname}')


def append(path, ext, suffix, verbose=False):
    for filepath in glob.iglob(os.path.join(path, '*.' + ext)):
        s = filepath.split(f'.{ext}')
        newname = f'{s[0]}_{suffix}.{ext}'
        if not os.path.exists(newname):
            os.rename(filepath, newname)
            if verbose:
                print(f'{filepath} -> {newname}')


def prepend(path, suffix, prefix, verbose=False):
    for filepath in glob.iglob(os.path.join(path, '*.' + suffix)):
        filename = os.path.basename(filepath)
        if filename.startswith(prefix):
            continue
        newname = os.path.join(path, prefix + '_' + filename)
        if not os.path.exists(newname):
            os.rename(filepath, newname)
            if verbose:
                print(f'{filepath} -> {newname}')


def main(path, verbose=False):
    undo_pxl(path, verbose=verbose)
    rename_suffix(path, verbose=verbose)
    rename_suffix(path, from_suffix='.NIGHT.jpg', to_suffix='.jpg',
                  verbose=verbose)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Rename some files.')
    parser.add_argument('path', type=str, help='Path name')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()
    main(args.path, verbose=args.verbose)
