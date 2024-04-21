#!/usr/bin/env python3

'''
Cleanup script to deal with Apple Mail placing thousands of emails in
local "Recovered Messages" folders. After moving these to an IMAP folder,
this script is used to scan source accounts and then purge entries from
that IMAP folder.

Config is read from a JSON file with login parameters for the source
and target server. Action happens in multiple passes:

1. If the config is called 'blah.json', start this with './clean.py blah.json'.
   This will create the folder 'blah' and list all folders on the source.

2. Edit blah/mailboxes.json to remove folders that should not be scanned.
   Run the script again to download all message IDs from those folders.

3. Run the script a third time to get all messages IDs from the (single)
   target IMAP folder where the "Recovered Messages" were uploaded.

4. Run a fourth time to mark all messages seen in the first folders
   for deletion in the target folder. (Un-comment the --dry-run at
   line ~89 in this file to not delete, and just list what would happen.)

If using a Google Mail account, need to first set an app password:
https://myaccount.google.com/u/2/apppasswords
(the /u/2 depends on which Google account is in the browser...)
'''

import json
import os
import sys

import imapdedup


def handle(config_path):
    if not os.path.exists(config_path):
        print(f'{config_path} does not exist')
        sys.exit(1)

    work_path = config_path[:-5]
    if not os.path.exists(work_path):
        os.makedirs(work_path)

    with open(config_path) as f:
        parsed = json.load(f)

    for key, args in parsed.items():
        print(key)
        # source_options = parsed['source']
        # target_options = parsed['target']

    '''
    list_path = os.path.join(work_path, 'mailboxes.json')
    source_id_path = os.path.join(work_path, 'source-ids.txt')
    target_id_path = os.path.join(work_path, 'target-ids.txt')

    if not os.path.exists(list_path):
        print(f'Saving list of mailboxes to {list_path}')
        print('Remove any entries from that file, and run again to create a list of IDs')
        options = [
            "--save-list", list_path
        ]
        imapdedup.process(*imapdedup.get_arguments(source_options + options))

    elif not os.path.exists(source_id_path):
        print(f'Writing a list of all message IDs from the source to {source_id_path}')
        print('Run again to create the list of IDs on the target.')
        options = [
            "--save-ids", source_id_path,
            "--dry-run"  # don't mark any found items for deletion
        ]
        with open(list_path, 'r') as f:
            mboxes = json.load(f)

        imapdedup.process(*imapdedup.get_arguments(source_options + options + mboxes))

    elif not os.path.exists(target_id_path):
        print(f'Writing a list of all recovered message IDs on the target at {source_id_path}')
        print('Run again to compare the two lists.')
        options = [
            "--save-ids", target_id_path,
            "--dry-run"  # don't mark any found items for deletion
        ]
        mboxes = [ 'recovered' ]

        imapdedup.process(*imapdedup.get_arguments(target_options + options + mboxes))

    else:
        options = [
            "--delete-ids", source_id_path,
            # "--dry-run"  # don't mark any found items for deletion
        ]
        mboxes = [ 'recovered' ]

        imapdedup.process(*imapdedup.get_arguments(target_options + options + mboxes))

        #

        print('List of message IDs not found in both locations:')
        gmail = set()
        with open(source_id_path) as f:
            for line in f:
                gmail.add(line.strip())

        recovered = set()
        with open(target_id_path) as f:
            for line in f:
                recovered.add(line.strip())
        recovered_count = len(recovered)

        remaining = recovered - gmail
        # for item in remaining:
        #     print(item)
        print(f'Found {len(remaining):,} unmwatched out of {recovered_count:,}')
    '''


if __name__ == "__main__":
    if len(sys.argv) == 2:
        handle(sys.argv[1])
    else:
        print(f'Usage: {sys.argv[0]} <config json name>')
