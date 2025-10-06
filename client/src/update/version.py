import os
import datetime
import subprocess
import tempfile
import shutil


def get_current_year_and_week():
    now = datetime.datetime.utcnow()
    year, week, _ = now.isocalendar()
    return year, week


def get_commit_count_local(path="."):
    year, week = get_current_year_and_week()
    try:
        result = subprocess.run(
            ["git", "-C", path, "log", "--pretty=%ct"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        commit_times = result.stdout.strip().split("\n")
        build = 0
        for t in commit_times:
            if not t:
                continue
            dt = datetime.datetime.utcfromtimestamp(int(t))
            y, w, _ = dt.isocalendar()
            if y == year and w == week:
                build += 1
        return build
    except Exception as e:
        raise RuntimeError(f"Error retrieving commits: {e}")


def get_commit_count_github_clone(repo_url):
    tempdir = tempfile.mkdtemp()
    try:
        subprocess.run(
            ["git", "clone", "--quiet", "--depth", "1000", repo_url, tempdir],
            check=True,
        )
        build = get_commit_count_local(tempdir)
    except Exception as e:
        raise RuntimeError(f"Error cloning repo: {e}")
    finally:
        shutil.rmtree(tempdir)
    return build


def get_version_number_local(target):
    year, week = get_current_year_and_week()
    build = get_commit_count_local(target)
    return f"{year}.{week}.{build}"


def get_version_number_github(target):
    year, week = get_current_year_and_week()
    build = get_commit_count_github_clone(target)
    return f"{year}.{week}.{build}"
