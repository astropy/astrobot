import os
import re
from flask import Flask, request
from github import Github

GITHUB_API_URL = 'https://api.github.com/'

app = Flask(__name__)

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

BLOCK_PATTERN = re.compile('\[#.+\]', flags=re.DOTALL)
ISSUE_PATTERN = re.compile('#[0-9]+')


def find_prs_in_changelog(content):
    issue_numbers = []
    for block in BLOCK_PATTERN.finditer(content):
        block_start, block_end = block.start(), block.end()
        block = content[block_start:block_end]
        for m in ISSUE_PATTERN.finditer(block):
            start, end = m.start(), m.end()
            issue_numbers.append(int(block[start:end][1:]))
    return issue_numbers


@app.route("/hook", methods=['POST'])
def hook():

    # Only check pull requests
    if request.headers['X-GitHub-Event'] != 'pull_request':
        return 'No action needed'

    # Only consider merge events
    if request.json['action'] != 'closed' or request.json['pull_request']['merged_at'] is None:
        return 'No action needed'

    merged_by = request.json['pull_request']['merged_by']['login']

    gh = Github(login_or_token=GITHUB_TOKEN)
    repo = gh.get_repo('astrofrog/testrepo')
    pr = repo.get_pull(int(request.json['number']))

    issues = []

    if request.json['pull_request']['milestone'] is None:
        issues.append("The milestone has not been set")

    issue = repo.get_issue(pr.number)
    labels = [label.name for label in issue.labels]

    changelog_entry = False
    for fl in pr.get_files():
        if fl.filename == 'CHANGES.rst':
            numbers = find_prs_in_changelog(fl.patch)
            changelog_entry = pr.number in numbers

    if 'no-changelog-entry-needed' in labels:
        if changelog_entry:
            issues.append("Changelog entry present but no-changelog-entry-needed label set")
    if 'affects-dev' in labels:
        if changelog_entry:
            issues.append("Changelog entry present but affects-dev label set")
    else:
        if not changelog_entry:
            issues.append("Changelog entry not present (or pull request number missing) and neither affects-dev nor no-changelog-entry-needed are set")

    if len(issues) > 0:

        message = "@{0} - I noticed the following issues with this merged pull request:\n\n".format(merged_by)
        for issue in issues:
            message += "* {0}\n".format(issue)

        message += "\nPlease fix these - thanks!\n"

    else:

        message = "@{0} - all good!⭐️\n".format(merged_by)

    pr.create_issue_comment(message)

    return message

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
