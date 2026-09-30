import os


# ============================================================
# PROJECT HEALTH CONFIGURATION
# ============================================================

DEPENDENCY_FILES = {
    "requirements.txt": "Python",
    "package.json": "Node.js",
    "package-lock.json": "Node.js",
    "yarn.lock": "Node.js",
    "pnpm-lock.yaml": "Node.js",
    "pom.xml": "Java",
    "build.gradle": "Java",
    "build.gradle.kts": "Java",
    "Gemfile": "Ruby",
    "go.mod": "Go",
    "Cargo.toml": "Rust",
}


IMPORTANT_PROJECT_FILES = [
    "README.md",
    "README",
    ".gitignore",
    "LICENSE",
]


TEST_FILE_PATTERNS = [
    "test_",
    "_test.",
    "tests/",
    "test/",
]


TODO_PATTERNS = [
    "TODO",
    "FIXME",
    "HACK",
    "XXX",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_path(file_path):
    """
    Normalize repository file paths.
    """

    return file_path.replace("\\", "/").strip()


def get_file_name(file_path):
    """
    Return the file name from a repository path.
    """

    normalized = normalize_path(file_path)

    return normalized.split("/")[-1]


def detect_dependency_files(repository_files):
    """
    Detect dependency and package-management files.
    """

    detected = []

    for file_path in repository_files:

        file_name = get_file_name(file_path)

        if file_name in DEPENDENCY_FILES:

            detected.append({
                "file": file_path,
                "ecosystem": DEPENDENCY_FILES[file_name]
            })

    return detected


def detect_important_files(repository_files):
    """
    Detect important project documentation/configuration files.
    """

    detected = []

    normalized_files = {
        normalize_path(file_path).lower(): file_path
        for file_path in repository_files
    }

    for important_file in IMPORTANT_PROJECT_FILES:

        key = important_file.lower()

        if key in normalized_files:

            detected.append(
                normalized_files[key]
            )

    return detected


def detect_test_files(repository_files):
    """
    Detect likely test files.
    """

    test_files = []

    for file_path in repository_files:

        normalized = normalize_path(
            file_path
        ).lower()

        file_name = get_file_name(
            file_path
        ).lower()

        is_test = False

        for pattern in TEST_FILE_PATTERNS:

            if (
                pattern in normalized
                or pattern in file_name
            ):

                is_test = True
                break

        if is_test:

            test_files.append(file_path)

    return test_files


def count_todo_markers(
    repository_files,
    source_loader
):
    """
    Count TODO/FIXME/HACK/XXX markers in source files.
    """

    total = 0

    details = []

    supported_extensions = (
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".php",
        ".rb",
        ".go",
        ".rs",
        ".cs",
        ".html",
        ".css"
    )

    for file_path in repository_files:

        if not file_path.lower().endswith(
            supported_extensions
        ):
            continue

        try:

            source_code = source_loader(
                file_path
            )

            if source_code is None:
                continue

            for line_number, line in enumerate(
                source_code.splitlines(),
                start=1
            ):

                upper_line = line.upper()

                for marker in TODO_PATTERNS:

                    if marker in upper_line:

                        total += 1

                        details.append({
                            "file": file_path,
                            "line": line_number,
                            "marker": marker,
                            "text": line.strip()
                        })

        except Exception:
            continue

    return {
        "count": total,
        "details": details
    }


# ============================================================
# PROJECT HEALTH ANALYSIS
# ============================================================

def analyze_project_health(
    repository_files,
    source_loader
):
    """
    Analyze basic project structure and health.
    """

    normalized_files = [
        normalize_path(file_path)
        for file_path in repository_files
    ]


    # --------------------------------------------------------
    # Dependency files
    # --------------------------------------------------------

    dependency_files = detect_dependency_files(
        normalized_files
    )


    # --------------------------------------------------------
    # Important files
    # --------------------------------------------------------

    important_files = detect_important_files(
        normalized_files
    )


    # --------------------------------------------------------
    # Test files
    # --------------------------------------------------------

    test_files = detect_test_files(
        normalized_files
    )


    # --------------------------------------------------------
    # TODO / FIXME markers
    # --------------------------------------------------------

    todo_result = count_todo_markers(
        normalized_files,
        source_loader
    )


    # --------------------------------------------------------
    # README detection
    # --------------------------------------------------------

    has_readme = any(
        get_file_name(file_path).lower()
        in ("readme.md", "readme")
        for file_path in normalized_files
    )


    # --------------------------------------------------------
    # Gitignore detection
    # --------------------------------------------------------

    has_gitignore = any(
        get_file_name(file_path).lower()
        == ".gitignore"
        for file_path in normalized_files
    )


    # --------------------------------------------------------
    # License detection
    # --------------------------------------------------------

    has_license = any(
        get_file_name(file_path).lower()
        in (
            "license",
            "license.md",
            "license.txt"
        )
        for file_path in normalized_files
    )


    # --------------------------------------------------------
    # Dependency ecosystem summary
    # --------------------------------------------------------

    ecosystems = sorted(
        {
            item["ecosystem"]
            for item in dependency_files
        }
    )


    # --------------------------------------------------------
    # Basic health indicators
    # --------------------------------------------------------

    health_indicators = {
        "readme_present": has_readme,
        "gitignore_present": has_gitignore,
        "license_present": has_license,
        "dependency_file_present": (
            len(dependency_files) > 0
        ),
        "tests_present": (
            len(test_files) > 0
        )
    }


    health_score = 100


    if not has_readme:
        health_score -= 20

    if not has_gitignore:
        health_score -= 10

    if not has_license:
        health_score -= 5

    if not dependency_files:
        health_score -= 10

    if not test_files:
        health_score -= 15


    health_score = max(
        0,
        min(100, health_score)
    )


    # --------------------------------------------------------
    # Health status
    # --------------------------------------------------------

    if health_score >= 80:

        health_status = "Healthy"

    elif health_score >= 60:

        health_status = "Needs Improvement"

    else:

        health_status = "Needs Attention"


    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {
        "success": True,

        "health_score": health_score,

        "health_status": health_status,

        "total_files": len(normalized_files),

        "dependency_files": dependency_files,

        "dependency_file_count": len(
            dependency_files
        ),

        "ecosystems": ecosystems,

        "important_files": important_files,

        "important_file_count": len(
            important_files
        ),

        "test_files": test_files,

        "test_file_count": len(
            test_files
        ),

        "todo_count": todo_result["count"],

        "todo_details": todo_result["details"],

        "has_readme": has_readme,

        "has_gitignore": has_gitignore,

        "has_license": has_license,

        "health_indicators": health_indicators
    }