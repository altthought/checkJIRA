#!/usr/bin/env python3
# Author: Alex Culp
# Version: 0.3.0 (release)

from getpass import getpass
from json.decoder import JSONDecodeError
from requests_html import HTMLSession
from requests.exceptions import ConnectionError
import sys
import json
import re

# JIRA base URLs 
JIRA_REST_URL_BASE    = 'https://resource.marketo.com/jira/rest/api/latest/search?jql='
JIRA_BROWSER_URL_BASE = 'https://resource.marketo.com/jira/browse/'

# Mercury 'resolved' tickets assigned to netID "u" (template)
JIRA_QUERY_TEMPLATE = '(reporter={u} or assignee={u} or verifier={u}) ' \
                      'and project=HG and status=resolved'

# Jenkins URLs for parsing
MERCURYSERVER_QE_URL    = 'http://sjbuild2.marketo.org:8080/job/MercuryServer-QE/changes'
MERCURYFRAMEWORK_QE_URL = 'http://sjbuild2.marketo.org:8080/job/MercuryFramework-QE/changes'

def get_jira_tickets(url, user, pw):  
   # NOTE: THIS IS _NOT_ SECURE AUTH! 
   jira_request = HTMLSession().get(url, auth=(user,pw))
   try:
      tickets = json.loads(jira_request.text) 
      # get _unique_ set of HG-#### ticket keys
      return {ticket['key'] for ticket in tickets['issues']}  
   except JSONDecodeError as j:
      print('Check JIRA credentials or JQL query string\n', j.args)
      sys.exit(1) # json exception hangs, need to manually exit
   except ConnectionError as c:
      print('Check that JIRA is up', j.args)
      sys.exit(1) # connection error hangs, manual exit

def get_jenkins_tickets(*jenkins_urls):    
   patt = re.compile('[hH][gG]-?(\d+)')
   jenkins_tickets = set() 
   # mercuryServer-QE v mercuryFramework-QE
   for url in jenkins_urls: 
      try: 
         print('Checking {}...'.format(url))
         jenkins_changes = HTMLSession().get(url).html.find('li')
         # go through changelog notes
         for li in jenkins_changes: 
            match = patt.search(li.text) 
            if match:
               # force formatting to HG-XXXX to match JIRA
               jenkins_tickets.add('HG-' + match.group(1))
      except ConnectionError as c:
         print("Check VPN connection, Jenkins appears down\n\n",c.args)
         sys.exit(1) # NOTE do not continue if VPN drops -- very slow drop
   # return unique tickets built on QE 
   return jenkins_tickets
         
if __name__ == "__main__":
   # debug mode flag as command line argument
   DEBUG = len(sys.argv) > 1 and sys.argv[-1] in ['-d','-debug', '--debug']
   if DEBUG:
      print('[ debug enabled ]')
   # get JIRA credentials
   username = input('username: ') 
   password = getpass('password: ')  
   # check JIRA
   jira_url = JIRA_REST_URL_BASE + JIRA_QUERY_TEMPLATE.format(u=username)  
   # get 'resolved' Mercury JIRA tickets and check against QE  
   print('Checking JIRA...')
   jira_tickets = get_jira_tickets(jira_url,username,password)  
   if DEBUG:
      for ticket in jira_tickets:
         print('JIRA Ticket:',ticket)
   if jira_tickets:
      print('[ {} assigned JIRA tickets found ]'.format(len(jira_tickets)), end='\n\n')
   else:
      print(f'[ No tickets assigned to "{username}" by that query ]')
      sys.exit(1) # skip slow jenkins parsing if you have no assigned tickets  
   print('Checking Jenkins changelog...') 
   jenkins_tickets = get_jenkins_tickets(MERCURYSERVER_QE_URL,MERCURYFRAMEWORK_QE_URL)
   if DEBUG:
      for ticket in jenkins_tickets:
         print('Jenkins Ticket:',ticket)
      print('[ end of Jenkins tickets ]')
   if jenkins_tickets:
      print('[ {} tickets found on Jenkins ]'.format(len(jenkins_tickets)), end='\n\n')
   else:
      print('[ no tickets found on Jenkins -- are you sure the page is up? ]')
   # print overlap of jenkins tickets and jira tickets 
   for ticket in jenkins_tickets.intersection(jira_tickets): 
      print('Ready: ', JIRA_BROWSER_URL_BASE + ticket) 
