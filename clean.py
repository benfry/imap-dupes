#!/usr/bin/env python3

'''
If using a Google Mail account, need to first set an app password:
https://myaccount.google.com/u/2/apppasswords
(the /u/2 depends on which Google account is in the browser...)

Connects to an account, and either lists mailboxes or
pulls all message IDs and writes them to a file.

1. Make sure no list.json file exists, run this once.
2. Edit the list.json file to remove mailboxes that should not be included.
'''

import json
import os
import sys

import imapdedup

# HERE = os.path.dirname(os.path.realpath(__file__))
# WORK = os.path.join(HERE, 'work')
# if not os.path.exists(WORK):
#     os.makedirs(WORK)

def handle(config_path):
    if not os.path.exists(config_path):
        print(f'{config_path} does not exist')
        sys.exit(1)

    work_path = config_path[:-5]
    if not os.path.exists(work_path):
        os.makedirs(work_path)

    with open(config_path) as f:
        parsed = json.load(f)
        source_options = parsed['source']
        target_options = parsed['target']

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


if __name__ == "__main__":
    if len(sys.argv) == 2:
        handle(sys.argv[1])
    else:
        print(f'Usage: {sys.argv[0]} <config json name>')