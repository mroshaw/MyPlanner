# Simple tests
from alexa_jira_helper import AlexaJiraHelper


def do_test():

    # Test data
    task_summary = "This is a test task"
    access_token = "<PASTE TOKEN FROM POSTMAN HERE>"

    # Initialise Jira connection
    jira_helper = AlexaJiraHelper(access_token)
    if not jira_helper.connected:
        print("Sorry, couldn't connect to Jira")
        return

    # Test - add new task
    print(f"Adding task: {task_summary}")

    ret_status, issue_key = jira_helper.add_new_todo_task(task_summary)
    if ret_status:
        print(f"Success. Issue key {issue_key}")
    else:
        print("Sorry, create failed.")

    # Test - task count
    print(f"Getting task count")

    ret_status, count = jira_helper.todo_task_count()
    if ret_status:
        print(f"Success. Issue count {count}")
    else:
        print("Sorry, count failed.")

    # Test - task summaries
    print(f"Getting task summaries")

    ret_status, task_summaries = jira_helper.todo_task_list()
    if ret_status:
        print(f"Success. Issue summaries: {task_summaries}")
    else:
        print("Sorry, issue list failed.")


# Run the main function
if __name__ == '__main__':
    do_test()
