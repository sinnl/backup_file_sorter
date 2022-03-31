Backup File Sorter
=========

The purpose of this script is to sort backup files based on the timestamp embedded in the filename. 


Description
------------

Script assumes:
* date is in the filename and is represented as a string with not special characters e.g. `20220101121244`
* date is on a format `YYYYMMDDHHMMSS`
* date is prefixed with `_`
* any number of characters can be used before `_` and after the date
* all files contain below patter in their name (this is to eliminate processing files that are not backup files):
  * `_202`


Script will travers the root path provided as a parameter and process all files matching the pattern above. Then it will
compare date string to pick each unique filename with the latest date string embedded in the filename
Finally it will create matching folder structure on `remote` path also provided as parameter and copy the backup file to
newly created folder, removing the timestamp from the file name. 


Usage
----------------

```commandline
usage: sort.py [-h] -p PATH -r REMOTE [-d]

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Absolute path to all backups
  -r REMOTE, --remote REMOTE
                        Absolute path to top level restore directory
  -d, --dry_run         Dry run, will only print out what would be done without taking any action
```

Usage Example
```commandline
python sort.py -p /backups -r /restored 
```
Dry run
```commandline
python sort.py -p /backups -r /restored -d
```

License
-------

BSD

Author Information
------------------

Lukasz Durlak, lukasz@itluk.eu


