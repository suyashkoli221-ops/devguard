import requests


GITHUB_API_URL = "https://api.github.com"


# File extensions we want to analyze
CODE_EXTENSIONS = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "React JSX",
    ".ts": "TypeScript",
    ".tsx": "React TSX",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sql": "SQL",
}


TEST_FILE_PATTERNS = [
    "test_",
    "_test.",
    ".test.",
    ".spec.",
    "tests/",
    "test/",
    "__tests__/",
]


IMPORTANT_FILES = [
    "README.md",
    "README",
    "LICENSE",
    "LICENSE.md",
    ".gitignore",
    "requirements.txt",
    "package.json",
    "pyproject.toml",
    "setup.py",
    "Dockerfile",
    "docker-compose.yml",
]


def get_headers(github_token=""):
    """
    Create headers for GitHub API requests.
    """

    headers = {
        "Accept": "application/vnd.github+json"
    }

    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    return headers


def get_repository_tree(
    owner,
    repository,
    branch,
    github_token=""
):
    """
    Get the complete file tree of a GitHub repository.
    """

    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repository}/git/trees/"
        f"{branch}?recursive=1"
    )

    try:

        response = requests.get(
            url,
            headers=get_headers(github_token),
            timeout=15
        )

        if response.status_code != 200:

            return {
                "success": False,
                "error": (
                    f"Unable to retrieve repository tree. "
                    f"GitHub returned {response.status_code}."
                )
            }

        data = response.json()

        if data.get("truncated"):

            warning = (
                "GitHub returned a truncated file tree. "
                "Very large repositories may not be fully analyzed."
            )

        else:

            warning = None

        return {
            "success": True,
            "tree": data.get("tree", []),
            "truncated": data.get("truncated", False),
            "warning": warning
        }

    except requests.exceptions.Timeout:

        return {
            "success": False,
            "error": "Repository scan timed out."
        }

    except requests.exceptions.RequestException as error:

        return {
            "success": False,
            "error": f"Unable to connect to GitHub: {error}"
        }


def is_test_file(path):
    """
    Determine whether a file appears to be a test file.
    """

    path_lower = path.lower()

    filename = path_lower.split("/")[-1]

    if filename.startswith("test_"):
        return True

    if "_test." in filename:
        return True

    if ".test." in filename:
        return True

    if ".spec." in filename:
        return True

    directory_parts = path_lower.split("/")

    for directory in [
        "test",
        "tests",
        "__tests__"
    ]:

        if directory in directory_parts:
            return True

    return False


def get_file_extension(path):
    """
    Return the file extension.
    """

    filename = path.split("/")[-1]

    if "." not in filename:
        return ""

    return "." + filename.rsplit(".", 1)[1].lower()


def analyze_repository_tree(tree):
    """
    Analyze repository files and directories.
    """

    files = []
    directories = []

    for item in tree:

        path = item.get("path", "")
        item_type = item.get("type")

        if item_type == "tree":

            directories.append(path)

        elif item_type == "blob":

            files.append(path)


    language_counts = {}

    test_files = []

    for file_path in files:

        extension = get_file_extension(file_path)

        if extension in CODE_EXTENSIONS:

            language = CODE_EXTENSIONS[extension]

            language_counts[language] = (
                language_counts.get(language, 0) + 1
            )

        if is_test_file(file_path):

            test_files.append(file_path)


    important_files_found = []

    file_names_lower = {
        file_path.lower()
        for file_path in files
    }


    for important_file in IMPORTANT_FILES:

        if important_file.lower() in file_names_lower:

            important_files_found.append(
                important_file
            )


    return {
        "total_files": len(files),

        "total_directories": len(directories),

        "files": files,

        "directories": directories,

        "language_counts": language_counts,

        "test_files": test_files,

        "test_file_count": len(test_files),

        "important_files": important_files_found,

        "important_file_count": len(
            important_files_found
        )
    }


def scan_repository(
    owner,
    repository,
    branch,
    github_token=""
):
    """
    Scan the complete repository structure.
    """

    tree_result = get_repository_tree(
        owner,
        repository,
        branch,
        github_token
    )

    if not tree_result["success"]:

        return tree_result


    analysis = analyze_repository_tree(
        tree_result["tree"]
    )


    analysis["success"] = True

    analysis["truncated"] = (
        tree_result["truncated"]
    )

    analysis["warning"] = (
        tree_result["warning"]
    )

    return analysis