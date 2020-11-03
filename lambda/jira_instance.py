# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class JiraInstance:
    # Constants
    # Issue types
    TYPE_TASK = {"Name": "Task", "API": "rest/api/2/issue"}
    TYPE_STORY = {"Name": "Story", "API": "rest/api/2/issue"}
    TYPE_EPIC = {"Name": "Epic", "API": "rest/api/2/issue"}

    # Issue states
    STATUS_TODO = "To Do"
    STATUS_IN_PROGRESS = "In Progress"
    STATUS_DONE = "Complete"

    # End point types
    QUERY = {"API": "rest/api/2/search"}

    # URLs
    BASE_RESOURCE_URL = "https://api.atlassian.com/oauth/token/accessible-resources"
    BASE_API_URL = "https://api.atlassian.com/ex/jira"
    
    def __init__(self, access_token):
        self.site_id = None
        self.access_token = access_token
        self.headers = {'content-type': 'application/json', 'authorization': f'Bearer {self.access_token}'}

    def set_site_id(self):
        """Obtains and sets the site id from the Jira API app"""
        # Construct headers
        headers = {'content-type': 'application/json', 'authorization': f'Bearer {self.access_token}'}

        # Invoke call to API to return resource details and site
        response = requests.get(self.BASE_RESOURCE_URL, headers=headers)

        # Check return code
        status_code = response.status_code

        # Check the status
        if status_code != 200:
            return False
        else:
            # Get the site ID
            response_json = response.json()
            site_id = response_json[0]['id']
            print(f"Got site ID: {site_id}")
            self.site_id = site_id
            return True

    def create_issue(self, issue_type, issue_summary, project_key):
        """Creates a Jira issue object in the given project"""

        # Construct the API URL
        api = issue_type["API"]
        issue_type_name = issue_type["Name"]
        jira_rest_url = f"{self.BASE_API_URL}/{self.site_id}/{api}"

        # Construct the JSON payload
        data = {
            "fields": {
                "project": {
                    "key": project_key,
                },
                "issuetype": {
                    "name": issue_type_name,
                },
                "summary": issue_summary,
            }
        }

        # Invoke the API
        response = requests.post(jira_rest_url, headers=self.headers, json=data)

        # Process status
        status_code = response.status_code
        if status_code != 201:
            # Failed
            return False, None
        else:
            # Success
            response_json = response.json()
            issue_key = response_json['key']
            return True, issue_key

    def issue_count(self, issue_type, use_status, status, project_key):
        """Gets a count of issues with type and status"""

        # Get list of issues and grab total
        status, response = self.get_issue_list(issue_type, use_status, status, project_key)
        status_code = response.status_code
        if status_code != 200:
            # Failed
            return False, None
        else:
            # Success
            response_json = response.json()
            total = response_json['total']
            return True, total

    def issue_summaries(self, issue_type, use_status, status, project_key):
        """Get a list of issue summaries with type and status"""
        status, response = self.get_issue_list(issue_type, use_status, status, project_key)
        status_code = response.status_code
        if status_code != 200:
            # Failed
            return False, None
        else:
            # Success. Parse the issue responses into a speakable string
            response_json = response.json()
            issue_summaries = ""
            issues = response_json["issues"]
            for issue in issues:
                issue_summaries += f'{issue["fields"]["summary"]}. '
            return True, issue_summaries

    def get_issue_list(self, issue_type, use_status, status, project_key):
        """Query the REST API for issues with type and status"""

        # Construct the API URL
        api = self.QUERY["API"]
        jira_rest_url = f"{self.BASE_API_URL}/{self.site_id}/{api}"
        issue_type_name = issue_type["Name"]

        # Construct the JSON payload
        if use_status:
            jql = f"project = {project_key} AND status={status} AND type={issue_type_name}"
        else:
            jql = f"project = {project_key} AND type={issue_type_name}"
        data = {
                "jql": jql,
                "startAt": 0,
                "maxResults": 15,
                "fields": [
                    "summary",
                    "status",
                    "assignee"
                ]
        }

        # Invoke the API
        response = requests.post(jira_rest_url, headers=self.headers, json=data)

        # Process status
        status_code = response.status_code
        if status_code != 200:
            # Failed
            return False, None
        else:
            # Success
            return True, response
