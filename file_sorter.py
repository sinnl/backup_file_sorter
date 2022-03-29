import os
import shutil
import sys
import glob
import json
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-p', '--path', help='Absolute path to all backups', required=True)
parser.add_argument('-l', '--latest', help='Absolute path to where latest backups should be moved', required=True)
parser.add_argument('-a', '--archive', help='Absolute path to where archive backups should be moved', required=True)
parser.add_argument('-d', '--dry_run', help='Dry run, will only print out what would be done without taking any action', required=False, action='store_true')

args = parser.parse_args()

all_backups_path = args.path
archive_backups_path = args.latest
latest_backups_path = args.archive


def check_paths():
    paths = [args.path, args.latest, args.archive]
    for local_path in paths:
        if not os.path.exists(local_path):
            print(f'Path "{local_path}" does not exist')
            sys.exit(1)


def get_backup_file_name(backup_file_path, backup_date):
    file = f'{backup_file_path}/*_{backup_date}*'
    backup_file = glob.glob(file)[0]
    return backup_file


def get_all_files(local_path):
    output = []
    all_items = os.scandir(path=local_path)
    for item in all_items:
        if item.is_file():
            output.append(f'{local_path}/{item.name}')

    return output


def generate_backup_dict(all_backups):
    tmp_backup_dict, out = {}, {}
    backup_dates = [x.split('_')[-1] for x in all_backups]

    for item in backup_dates:
        backup_date = item[:8]
        backup_time = item[8:12]
        if backup_date in tmp_backup_dict.keys():
            tmp_backup_dict[backup_date].append(backup_time)
        else:
            tmp_backup_dict[backup_date] = [backup_time]

    for key, values in tmp_backup_dict.items():
        out.update({key: sorted(values)})

    return out


def get_latest_backups(backups, backups_path):
    out = []
    for key, value in backups.items():
        backup_date = key
        backup_time = value[-1]
        out.append(get_backup_file_name(backups_path, f'{backup_date}{backup_time}'))

    return out


def move_latest_backups(backups, destination):
    for backup_file in backups:
        shutil.move(backup_file, destination)


def archive_backups(all_backups, latest, destination):
    backups_to_archive = [x for x in all_backups if x not in latest]
    for backup_file in backups_to_archive:
        shutil.move(backup_file, destination)


if __name__ == '__main__':
    check_paths()
    all_backup_files = get_all_files(all_backups_path)
    bk_dk = generate_backup_dict(all_backup_files)
    latest_backups = get_latest_backups(bk_dk, all_backups_path)

    if args.dry_run:
        print(f'would Moved {len(latest_backups)} files to {args.latest}')
        print(f'Would Moved {len(all_backup_files) - len(latest_backups)} files to {args.archive}' + '\n')

        print(f'Latest backups:')
        print('\n'.join(latest_backups) + '\n')
        print('No action has been taken')
    else:
        move_latest_backups(latest_backups, latest_backups_path)
        archive_backups(all_backup_files, latest_backups, archive_backups_path)

        print(f'Moved {len(latest_backups)} files to {args.latest}')
        print(f'Moved {len(all_backup_files) - len(latest_backups)} files to {args.archive}')
        print(f'Folder {args.path} should now be empty')