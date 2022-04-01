import os
import shutil
import sys
import json
from argparse import ArgumentParser
from rich.console import Console

parser = ArgumentParser()
parser.add_argument('-p', '--path', help='Absolute path to all backups', required=True)
parser.add_argument('-r', '--remote', help='Absolute path to top level restore directory', required=True)
parser.add_argument('-d', '--dry_run', help='Dry run, will only print out what would be done without taking any action', required=False, action='store_true')

args = parser.parse_args()

all_backups_path = args.path
remote_path = args.remote
backup_dirs = []
NAME_PATTERN = '_202'

console = Console()
error = 'bold red'
warning = 'bold yellow'
info = 'bold green'


def check_paths():
    paths = [args.path, args.remote]
    for local_path in paths:
        if not os.path.exists(local_path):
            console.print(f'Path "{local_path}" does not exist', style=error)
            sys.exit(1)


def get_directories(local_path):
    items = os.scandir(local_path)
    for item in items:
        if item.is_dir():
            backup_dirs.append(f'{local_path}/{item.name}')
            get_directories(f'{local_path}/{item.name}')


def get_files(directories):
    out = {}
    for directory in directories:
        items = os.scandir(directory)
        for item in items:
            if item.is_file():
                if NAME_PATTERN in item.name.strip():
                    if directory in out.keys():
                        out[directory].append(item.name.strip())
                    else:
                        out[directory] = [item.name.strip()]

    return out


def get_latest_backup(backups):
    tmp_backup_dict, latest_files = {}, {}

    backups = {k: [(x, x.split('_')[-1]) for x in v] for k, v in backups.items()}
    for local_path, files in backups.items():
        for backup_file in files:
            backup_date = backup_file[1][:8]
            backup_time = backup_file[1][8:14]
            filename = '_'.join(backup_file[0].split('_')[:-1])

            if f'{local_path}/{filename}' in tmp_backup_dict.keys():
                tmp_backup_dict[f'{local_path}/{filename}'].append(f'{backup_date}{backup_time}')
            else:
                tmp_backup_dict[f'{local_path}/{filename}'] = [f'{backup_date}{backup_time}']

    for key, values in tmp_backup_dict.items():
        file_path = '/'.join(key.split('/')[:-1])
        file_name = '/'.join(key.split('/')[:-1])

        latest_date = sorted(values)[-1]
        for files in backups[file_name]:
            if latest_date in files[1]:
                bk_file = files[0]

        if file_path in latest_files.keys():
            latest_files[file_path].append(bk_file)
        else:
            latest_files[file_path] = [bk_file]

    return latest_files


def move_latest_backups(backups, destination):
    copied = []

    for backup_path, backup_files in backups.items():

        for backup_filename in backup_files:
            backup_file = f'{backup_path}/{backup_filename}'
            new_filename = '_'.join(backup_filename.split('_')[:-1])
            # file_path = '/'.join(backup_path.split('/')[6:])
            file_path = '/'.join(backup_path.split('/')[2:])
            new_path = f'{destination}/{file_path}'

            if args.dry_run:
                copied.append((backup_file, f'{new_path}/{new_filename}'))
            else:
                try:
                    if not os.path.exists(new_path):
                        os.makedirs(new_path)
                    console.print(f'Coping {backup_file} to {new_path}/{new_filename}', style=info)
                    shutil.copy(backup_file, f'{new_path}/{new_filename}')
                    copied.append((backup_file, f'{new_path}/{new_filename}'))
                except Exception as e:
                    console.print(e, style=error)
                    console.print(f'There have been a problem while copying file {new_path}/{new_filename}', style=warning)

    if args.dry_run:
        console.print('\n- Dry run - !Taking No Action!\n', style=warning)
        for item in copied:
            console.print(f'[NOOP] copying {item[0]} to {item[1]}', style=warning)

        console.print(f'\n[NOOP] Copied {len(copied)} files to new locations\n', style=warning)
        console.print('- Dry run - !No Action Taken!', style=warning)
    else:
        console.print(f'\nCopied {len(copied)} files to new locations\n', style=error)


if __name__ == '__main__':
    check_paths()
    
    get_directories(all_backups_path)
    backup_files = get_files(backup_dirs)
    latest_backups = get_latest_backup(backup_files)
    
    move_latest_backups(latest_backups, remote_path)