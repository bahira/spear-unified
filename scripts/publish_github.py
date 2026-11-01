"""Publish the prepared plan to an existing private repository via authenticated gh."""
import argparse
import json
from pathlib import Path
import subprocess

p=argparse.ArgumentParser()
p.add_argument('repository',help='owner/repo; must already exist and be private')
a=p.parse_args()
def api(path,method='GET',body=None):
    cmd=['gh','api',path,'--method',method]
    if body is not None:cmd+=['--input','-']
    r=subprocess.run(cmd,input=json.dumps(body) if body is not None else None,text=True,capture_output=True)
    if r.returncode:raise SystemExit(r.stderr)
    return json.loads(r.stdout)
repo=api('repos/'+a.repository)
if not repo['private']:raise SystemExit('Expected a private repository')
plan=json.loads((Path(__file__).parent.parent/'github-plan.json').read_text())
existing=api(f'repos/{a.repository}/milestones?state=all&per_page=100')
numbers={x['title']:x['number'] for x in existing}
for m in plan['milestones']:
    if m['title'] not in numbers:
        numbers[m['title']]=api(f'repos/{a.repository}/milestones','POST',m)['number']
issues=api(f'repos/{a.repository}/issues?state=all&per_page=100')
known={x['title'] for x in issues}
for issue in plan['issues']:
    if issue['title'] in known:continue
    body={**issue,'milestone':numbers[issue['milestone']]}
    created=api(f'repos/{a.repository}/issues','POST',body)
    print(created['html_url'])
