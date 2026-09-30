from app.github_contents import get_file_content

from app.analyzers.code_quality import (
    analyze_python_code,
    calculate_basic_quality_score,
)


# ==========================================================
# DEVGUARD REPOSITORY QUALITY ANALYZER
# ==========================================================

MAX_PYTHON_FILES = 20


def analyze_repository_quality(
    owner,
    repository,
    branch,
    repository_files,
    github_token=""
):
    """
    Analyze Python source files in a GitHub repository.

    Includes:
    - Line metrics
    - Comment metrics
    - Function metrics
    - Documentation metrics
    - Long-line detection
    - Long-function detection
    - Syntax errors
    - Complexity analysis
    - High-complexity function detection
    - DevGuard heuristic quality score
    """

    # ======================================================
    # FIND PYTHON FILES
    # ======================================================

    python_files = [
        file_path
        for file_path in repository_files
        if file_path.lower().endswith(".py")
    ]

    # Limit analysis to avoid excessive GitHub API requests
    python_files = python_files[:MAX_PYTHON_FILES]

    file_results = []

    skipped_files = []

    # ======================================================
    # ANALYZE EACH PYTHON FILE
    # ======================================================

    for file_path in python_files:

        try:

            response = get_file_content(
                owner=owner,
                repository=repository,
                file_path=file_path,
                branch=branch,
                github_token=github_token,
            )

            if not response.get("success"):

                skipped_files.append({
                    "file_path": file_path,
                    "reason": response.get(
                        "error",
                        "Unable to retrieve file"
                    ),
                })

                continue

            source_code = response.get(
                "content",
                ""
            )

            result = analyze_python_code(
                file_path,
                source_code
            )

            file_results.append(result)

        except Exception as error:

            skipped_files.append({
                "file_path": file_path,
                "reason": str(error),
            })

    # ======================================================
    # BASIC COUNTERS
    # ======================================================

    files_analyzed = len(file_results)

    files_skipped = len(skipped_files)

    total_lines = sum(
        result.get("total_lines", 0)
        for result in file_results
    )

    total_blank_lines = sum(
        result.get("blank_lines", 0)
        for result in file_results
    )

    total_comment_lines = sum(
        result.get("comment_lines", 0)
        for result in file_results
    )

    total_functions = sum(
        result.get("total_functions", 0)
        for result in file_results
    )

    documented_functions = sum(
        result.get("documented_functions", 0)
        for result in file_results
    )

    undocumented_functions = sum(
        result.get("undocumented_functions", 0)
        for result in file_results
    )

    total_long_lines = sum(
        result.get("long_line_count", 0)
        for result in file_results
    )

    total_syntax_errors = sum(
        result.get("syntax_error_count", 0)
        for result in file_results
    )

    total_classes = sum(
        result.get("class_count", 0)
        for result in file_results
    )

    # ======================================================
    # FUNCTION LENGTH
    # ======================================================

    all_functions = []

    for result in file_results:

        for function in result.get(
            "functions",
            []
        ):

            function_copy = dict(function)

            function_copy["file_path"] = result.get(
                "file_path",
                "unknown"
            )

            all_functions.append(
                function_copy
            )

    # ======================================================
    # LONG FUNCTIONS
    # ======================================================

    long_functions = []

    for function in all_functions:

        if function.get("line_count", 0) > 50:

            long_functions.append(function)

    # ======================================================
    # COMPLEXITY ANALYSIS
    # ======================================================

    total_complexity = sum(
        function.get("complexity", 0)
        for function in all_functions
    )

    if total_functions > 0:

        average_complexity = round(
            total_complexity / total_functions,
            2
        )

        average_function_length = round(
            sum(
                function.get(
                    "line_count",
                    0
                )
                for function in all_functions
            )
            / total_functions,
            1
        )

    else:

        average_complexity = 0

        average_function_length = 0

    # ======================================================
    # HIGH COMPLEXITY FUNCTIONS
    # ======================================================

    high_complexity_functions = [
        function
        for function in all_functions
        if function.get(
            "high_complexity",
            False
        )
    ]

    # ======================================================
    # DOCUMENTATION RATIO
    # ======================================================

    if total_functions > 0:

        documentation_ratio = round(
            (
                documented_functions
                / total_functions
            ) * 100,
            2
        )

    else:

        documentation_ratio = 0

    # ======================================================
    # COMMENT RATIO
    # ======================================================

    if total_lines > 0:

        comment_ratio = round(
            (
                total_comment_lines
                / total_lines
            ) * 100,
            2
        )

        blank_line_ratio = round(
            (
                total_blank_lines
                / total_lines
            ) * 100,
            2
        )

    else:

        comment_ratio = 0

        blank_line_ratio = 0

    # ======================================================
    # QUALITY SCORE
    # ======================================================

    quality_score = calculate_basic_quality_score(
        file_results
    )

    # ======================================================
    # RETURN COMPLETE RESULT
    # ======================================================

    return {

        # --------------------------------------------------
        # File information
        # --------------------------------------------------

        "files_analyzed": files_analyzed,

        "files_skipped": files_skipped,

        "skipped_files": skipped_files,

        # --------------------------------------------------
        # Line metrics
        # --------------------------------------------------

        "total_lines": total_lines,

        "total_blank_lines": total_blank_lines,

        "blank_line_ratio": blank_line_ratio,

        "total_comment_lines": total_comment_lines,

        "comment_ratio": comment_ratio,

        # --------------------------------------------------
        # Function metrics
        # --------------------------------------------------

        "total_functions": total_functions,

        "documented_functions": documented_functions,

        "undocumented_functions": undocumented_functions,

        "documentation_ratio": documentation_ratio,

        "average_function_length": average_function_length,

        # --------------------------------------------------
        # Long-line metrics
        # --------------------------------------------------

        "long_line_count": total_long_lines,

        # --------------------------------------------------
        # Long-function metrics
        # --------------------------------------------------

        "long_functions": long_functions,

        "long_function_count": len(
            long_functions
        ),

        # --------------------------------------------------
        # Class metrics
        # --------------------------------------------------

        "total_classes": total_classes,

        # --------------------------------------------------
        # Syntax metrics
        # --------------------------------------------------

        "syntax_error_count": total_syntax_errors,

        # --------------------------------------------------
        # Complexity metrics
        # --------------------------------------------------

        "total_complexity": total_complexity,

        "average_complexity": average_complexity,

        "high_complexity_functions": (
            high_complexity_functions
        ),

        "high_complexity_count": len(
            high_complexity_functions
        ),

        # --------------------------------------------------
        # Quality score
        # --------------------------------------------------

        "quality_score": quality_score,

        # --------------------------------------------------
        # Individual file results
        # --------------------------------------------------

        "file_results": file_results,
    }