import re


# ============================================================
# SECURITY ANALYZER CONFIGURATION
# ============================================================

SECRET_PATTERNS = [
    (
        "api_key",
        re.compile(
            r"(?i)\b(api[_-]?key)\s*[:=]\s*['\"][^'\"]{12,}['\"]"
        ),
        "Possible hardcoded API key."
    ),
    (
        "secret_key",
        re.compile(
            r"(?i)\b(secret[_-]?key)\s*[:=]\s*['\"][^'\"]{12,}['\"]"
        ),
        "Possible hardcoded secret key."
    ),
    (
        "password",
        re.compile(
            r"(?i)\b(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
        ),
        "Possible hardcoded password."
    ),
    (
        "access_token",
        re.compile(
            r"(?i)\b(access[_-]?token|auth[_-]?token)\s*[:=]\s*['\"][^'\"]{12,}['\"]"
        ),
        "Possible hardcoded access token."
    ),
]


# ============================================================
# DANGEROUS FUNCTIONS
# ============================================================

DANGEROUS_FUNCTION_PATTERNS = [
    (
        "eval",
        re.compile(r"\beval\s*\("),
        "Use of eval()"
    ),
    (
        "exec",
        re.compile(r"\bexec\s*\("),
        "Use of exec()"
    ),
    (
        "os_system",
        re.compile(r"\bos\.system\s*\("),
        "Use of os.system()"
    ),
    (
        "shell_true",
        re.compile(r"\bshell\s*=\s*True\b"),
        "subprocess shell=True"
    ),
]


# ============================================================
# SUSPICIOUS CONFIGURATION PATTERNS
# ============================================================

SUSPICIOUS_PATTERNS = [
    (
        "debug_mode",
        re.compile(
            r"\bdebug\s*=\s*True\b",
            re.IGNORECASE
        ),
        "Debug mode enabled",
        "medium"
    ),
]


# ============================================================
# SQL INJECTION PATTERNS
# ============================================================

SQL_PATTERNS = [
    (
        "sql_string_format",
        re.compile(
            r"""(?i)(SELECT|INSERT|UPDATE|DELETE)\b.*(%s|\+.*\+|\.format\s*\(|f['"])"""
        ),
        "Possible SQL query built using string interpolation.",
        "medium"
    ),
]


# ============================================================
# URL DETECTION
# ============================================================

# IMPORTANT:
# Only detect insecure HTTP URLs.
#
# `https://` is intentionally NOT matched.
#
# This prevents legitimate HTTPS URLs such as:
# https://www.google.com
# from being reported as security findings.

HTTP_URL_PATTERN = re.compile(
    r"""http://[^\s'"]+""",
    re.IGNORECASE
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_test_file(file_path):
    """
    Determine whether a file is likely a test file.
    """

    normalized = file_path.lower().replace("\\", "/")

    file_name = normalized.split("/")[-1]

    return (
        normalized.startswith("tests/")
        or normalized.startswith("test/")
        or file_name.startswith("test_")
        or file_name.endswith("_test.py")
    )


def is_example_url(url):
    """
    Determine whether a URL is clearly an example,
    local development URL, or test URL.
    """

    url_lower = url.lower()

    ignored_hosts = [
        "example.com",
        "example.org",
        "example.net",
        "localhost",
        "127.0.0.1",
        "0.0.0.0"
    ]

    for host in ignored_hosts:

        if host in url_lower:
            return True

    return False


def is_likely_frontend_data_url(
    file_path,
    line
):
    """
    Determine whether an HTTP URL in frontend code is
    likely being used as application or example data
    rather than as a security-sensitive endpoint.
    """

    normalized = file_path.lower().replace(
        "\\",
        "/"
    )

    frontend_extensions = (
        ".html",
        ".css",
        ".js",
        ".jsx",
        ".ts",
        ".tsx"
    )

    if not normalized.endswith(
        frontend_extensions
    ):
        return False


    data_indicators = [
        "url",
        "urls",
        "link",
        "href",
        "src",
        "image",
        "website",
        "websiteurl",
        "targeturl",
        "testurl",
        "sample",
        "example"
    ]


    line_lower = line.lower()


    for indicator in data_indicators:

        if indicator in line_lower:
            return True


    return False


def is_comment_line(line):
    """
    Detect obvious source-code comment lines.
    """

    stripped = line.strip()

    return (
        stripped.startswith("#")
        or stripped.startswith("//")
        or stripped.startswith("<!--")
        or stripped.startswith("*")
    )


def add_finding(
    findings,
    finding_type,
    severity,
    title,
    file_path,
    line_number,
    message
):
    """
    Add a standardized security finding.
    """

    findings.append({
        "type": finding_type,
        "severity": severity,
        "title": title,
        "file": file_path,
        "line": line_number,
        "message": message
    })


# ============================================================
# SOURCE CODE ANALYSIS
# ============================================================

def analyze_source_code(
    file_path,
    source_code
):

    findings = []

    if not source_code:

        return {
            "file": file_path,
            "findings": [],
            "finding_count": 0
        }


    test_file = is_test_file(
        file_path
    )

    lines = source_code.splitlines()


    for line_number, line in enumerate(
        lines,
        start=1
    ):

        # ----------------------------------------------------
        # Skip obvious comments
        # ----------------------------------------------------

        if is_comment_line(line):
            continue


        # ----------------------------------------------------
        # SECRET DETECTION
        # ----------------------------------------------------

        for (
            secret_type,
            pattern,
            message
        ) in SECRET_PATTERNS:

            if pattern.search(line):

                add_finding(
                    findings,
                    "hardcoded_secret",
                    "high",
                    (
                        "Possible hardcoded "
                        f"{secret_type.replace('_', ' ')}"
                    ),
                    file_path,
                    line_number,
                    message
                )


        # ----------------------------------------------------
        # DANGEROUS FUNCTIONS
        # ----------------------------------------------------

        for (
            dangerous_type,
            pattern,
            title
        ) in DANGEROUS_FUNCTION_PATTERNS:

            if pattern.search(line):

                severity = "medium"

                if dangerous_type in (
                    "eval",
                    "exec"
                ):
                    severity = "high"

                add_finding(
                    findings,
                    "dangerous_function",
                    severity,
                    title,
                    file_path,
                    line_number,
                    (
                        "A potentially dangerous function "
                        "or configuration was detected."
                    )
                )


        # ----------------------------------------------------
        # DEBUG MODE
        # ----------------------------------------------------

        for (
            pattern_type,
            pattern,
            title,
            severity
        ) in SUSPICIOUS_PATTERNS:

            if pattern.search(line):

                add_finding(
                    findings,
                    "suspicious_configuration",
                    severity,
                    title,
                    file_path,
                    line_number,
                    (
                        "Debug mode should normally be "
                        "disabled in production."
                    )
                )


        # ----------------------------------------------------
        # SQL INJECTION PATTERNS
        # ----------------------------------------------------

        for (
            sql_type,
            pattern,
            message,
            severity
        ) in SQL_PATTERNS:

            if pattern.search(line):

                add_finding(
                    findings,
                    "sql_injection_risk",
                    severity,
                    "Possible SQL injection risk",
                    file_path,
                    line_number,
                    message
                )


        # ----------------------------------------------------
        # HTTP URL ANALYSIS
        # ----------------------------------------------------

        # Test files are ignored because they commonly
        # contain URLs as test inputs.

        if not test_file:

            urls = HTTP_URL_PATTERN.findall(
                line
            )

            for url in urls:

                # Ignore known example/local URLs.
                if is_example_url(url):
                    continue


                # Ignore URLs that appear to be normal
                # frontend data or links.
                if is_likely_frontend_data_url(
                    file_path,
                    line
                ):
                    continue


                add_finding(
                    findings,
                    "suspicious_pattern",
                    "low",
                    "Hardcoded HTTP URL",
                    file_path,
                    line_number,
                    (
                        "An HTTP URL was found in source "
                        "code. HTTPS is recommended when "
                        "transmitting sensitive data."
                    )
                )


    return {
        "file": file_path,
        "findings": findings,
        "finding_count": len(findings)
    }


# ============================================================
# REPOSITORY SECURITY ANALYSIS
# ============================================================

def analyze_repository_security(
    repository_files,
    source_loader
):

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


    files_to_analyze = [
        file_path
        for file_path in repository_files
        if file_path.lower().endswith(
            supported_extensions
        )
    ]


    max_files = 50

    files_to_analyze = files_to_analyze[
        :max_files
    ]


    files_analyzed = 0
    files_skipped = 0

    all_findings = []
    file_results = []


    # ========================================================
    # ANALYZE FILES
    # ========================================================

    for file_path in files_to_analyze:

        try:

            source_code = source_loader(
                file_path
            )

            if source_code is None:

                files_skipped += 1

                continue


            result = analyze_source_code(
                file_path,
                source_code
            )


            file_results.append(
                result
            )


            all_findings.extend(
                result["findings"]
            )


            files_analyzed += 1


        except Exception:

            files_skipped += 1


    # ========================================================
    # SEVERITY COUNTS
    # ========================================================

    high_severity = sum(
        1
        for finding in all_findings
        if finding["severity"] == "high"
    )


    medium_severity = sum(
        1
        for finding in all_findings
        if finding["severity"] == "medium"
    )


    low_severity = sum(
        1
        for finding in all_findings
        if finding["severity"] == "low"
    )


    # ========================================================
    # SECURITY STATUS
    # ========================================================

    if high_severity > 0:

        security_status = "High Risk"

    elif medium_severity > 0:

        security_status = "Needs Review"

    elif low_severity > 0:

        security_status = "Low Risk"

    else:

        security_status = "No Issues Detected"


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "success": True,
        "files_analyzed": files_analyzed,
        "files_skipped": files_skipped,
        "total_findings": len(all_findings),
        "high_severity": high_severity,
        "medium_severity": medium_severity,
        "low_severity": low_severity,
        "security_status": security_status,
        "findings": all_findings,
        "file_results": file_results
    }