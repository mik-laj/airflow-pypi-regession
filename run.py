import argparse
import json
import random
import subprocess
import sys
from typing import List

from tabulate import tabulate

PIP_ARGS_VARIANTS =[
    "pip @ https://github.com/uranusjr/pip/archive/new-resolver-constraint-affects-extra-entry.zip",
    "pip==20.2.4"
]


parser = argparse.ArgumentParser()
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
args = parser.parse_args()

extras: List[str] = list(args.infile.read().split("\n"))
extras = [f for f in extras if f and not f.startswith("#")]
# random.shuffle(extras)
# extras = extras[:10]

print("Extras:")
print(extras)


def build_image(pip_arg, airflow_extras):
    extras = ",".join(airflow_extras)

    output = subprocess.check_output(
        [
            'gcloud',
            'builds',
            'submit',
            '--async',
            '--config=cloudbuild.yaml',
            f"--substitutions=^%^_AIRFLOW_EXTRAS={extras}%_PIP_INSTALL_ARG={pip_arg}",
            "--format=json",
        ],
        stderr=subprocess.DEVNULL
    )
    print()
    print()
    build = json.loads(output)
    log_url = build['logUrl']

    print(extras, "log_url=", log_url)
    build_id = build["id"]
    return build_id


def wait_for_builds(list_build_ids: List[str]):
    finished_build = []
    to_process_build_ids = list_build_ids.copy()
    while len(finished_build) != len(list_build_ids):
        build_statuses = get_build_statuses(to_process_build_ids[:16])
        random.shuffle(to_process_build_ids)
        for build_id, build_status in build_statuses.items():
            if build_status not in ('QUEUED', 'WORKING'):
                finished_build.append(build_id)
                to_process_build_ids.remove(build_id)
            if build_status == 'WORKING':
                to_process_build_ids.remove(build_id)
                to_process_build_ids.insert(0, build_id)

        print(f"Waiting: {len(finished_build)}/{len(list_build_ids)}")


def get_build_statuses(list_build_ids: List[str]):
    result = {}
    for build_id in list_build_ids:
        output = subprocess.check_output([
            'gcloud', 'builds', 'describe', build_id, '--format', 'json']
        )
        build = json.loads(output)
        result[build_id] = build['status']
    return result


def check_extras():
    builds = {}

    for extra_item in extras:
        for pip_arg in PIP_ARGS_VARIANTS:
            builds[(pip_arg, extra_item)] = build_image(pip_arg=pip_arg, airflow_extras=[extra_item])

    wait_for_builds(list(builds.values()))

    build_statuses = get_build_statuses(list_build_ids=list(builds.values()))
    result = {}
    for extra_item, build_id in builds.items():
        result[extra_item] = build_statuses[build_id]
    return result


result = check_extras()
# result = {"A": "Success"}

print(tabulate([[*k, v] for k, v in result.items()], headers=["Pip", "Extra", "Status"], tablefmt="github"))
