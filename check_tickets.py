#!/usr/bin/env python3
# Author: Alex Culp
# Version: 0.5.1

from getpass import getpass
from requests_html import HTMLSession
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError 
import json
import re
import sys

def get_jenkins_tickets(jira_prefix, jenkins_urls):
    """
    Given Jenkins changelog URL, returns set of JIRA tickets mentioned in builds
    """
    jenkins_tickets = set()
    jira_pattern = re.compile(r'[hH][gG][\s-]?(\d+)')
    # go through ServerQE, then FrameworkQE
    for jenkins_url in jenkins_urls:
        print(f'[ Checking: {jenkins_url}... ]')
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
        print('\n[ Checking: JIRA... ]')
        jira_request = HTMLSession().get(url, auth=(user,pw))
        tickets = json.loads(jira_request.text) 
        # get *unique* set of HG-#### ticket keys
        return {ticket['key'] for ticket in tickets['issues']}  
    except JSONDecodeError as j:
        print('Check JIRA credentials or JQL query string\n', j.args)
        sys.exit(1) # json exception hangs 
    except ConnectionError as c:
        print('Check that JIRA is up', j.args)
        sys.exit(1) # connection error hangs 

if __name__ == "__main__":

    # print all tickets we find on Jenkins & JIRA
    DEBUG_MODE = sys.argv[-1] in ('--debug','-d')

    # load config file and map URLs
    with open('config.json', 'rt') as f:
        global config
        config = json.loads(f.read())
    
    JIRA_PROJECT_NAME   = config['jira']['JIRA_PROJECT_NAME']
    JIRA_QUERY_TEMPLATE = config['jira']['JIRA_QUERY_TEMPLATE']
    JIRA_REST_URL_BASE  = config['jira']['JIRA_REST_URL_BASE']
    JIRA_BROWSER_BASE   = config['jira']['JIRA_BROWSER_BASE']
    JENKINS_URLS        = tuple(config['jenkins_urls'])
 
    # grab JIRA tickets assigned to me
    user = input("username: ")
    password = getpass("password: ")
     
    # get JIRA tickets
    jira_tickets = get_jira_tickets(JIRA_REST_URL_BASE + 
            JIRA_QUERY_TEMPLATE.format(prefix=JIRA_PROJECT_NAME, u=user), user, password) 
    
    # grab Jenkins tickets
    jenkins_tickets = get_jenkins_tickets(JIRA_PROJECT_NAME, JENKINS_URLS)
    
    # print all tickets for debugging
    if DEBUG_MODE:
        print(f'\n[ DEBUG: JIRA ]\n{jira_tickets}\n')
        print(f'\n[ DEBUG: Jenkins ]\n{jenkins_tickets}\n') 
    
    # print intersection of my tickets and tickets on QE
    print('\n[ Ready: ]')
    
    for ticket in jira_tickets.intersection(jenkins_tickets):
        print('\t{}{}'.format(JIRA_BROWSER_BASE, ticket))

