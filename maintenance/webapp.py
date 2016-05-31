import os
from flask import Flask, request
from github import Github

GITHUB_API_URL = 'https://api.github.com/'

app = Flask(__name__)

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

@app.route("/hook", methods=['POST'])
def hook():

    # Only check pull requests
    if request.headers['X-GitHub-Event'] != 'pull_request':
        return 'No action needed'

    # Only consider merge events
    if request.json['action'] != 'closed' or request.json['pull_request']['merged_at'] is None:
        return 'No action needed'

    merged_by = request.json['pull_request']['merged_by']['login']

    issues = []

    if request.json['pull_request']['milestone'] is None:
        issues.append("The milestone has not been set")

    if len(issues) > 0:

        message = "@{0} - I noticed the following issues with this merged pull request:\n\n".format(merged_by)
        for issue in issues:
            message += "* {0}\n".format(issue)

        message += "\nPlease fix these - thanks!\n"

    else:

        message = "@{0} - all good!⭐️\n".format(merged_by)

    GITHUB = Github(login_or_token=GITHUB_TOKEN)
    REPO = GITHUB.get_repo('astrofrog/testrepo')
    pr = REPO.get_pull(int(request.json['number']))
    pr.create_issue_comment(message)

    return message

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
