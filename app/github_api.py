import requests
from urllib.parse import urlparse


GITHUB_API_URL = "https://api.github.com"


def parse_github_url(repo_url):
    """
    Extract owner and repository name from a GitHub URL.
    """

    try:
        parsed = urlparse(repo_url.strip())

        if parsed.netloc.lower() not in ["github.com", "www.github.com"]:
            return None, None

        parts = [
            part for part in parsed.path.strip("/").split("/")
            if part
        ]

        if len(parts) < 2:
            return None, None

        owner = parts[0]
        repository = parts[1]

        # Remove .git if the user enters a Git URL
        if repository.endswith(".git"):
            repository = repository[:-4]

        return owner, repository

    except Exception:
        return None, None


def get_repository_info(repo_url, github_token=""):
    """
    Fetch repository information from GitHub API.
    """

    owner, repository = parse_github_url(repo_url)

    if not owner or not repository:
        return {
            "success": False,
            "error": "Invalid GitHub repository URL."
        }

    url = f"{GITHUB_API_URL}/repos/{owner}/{repository}"

    headers = {
        "Accept": "application/vnd.github+json"
    }

    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code == 404:
            return {
                "success": False,
                "error": "Repository not found or is private."
            }

        if response.status_code == 403:
            return {
                "success": False,
                "error": "GitHub API rate limit reached."
            }

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"GitHub API returned status {response.status_code}."
            }

        data = response.json()

        license_info = data.get("license")

        repository_info = {
            "success": True,
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "owner": data.get("owner", {}).get("login"),
            "description": data.get("description"),
            "html_url": data.get("html_url"),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "language": data.get("language"),
            "size_kb": data.get("size", 0),
            "default_branch": data.get("default_branch"),
            "visibility": data.get("visibility"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "license": (
                license_info.get("spdx_id")
                if license_info
                else None
            ),
            "is_fork": data.get("fork", False),
            "archived": data.get("archived", False)
        }

        return repository_info

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "GitHub request timed out."
        }

    except requests.exceptions.RequestException as error:
        return {
            "success": False,
            "error": f"Unable to connect to GitHub: {error}"
        }