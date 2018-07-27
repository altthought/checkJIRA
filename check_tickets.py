#!/usr/bin/env python3
# Author: Alex Culp
# Version: 0.4.1

from getpass import getpass
from requests_html import HTMLSession
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError 
import json
import re
import sys

def get_jenkins_tickets(*jenkins_urls):
    """
    Given Jenkins changelog URL, returns set of JIRA tickets mentioned in builds
    """
    jenkins_tickets = set()
    jira_pattern = re.compile(r'[hH][gG][\s-]?(\d+)')
    # go through ServerQE, then FrameworkQE
    for jenkins_url in jenkins_urls:
        print(f'Checking: {jenkins_url}...')
        try:
            # grab individual build URLs from the main changelog page 
            changelog_json = json.loads(HTMLSession().get(jenkins_url).text)
        except ConnectionError as c:
            print('Check VPN connection! Exiting...\n', c.args)
            sys.exit(1) # VPN necessary to grab ticket information!
        build_urls = [build['url'] for build in changelog_json['builds']]
        # go through individual builds
        for build_url in build_urls: 
            build_data = json.loads(HTMLSession().get(f'{build_url}/api/json').text)
            # need change count per build to search messages
            change_count = len(build_data['changeSet']['items'])
            # check each change for a JIRA ticket reference
            for change in range(change_count):
                msg = build_data['changeSet']['items'][change]['msg']
                match = jira_pattern.search(msg) 
                # search changelog message for JIRA ticket
                if match:
                    # force formatting to HG-XXXX to match JIRA
                    jenkins_tickets.add('HG-' + match.group(1))
    return jenkins_tickets

def get_jira_tickets(url, user, pw):  
    """ 
    Grab tickets from JIRA query URL (JQL)
    *************************************
    *  NOTE: THIS IS _NOT_ SECURE AUTH! *
    *************************************
    """
    try:
        print('Checking: JIRA...')
        jira_request = HTMLSession().get(url, auth=(user,pw))
        tickets = json.loads(jira_request.text) 
        # get _unique_ set of HG-#### ticket keys
        return {ticket['key'] for ticket in tickets['issues']}  
    except JSONDecodeError as j:
        print('Check JIRA credentials or JQL query string\n', j.args)
        sys.exit(1) # json exception hangs for several seconds
    except ConnectionError as c:
        print('Check that JIRA is up', j.args)
        sys.exit(1) # connection error hangs for several seconds

if __name__ == "__main__":
    # JIRA base URLs 
    JIRA_REST_URL_BASE    = 'https://resource.marketo.com/jira/rest/api/latest/search?jql='
    JIRA_BROWSER_URL_BASE = 'https://resource.marketo.com/jira/browse/'
            
    # Mercury 'resolved' tickets assigned to netID "u" (template)
    JIRA_QUERY_TEMPLATE = '(reporter={u} or assignee={u} or verifier={u}) ' \
                        'and project=HG and status=resolved'
        
    # Jenkins API endpoints
    SERVER_QE_URL    = 'http://sjbuild2.marketo.org:8080/job/MercuryServer-QE/api/json'
    FRAMEWORK_QE_URL = 'http://sjbuild2.marketo.org:8080/job/MercuryFramework-QE/api/json'
        
    DEBUG_MODE = sys.argv[-1] in ['-d', '--debug']     
    # grab JIRA tickets assigned to me
    username = input("username: ")
    password = getpass("password: ")
    # get JIRA tickets
    jira_tickets = get_jira_tickets(JIRA_REST_URL_BASE + 
            JIRA_QUERY_TEMPLATE.format(u=username),username,password) 
    # grab Jenkins tickets
    jenkins_tickets = get_jenkins_tickets(FRAMEWORK_QE_URL,SERVER_QE_URL) 
    # debug info for ticket fetching
    if DEBUG_MODE:
        print('[ DEBUG: JIRA ]\n', jira_tickets) 
        print('[ DEBUG: Jenkins ]\n', jenkins_tickets)
    # print intersection of my tickets and tickets on QE
    print('Workable tickets:')
    for ticket in jira_tickets.intersection(jenkins_tickets):
        print('\t{}{}'.format(JIRA_BROWSER_URL_BASE, ticket))

