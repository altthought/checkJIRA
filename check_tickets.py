#!/usr/bin/env python3
# Author: Alex Culp
# Version: 0.5.3

from getpass import getpass
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError, HTTPError
import urllib3
import requests
import json
import re
import sys

def get_jenkins_tickets(jira_prefix, jenkins_urls):
    """
    Given Jenkins changelog URL, returns set of JIRA tickets mentioned in builds
    """
    jenkins_tickets = set()
    ticket_number = r'[\s-]?(\d+)' 
    # regex pattern for tickets in form: 'HG 3323' / 'HG-3323' / 'Hg3323'
    jira_pattern = re.compile(jira_prefix + ticket_number, re.IGNORECASE)
    # go through jenkins jobs
    for jenkins_url in jenkins_urls:
        print(f'[ Fetching: {jenkins_url}... ]')
        try:
            # fetch build info from changelog (ignore self-signed cert)
            r = requests.get(jenkins_url, verify=False)
            changelog_json = json.loads(r.text)
        except ConnectionError as c:
            print('Check VPN connection! Exiting...\n\n', c.args)
            sys.exit(1) # VPN necessary to grab ticket information!
        except HTTPError as h:
            print('Jenkins is down!\n\n', h.args)
            sys.exit(1) # Jenkins breaks query
        build_urls = [build['url'] for build in changelog_json['builds']]
        # go through individual builds for each jenkins job
        for build_url in build_urls: 
            try:
                # turn off SSL verification (self-signed cert)
                r = requests.get(f'{build_url}/api/json', verify=False)
                if r.status_code != 200:
                    print('Failure to parse: invalid page')
                    sys.exit(1)
                build_data = json.loads(r.text)
            except urllib3.exceptions.InsecureRequestWarning:
                print('skipping',r.url)
            # need changelog count per build to search messages
            changelog_size = len(build_data['changeSet']['items'])
            # check each change for a JIRA ticket reference
            for change in range(changelog_size):
                msg = build_data['changeSet']['items'][change]['msg']
                match = jira_pattern.search(msg) 
                # search changelog message for JIRA ticket
                if match:
                    # force formatting to HG-XXXX to match JIRA
                    jenkins_tickets.add(f'{jira_prefix}-{match.group(1)}')
    return jenkins_tickets

def get_jira_tickets(url, user, pw):  
    """ 
    Grab tickets from JIRA query URL (JQL)
    **************************************
    *  NOTE: THIS IS _NOT_ SECURE AUTH!  *
    **************************************
    """
    try:
        print('\n[ Fetching: JIRA... ]')
        jira_request = requests.get(url, auth=(user,pw))
        tickets = json.loads(jira_request.text) 
        # get *unique* set of HG-#### ticket keys
        return {ticket['key'] for ticket in tickets['issues']}  
    except JSONDecodeError as j:
        print('Incorrect JIRA username/password or broken JQL query!\n', j.args)
        sys.exit(1) # json exception hangs 
    except ConnectionError as c:
        print('Check that JIRA is up', c.args)
        sys.exit(1) # connection error hangs 

def main(): 
    # warnings for internal self-signed certs are useless
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # print all tickets we find on Jenkins & JIRA
    DEBUG_FLAG = sys.argv[-1] in ('--debug','-d')

    # load config file and map URLs
    config = {}
    with open('config.json', 'rt') as f:
        config = json.loads(f.read())
    try:
        JIRA_PROJECT      = config['JIRA_PROJECT']
        JIRA_TEMPLATE     = config['JIRA_TEMPLATE']
        JIRA_URL_BASE     = config['JIRA_URL_BASE']
        JIRA_BROWSER_BASE = config['JIRA_BROWSER_BASE']
        JENKINS_URLS      = config['JENKINS_URLS']
    except KeyError as k:
        print("failed to load key:", k.args)
        sys.exit(1)

    # grab JIRA tickets assigned to me
    user = input("username: ")
    password = getpass("password: ")

    while True:
        # get JIRA tickets
        JIRA_URL = JIRA_URL_BASE + JIRA_TEMPLATE.format(project=JIRA_PROJECT, u=user) 
        jira_tickets = get_jira_tickets(JIRA_URL, user, password) 
        
        # grab Jenkins tickets
        jenkins_tickets = get_jenkins_tickets(JIRA_PROJECT, JENKINS_URLS)
        
        # print all tickets for debugging
        if DEBUG_FLAG:
            print(f'\n[ DEBUG: JIRA ]\n{jira_tickets}\n')
            print(f'\n[ DEBUG: Jenkins ]\n{jenkins_tickets}\n') 
        
        # print intersection of my tickets and tickets on QE
        print('\n[ Ready: ]')
        
        for ticket in jira_tickets.intersection(jenkins_tickets):
            print('\t{}{}\n'.format(JIRA_BROWSER_BASE, ticket))
        
        # stop scanning
        if input("Check again? (Y/n): ") not in 'yY':
            break

if __name__ == "__main__":
    main()
