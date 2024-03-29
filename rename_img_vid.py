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


def change_ts_from_utc_to_local(path, extension='jpg', utc_offset=-7, verbose=False):
    """This is very specific to the case when Pam's photos
    were stamped with local time but mine were stamped in UTC.
    Since she took way more than I did, it is easier to change
    everything to local time to match hers. Her seconds stamp
    is also shorter than mine, which messed up the ordering
    by filename.

    For other usage, check/modify the logic first, as needed.

    """
    import datetime
    from pathlib import Path

    data_path = Path(path).resolve()
    all_files = sorted(glob.glob(str(data_path / f'*.{extension}')))
    for cur_filepath in all_files:
        cur_file = os.path.basename(cur_filepath)

        # Do not touch her files.
        if cur_filepath.endswith(f'_pam.{extension}'):
            if verbose:
                print(f'Skipping {cur_file} (belongs to Pam)')
            continue

        # Already changed before, skip.
        parts = cur_file.split('_')
        timestamp = parts[2].split('.')[0]
        if len(timestamp) != 9:
            if verbose:
                print(f'Skipping {cur_file} (found ts={timestamp})')
            continue

        try:
            t = datetime.datetime.strptime(cur_file, 'IMG_%Y%m%d_%H%M%S%f.jpg')
        except Exception as e:  # Pattern no match, skip
            if verbose:
                print(f'Skipping {cur_file} ({repr(e)})')
            continue

        dt = datetime.timedelta(hours=utc_offset)  # UTC -> local
        new_t = t + dt
        new_name = str(data_path / new_t.strftime('IMG_%Y%m%d_%H%M%S.jpg'))

        if os.path.exists(new_name):
            if verbose:
                print(f'Skipping {new_name}, file exists')
            continue

        os.rename(cur_filepath, new_name)
        if verbose:
            print(f'{cur_filepath} -> {new_name}')


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


def undo_whatsapp(path, verbose=False):
    for filepath in glob.iglob(os.path.join(path, '*-WA*.*')):
        basename = os.path.basename(filepath)
        newname = os.path.join(path, basename.replace('-', '_'))
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
