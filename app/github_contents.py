import base64
import requests


GITHUB_API_URL = "https://api.github.com"


MAX_FILE_SIZE = 500_000


def get_headers(github_token=""):

    headers = {
        "Accept": "application/vnd.github+json"
    }

    if github_token:

        headers["Authorization"] = (
            f"Bearer {github_token}"
        )

    return headers


def get_file_content(
    owner,
    repository,
    file_path,
    branch,
    github_token=""
):
    """
    Download a text file from GitHub.
    """

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repository}/contents/"
        f"{file_path}"
    )

    params = {
        "ref": branch
    }

    try:

        response = requests.get(
            url,
            headers=get_headers(github_token),
            params=params,
            timeout=15
        )

        if response.status_code != 200:

            return {
                "success": False,
                "error": (
                    f"GitHub returned "
                    f"{response.status_code}"
                )
            }

        data = response.json()


        # GitHub can return a directory instead
        # of a file.

        if data.get("type") != "file":

            return {
                "success": False,
                "error": "Path is not a file."
            }


        # Avoid downloading very large files.

        file_size = data.get(
            "size",
            0
        )

        if file_size > MAX_FILE_SIZE:

            return {
                "success": False,
                "error": (
                    "File is too large "
                    "to analyze."
                ),
                "skipped": True
            }


        encoded_content = data.get(
            "content",
            ""
        )


        # GitHub sometimes inserts newlines
        # into Base64 content.

        encoded_content = (
            encoded_content
            .replace("\n", "")
        )


        try:

            decoded_content = base64.b64decode(
                encoded_content
            )

            content = decoded_content.decode(
                "utf-8",
                errors="replace"
            )

        except Exception as error:

            return {
                "success": False,
                "error": (
                    f"Unable to decode file: "
                    f"{error}"
                )
            }


        return {
            "success": True,
            "path": file_path,
            "size": file_size,
            "content": content
        }


    except requests.exceptions.Timeout:

        return {
            "success": False,
            "error": "GitHub request timed out."
        }


    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "error": (
                f"Unable to connect to GitHub: "
                f"{error}"
            )
        }