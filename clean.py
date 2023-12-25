#!/usr/bin/env python3

'''
Connects to the Fathom Gmail account, and either lists mailboxes or
pulls all message IDs and writes them to a file.

1. Make sure no list.json file exists, run this once.
2. Edit the list.json file to remove mailboxes that should not be included.
'''

import json
import os

import imapdedup

HERE = os.path.dirname(os.path.realpath(__file__))
WORK = os.path.join(HERE, 'work')
if not os.path.exists(WORK):
    os.makedirs(WORK)

list_path = os.path.join(WORK, 'list.json')
google_id_path = os.path.join(WORK, 'google-ids.txt')
franklin_id_path = os.path.join(WORK, 'franklin-ids.txt')


if not os.path.exists(list_path):
    print(f'Saving list of mailboxes to {list_path}')
    print('Remove any entries from that file, and run again to create a list of IDs')
    options = [
        "--save-list", list_path
    ]
    imapdedup.process(*imapdedup.get_arguments(google_options + options))

elif not os.path.exists(google_id_path):
    print(f'Writing a list of all message IDs on Google at {google_id_path}')
    print('Run again to create the list of IDs on Franklin.')
    options = [
        "--save-ids", google_id_path,
        "--dry-run"  # don't mark any found items for deletion
    ]
    with open(list_path, 'r') as f:
        mboxes = json.load(f)

    imapdedup.process(*imapdedup.get_arguments(google_options + options + mboxes))

elif not os.path.exists(franklin_id_path):
    print(f'Writing a list of all recovered message IDs on Franklin at {google_id_path}')
    print('Run again to compare the two lists.')
    options = [
        "--save-ids", franklin_id_path,
        "--dry-run"  # don't mark any found items for deletion
    ]
    mboxes = [ 'recovered' ]

    imapdedup.process(*imapdedup.get_arguments(franklin_options + options + mboxes))

else:
    options = [
        "--delete-ids", google_id_path,
        # "--dry-run"  # don't mark any found items for deletion
    ]
    mboxes = [ 'recovered' ]

    imapdedup.process(*imapdedup.get_arguments(franklin_options + options + mboxes))

    #

    print('List of message IDs not found in both locations:')
    gmail = set()
    with open(google_id_path) as f:
        for line in f:
            gmail.add(line.strip())

    recovered = set()
    with open(franklin_id_path) as f:
        for line in f:
            recovered.add(line.strip())
    recovered_count = len(recovered)

    remaining = recovered - gmail
    # for item in remaining:
    #     print(item)
    print(f'Found {len(remaining):,} unmwatched out of {recovered_count:,}')
