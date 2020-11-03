import logging
from jira_instance import JiraInstance

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.setLevel(logging.INFO)


class AlexaJiraHelper:
    """Helper class to abstract Jira calls for Alexa consumption"""

    def __init__(self, access_token):
        self.jira_instance = JiraInstance(access_token)
        self.project_key = "PTD"
        self.connected = False
        # Get the Jira site ID
        ret_status = self.jira_instance.set_site_id()

        # Check we've got the site
        if not ret_status:
            self.connected = False
        else:
            self.connected = True

    def add_new_todo_task(self, task_summary):
        """Handle request to add a new Task"""
        issue_type = self.jira_instance.TYPE_TASK
        ret_status, issue_id = self.jira_instance.create_issue(issue_type, task_summary,
                                                               self.project_key)
        return ret_status, issue_id

    def todo_task_count(self):
        """Handle request to count Tasks"""
        issue_type = self.jira_instance.TYPE_TASK
        issue_status = self.jira_instance.STATUS_TODO
        ret_status, count = self.jira_instance.issue_count(issue_type, True, f"'{issue_status}'",
                                                           self.project_key)
        return ret_status, count

    def todo_task_list(self):
        """Handle request to list Tasks"""
        issue_type = self.jira_instance.TYPE_TASK
        issue_status = self.jira_instance.STATUS_TODO
        ret_status, issue_summaries = self.jira_instance.issue_summaries(issue_type, True, f"'{issue_status}'",
                                                                         self.project_key)
        return ret_status, issue_summaries
