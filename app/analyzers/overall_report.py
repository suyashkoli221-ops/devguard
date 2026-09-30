# ==========================================================
# DEVGUARD - OVERALL REPOSITORY REPORT
# ==========================================================


def calculate_security_score(security_result):
    """
    Convert security findings into a 0-100 security score.

    This is a custom DevGuard heuristic and is not an
    industry-standard security score.
    """

    high = security_result.get("high_severity", 0)
    medium = security_result.get("medium_severity", 0)
    low = security_result.get("low_severity", 0)

    score = 100

    score -= high * 20
    score -= medium * 10
    score -= low * 3

    return max(0, min(100, score))


def calculate_overall_score(
    quality_result,
    security_result,
    health_result
):
    """
    Calculate the overall DevGuard repository score.

    Weighting:
        Code Quality   = 40%
        Security       = 30%
        Project Health = 30%

    This is a custom DevGuard scoring model.
    """

    quality_score = quality_result.get(
        "quality_score",
        0
    )

    security_score = calculate_security_score(
        security_result
    )

    health_score = health_result.get(
        "health_score",
        0
    )

    overall_score = (
        quality_score * 0.40
        + security_score * 0.30
        + health_score * 0.30
    )

    return round(overall_score, 2)


def determine_status(overall_score):
    """
    Determine the repository status.
    """

    if overall_score >= 85:
        return "Good"

    if overall_score >= 70:
        return "Needs Improvement"

    return "Needs Attention"


def generate_recommendations(
    quality_result,
    security_result,
    health_result
):
    """
    Generate actionable recommendations.
    """

    recommendations = []

    # ======================================================
    # SECURITY
    # ======================================================

    high_security = security_result.get(
        "high_severity",
        0
    )

    medium_security = security_result.get(
        "medium_severity",
        0
    )

    low_security = security_result.get(
        "low_severity",
        0
    )

    if high_security > 0:
        recommendations.append({
            "priority": "High",
            "category": "Security",
            "message": (
                "Address high-severity security findings "
                "before deploying the repository."
            )
        })

    if medium_security > 0:
        recommendations.append({
            "priority": "Medium",
            "category": "Security",
            "message": (
                "Review and fix medium-severity security "
                "findings."
            )
        })

    if low_security > 0:
        recommendations.append({
            "priority": "Low",
            "category": "Security",
            "message": (
                "Review low-severity security findings "
                "for potential improvements."
            )
        })

    # ======================================================
    # CODE QUALITY
    # ======================================================

    long_function_count = quality_result.get(
        "long_function_count",
        0
    )

    if long_function_count > 0:
        recommendations.append({
            "priority": "Medium",
            "category": "Code Quality",
            "message": (
                f"Consider breaking {long_function_count} "
                "long function(s) into smaller functions."
            )
        })

    high_complexity_count = quality_result.get(
        "high_complexity_count",
        0
    )

    if high_complexity_count > 0:
        recommendations.append({
            "priority": "Medium",
            "category": "Code Quality",
            "message": (
                f"Review {high_complexity_count} "
                "high-complexity function(s) to improve "
                "maintainability."
            )
        })

    syntax_error_count = quality_result.get(
        "syntax_error_count",
        0
    )

    if syntax_error_count > 0:
        recommendations.append({
            "priority": "High",
            "category": "Code Quality",
            "message": (
                f"Fix {syntax_error_count} syntax error(s) "
                "detected in the repository."
            )
        })

    documentation_ratio = quality_result.get(
        "documentation_ratio",
        0
    )

    if documentation_ratio < 20:
        recommendations.append({
            "priority": "Low",
            "category": "Documentation",
            "message": (
                "Consider adding documentation to more "
                "functions to improve code maintainability."
            )
        })

    # ======================================================
    # PROJECT HEALTH
    # ======================================================

    has_readme = health_result.get(
        "has_readme",
        False
    )

    if not has_readme:
        recommendations.append({
            "priority": "Medium",
            "category": "Project Health",
            "message": (
                "Add a README file describing the project, "
                "setup instructions, and usage."
            )
        })

    has_gitignore = health_result.get(
        "has_gitignore",
        False
    )

    if not has_gitignore:
        recommendations.append({
            "priority": "Medium",
            "category": "Project Health",
            "message": (
                "Add a .gitignore file to prevent unnecessary "
                "or sensitive files from being committed."
            )
        })

    has_license = health_result.get(
        "has_license",
        False
    )

    if not has_license:
        recommendations.append({
            "priority": "Low",
            "category": "Project Health",
            "message": (
                "Consider adding a LICENSE file to clearly "
                "define how the project can be used."
            )
        })

    dependency_file_count = health_result.get(
        "dependency_file_count",
        0
    )

    if dependency_file_count == 0:
        recommendations.append({
            "priority": "Low",
            "category": "Project Health",
            "message": (
                "No dependency file was detected. Consider "
                "adding one if the project uses external "
                "dependencies."
            )
        })

    test_file_count = health_result.get(
        "test_file_count",
        0
    )

    if test_file_count == 0:
        recommendations.append({
            "priority": "Medium",
            "category": "Testing",
            "message": (
                "No test files were detected. Consider adding "
                "automated tests."
            )
        })

    # ======================================================
    # TODO / FIXME
    # ======================================================

    todo_count = health_result.get(
        "todo_count",
        0
    )

    if todo_count > 0:
        recommendations.append({
            "priority": "Low",
            "category": "Maintenance",
            "message": (
                f"Review {todo_count} TODO/FIXME marker(s) "
                "found in the repository."
            )
        })

    return recommendations


def analyze_overall_repository(
    quality_result,
    security_result,
    health_result
):
    """
    Generate the final DevGuard repository report.
    """

    security_score = calculate_security_score(
        security_result
    )

    overall_score = calculate_overall_score(
        quality_result,
        security_result,
        health_result
    )

    status = determine_status(
        overall_score
    )

    recommendations = generate_recommendations(
        quality_result,
        security_result,
        health_result
    )

    return {
        "success": True,

        "overall_score": overall_score,

        "status": status,

        "component_scores": {
            "code_quality": quality_result.get(
                "quality_score",
                0
            ),
            "security": security_score,
            "project_health": health_result.get(
                "health_score",
                0
            )
        },

        "recommendation_count": len(
            recommendations
        ),

        "recommendations": recommendations
    }