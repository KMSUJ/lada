import subprocess


def get_revision_hash():
    try:
        result = subprocess.check_output(["git", "rev-parse", "HEAD"])
        result = result.decode()
        result = result.strip()
        return result
    except FileNotFoundError:
        return None
