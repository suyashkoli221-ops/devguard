"""
DevGuard Repository Security Analyzer

Connects the security analyzer with GitHub repository files.
"""

from app.analyzers.security_analyzer import analyze_source_code


# ============================================================
# CONFIGURATION
# ============================================================

MAX_FILES_TO_ANALYZE = 50

SUPPORTED_EXTENSIONS = {
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
    ".css",
}


# ============================================================
# FILE FILTER
# ============================================================

def is_supported_file(file_path):
    """
    Check whether a repository file should be analyzed.
    """

    file_path_lower = file_path.lower()

    return any(
        file_path_lower.endswith(extension)
        for extension in SUPPORTED_EXTENSIONS
    )


# ============================================================
# REPOSITORY SECURITY ANALYSIS
# ============================================================

def analyze_repository_security(
    repository_files,
    source_loader
):
    """
    Analyze supported source files in a repository.

    Parameters
    ----------
    repository_files:
        List of repository file paths.

    source_loader:
        Function that receives a file path and returns
        the source code.

    Returns
    -------
    dict
        Repository security analysis.
    """

    file_results = []
    all_findings = []

    files_analyzed = 0
    files_skipped = 0

    supported_files = [
        file_path
        for file_path in repository_files
        if is_supported_file(file_path)
    ]

    # Limit the number of files analyzed
    supported_files = supported_files[:MAX_FILES_TO_ANALYZE]

    for file_path in supported_files:

        try:

            source_code = source_loader(file_path)

            if source_code is None:
                files_skipped += 1
                continue

            result = analyze_source_code(
                file_path,
                source_code
            )

            file_results.append(result)

            all_findings.extend(
                result.get("findings", [])
            )

            files_analyzed += 1

        except Exception as error:

            files_skipped += 1

            file_results.append(
                {
                    "file": file_path,
                    "findings": [],
                    "finding_count": 0,
                    "error": str(error),
                }
            )


    # ========================================================
    # SEVERITY COUNTS
    # ========================================================

    high_severity = sum(
        1
        for finding in all_findings
        if finding.get("severity") == "high"
    )

    medium_severity = sum(
        1
        for finding in all_findings
        if finding.get("severity") == "medium"
    )

    low_severity = sum(
        1
        for finding in all_findings
        if finding.get("severity") == "low"
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
    # RESULT
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
        "file_results": file_results,
    }