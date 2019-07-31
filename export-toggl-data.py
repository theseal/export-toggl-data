#!/usr/bin/env python3

import sys

import dateutil.parser as parser
import requests
from requests.auth import HTTPBasicAuth

BASEURL = "https://www.toggl.com/api/v8/"

TOKEN = sys.argv[1]
START = sys.argv[2]
END = sys.argv[3]
TIMEENTRYURL = BASEURL + "time_entries"

STARTISO = parser.parse(START)
ENDISO = parser.parse(END)

PARAMS = {
    'start_date': STARTISO.isoformat() + "+02:00",
    'end_date': ENDISO.isoformat() + "+02:00"
}


def main():
    response = requests.get(
        TIMEENTRYURL, auth=HTTPBasicAuth(TOKEN, 'api_token'), params=PARAMS)

    timedict = {}
    totaltime = 0
    for entry in response.json():
        pid = entry['pid']
        duration = entry['duration']
        tags = entry['tags']
        if len(tags) != 1:
            print("Invalid amount of tags")
            sys.exit(1)
        tag = tags[0]
        totaltime += duration

        if not timedict.get(pid):
            timedict[pid] = {tag: duration}
        else:
            if not timedict[pid].get(tag):
                timedict[pid].update({tag: duration})
            else:
                timedict[pid][tag] += duration

    for entry in timedict:
        projecturl = BASEURL + "projects/" + str(entry)
        response = requests.get(
            projecturl, auth=HTTPBasicAuth(TOKEN, 'api_token'))
        name = response.json()['data']['name']
        for tag in timedict[entry]:
            value = round(int(timedict[entry][tag]) / 60 / 60, 1)
            print('{} - {}: {} hours'.format(name, tag, value))

    print('Total {} hours during {} - {}'.format(
        round(totaltime / 60 / 60, 1), START, END))


if __name__ == '__main__':
    main()
