import os
import sys
import subprocess
import datetime


def _print(*args, **kwargs):
    # small wrapper so all messages show consistently
    print("[autoupdate]", *args, **kwargs)


def run_autoupdate() -> bool:
    # allow opt-out
    if os.environ.get("DASHR_NO_AUTOUPDATE"):
        _print("Autoupdate disabled via DASHR_NO_AUTOUPDATE")
        return False

    install_dir = os.environ.get("DASHR_INSTALL_DIR", os.path.expanduser("~/dashr"))
    user_data_dir = os.environ.get(
        "DASHR_USER_DATA_DIR", os.path.expanduser("~/dashr-data")
    )

    # Determine repository root (three levels up from this file: client/src/update)
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )

    # Only auto-update when running from the installation directory to avoid
    # updating a developer checkout unintentionally.
    if os.path.abspath(repo_root) != os.path.abspath(install_dir):
        _print(
            f"Autoupdate skipped: running from {repo_root} (not install dir {install_dir})"
        )
        return False

    if not os.path.isdir(install_dir):
        _print(f"Autoupdate skipped: install directory does not exist: {install_dir}")
        return False

    git_dir = os.path.join(install_dir, ".git")
    if not os.path.isdir(git_dir):
        _print("Autoupdate skipped: installation is not a git repository")
        return False

    try:
        _print(f"Checking for updates in {install_dir}...")

        # Stash local changes if present
        status = subprocess.run(
            ["git", "-C", install_dir, "status", "--porcelain"],
            capture_output=True,
            text=True,
        )
        if status.stdout.strip():
            _print("Stashing local changes...")
            subprocess.run(
                [
                    "git",
                    "-C",
                    install_dir,
                    "stash",
                    "push",
                    "-m",
                    f"Auto-stash before update on {datetime.datetime.utcnow().isoformat()}",
                ],
                check=True,
            )
        else:
            _print("No local changes to stash.")

        # Ensure on main
        subprocess.run(["git", "-C", install_dir, "checkout", "main"], check=True)

        # Fetch
        _print("Fetching latest updates from repository...")
        subprocess.run(["git", "-C", install_dir, "fetch", "origin"], check=True)

        # Compare local and remote
        local = subprocess.run(
            ["git", "-C", install_dir, "rev-parse", "@"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        try:
            remote = subprocess.run(
                ["git", "-C", install_dir, "rev-parse", "@{u}"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        except subprocess.CalledProcessError:
            # fallback to origin/main if upstream not set
            remote = subprocess.run(
                ["git", "-C", install_dir, "rev-parse", "origin/main"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()

        if local == remote:
            _print("Dashr is already up to date!")
            _print(f"User data is stored at: {user_data_dir}")
            return False

        _print("Updates available. Updating...")
        subprocess.run(["git", "-C", install_dir, "pull", "origin", "main"], check=True)

        # Update Python dependencies if virtualenv exists
        venv_dir = os.path.join(install_dir, "venv")
        requirements = os.path.join(install_dir, "client", "src", "requirements.txt")
        if os.path.isdir(venv_dir):
            python_bin = os.path.join(venv_dir, "bin", "python")
            if os.path.isfile(python_bin):
                _print("Updating Python dependencies in virtualenv...")
                # try to upgrade pip and then requirements
                subprocess.run(
                    [python_bin, "-m", "pip", "install", "--upgrade", "pip"],
                    check=False,
                )
                if os.path.isfile(requirements):
                    subprocess.run(
                        [
                            python_bin,
                            "-m",
                            "pip",
                            "install",
                            "-r",
                            requirements,
                            "--upgrade",
                        ],
                        check=False,
                    )
                    _print("Dependencies updated.")
                else:
                    _print("No requirements.txt found. Skipping dependency update.")
            else:
                _print(
                    "Warning: python executable not found in venv. Skipping dependency update."
                )
        else:
            _print(
                "Warning: Virtual environment not found. Dependencies may need manual update."
            )
            if os.path.isfile(requirements):
                _print("You can manually update dependencies with:")
                _print(f"python3 -m pip install -r {requirements} --upgrade")

        # Update desktop file on Linux
        if sys.platform.startswith("linux"):
            desktop_file_dest = os.path.expanduser(
                "~/.local/share/applications/dashr.desktop"
            )
            desktop_source = os.path.join(
                install_dir, "client", "scripts", "resources", "dashr.desktop"
            )
            if os.path.isfile(desktop_source):
                with open(desktop_source, "r") as f:
                    content = f.read()
                resolved = content.replace("__INSTALL_DIR__", install_dir)
                os.makedirs(os.path.dirname(desktop_file_dest), exist_ok=True)
                need_update = True
                if os.path.isfile(desktop_file_dest):
                    with open(desktop_file_dest, "r") as f:
                        existing = f.read()
                    if existing == resolved:
                        need_update = False
                if need_update:
                    with open(desktop_file_dest, "w") as f:
                        f.write(resolved)
                    try:
                        os.chmod(desktop_file_dest, 0o755)
                    except Exception:
                        pass
                    try:
                        subprocess.run(
                            [
                                "update-desktop-database",
                                os.path.dirname(desktop_file_dest),
                            ],
                            check=False,
                        )
                    except Exception:
                        pass
                    _print(
                        f"Desktop file updated at {desktop_file_dest} with paths resolved"
                    )
                else:
                    _print("Desktop file is already up to date")
            else:
                _print(f"Warning: Desktop file not found at {desktop_source}")

        _print("")
        _print("Dashr has been successfully updated!")
        _print(
            "You may need to restart the application for code changes to take effect."
        )

        return True

    except subprocess.CalledProcessError as e:
        _print(f"Update failed: {e}")
        return False

    except Exception as e:
        _print(f"Unexpected error during autoupdate: {e}")
        return False
