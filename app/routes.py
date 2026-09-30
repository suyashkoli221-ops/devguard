from flask import Blueprint, render_template, request, jsonify

from app.github_api import get_repository_info
from app.repository_scanner import scan_repository
from app.analyzers.repository_quality import analyze_repository_quality
from app.analyzers.repository_security import analyze_repository_security
from app.analyzers.project_health import analyze_project_health
from app.analyzers.overall_report import analyze_overall_repository
from app.github_contents import get_file_content
from app.database.history import (
    init_history_database,
    save_scan_history,
    get_scan_history,
    get_scan_by_id,
    delete_scan_history,
    clear_scan_history
)
from config import Config


main = Blueprint("main", __name__)


# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

init_history_database()


# ==========================================================
# HOME PAGE
# ==========================================================

@main.route("/")
def index():
    return render_template("index.html")


# ==========================================================
# ANALYZE REPOSITORY
# ==========================================================

@main.route("/api/analyze", methods=["POST"])
def analyze_repository():

    try:

        # ==================================================
        # GET REQUEST DATA
        # ==================================================

        data = request.get_json(silent=True) or {}

        repository_url = data.get(
            "repository_url",
            ""
        ).strip()

        if not repository_url:

            return jsonify({
                "success": False,
                "error": "GitHub repository URL is required."
            }), 400

        # ==================================================
        # REPOSITORY INFORMATION
        # ==================================================

        repository_info = get_repository_info(
            repository_url,
            Config.GITHUB_TOKEN
        )

        if not repository_info.get("success"):

            return jsonify({
                "success": False,
                "error": repository_info.get(
                    "error",
                    "Unable to retrieve repository information."
                )
            }), 400

        full_name = repository_info.get(
            "full_name",
            ""
        )

        parts = full_name.split("/")

        if len(parts) != 2:

            return jsonify({
                "success": False,
                "error": "Invalid repository information."
            }), 400

        owner = parts[0]

        repository_name = parts[1]

        branch = repository_info.get(
            "default_branch",
            "main"
        )

        # ==================================================
        # REPOSITORY SCANNER
        # ==================================================

        scan_result = scan_repository(
            owner,
            repository_name,
            branch,
            Config.GITHUB_TOKEN
        )

        if not scan_result.get("success"):

            return jsonify({
                "success": False,
                "error": scan_result.get(
                    "error",
                    "Repository scan failed."
                )
            }), 400

        repository_files = scan_result.get(
            "files",
            []
        )

        # ==================================================
        # CODE QUALITY
        # ==================================================

        quality_result = analyze_repository_quality(
            owner,
            repository_name,
            branch,
            repository_files,
            Config.GITHUB_TOKEN
        )

        # ==================================================
        # SOURCE LOADER
        # ==================================================

        def source_loader(file_path):

            result = get_file_content(
                owner,
                repository_name,
                file_path,
                branch,
                Config.GITHUB_TOKEN
            )

            if not result.get("success"):

                return None

            return result.get(
                "content",
                ""
            )

        # ==================================================
        # SECURITY
        # ==================================================

        security_result = analyze_repository_security(
            repository_files,
            source_loader
        )

        # ==================================================
        # PROJECT HEALTH
        # ==================================================

        project_health_result = analyze_project_health(
            repository_files,
            source_loader
        )

        # ==================================================
        # OVERALL REPORT
        # ==================================================

        overall_report = analyze_overall_repository(
            quality_result,
            security_result,
            project_health_result
        )

        # ==================================================
        # SAVE SCAN HISTORY
        # ==================================================

        component_scores = (
            overall_report.get(
                "component_scores",
                {}
            )
        )

        scan_id = save_scan_history(

            repository_name=full_name,

            repository_url=repository_url,

            overall_score=overall_report.get(
                "overall_score",
                0
            ),

            overall_status=overall_report.get(
                "status",
                "Unknown"
            ),

            code_quality_score=component_scores.get(
                "code_quality",
                0
            ),

            security_score=component_scores.get(
                "security",
                0
            ),

            project_health_score=component_scores.get(
                "project_health",
                0
            )
        )

        # Add scan ID to the report

        overall_report["scan_id"] = scan_id

        # ==================================================
        # FINAL RESPONSE
        # ==================================================

        return jsonify({

            "success": True,

            "repository": repository_info,

            "scan": scan_result,

            "quality": quality_result,

            "security": security_result,

            "project_health": project_health_result,

            "overall_report": overall_report

        })

    except Exception as error:

        print(
            "Repository analysis error:",
            error
        )

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# ==========================================================
# GET SCAN HISTORY
# ==========================================================

@main.route("/api/history", methods=["GET"])
def history():

    try:

        history_records = get_scan_history(
            limit=20
        )

        return jsonify({

            "success": True,

            "count": len(
                history_records
            ),

            "history": history_records

        })

    except Exception as error:

        print(
            "History error:",
            error
        )

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# ==========================================================
# GET SINGLE SCAN
# ==========================================================

@main.route(
    "/api/history/<int:scan_id>",
    methods=["GET"]
)
def single_history(scan_id):

    try:

        record = get_scan_by_id(
            scan_id
        )

        if record is None:

            return jsonify({

                "success": False,

                "error": "Scan history record not found."

            }), 404

        return jsonify({

            "success": True,

            "scan": record

        })

    except Exception as error:

        print(
            "Single history error:",
            error
        )

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# ==========================================================
# DELETE SINGLE SCAN
# ==========================================================

@main.route(
    "/api/history/<int:scan_id>",
    methods=["DELETE"]
)
def delete_history(scan_id):

    try:

        deleted = delete_scan_history(
            scan_id
        )

        if not deleted:

            return jsonify({

                "success": False,

                "error": "Scan history record not found."

            }), 404

        return jsonify({

            "success": True,

            "message": "Scan history deleted successfully."

        })

    except Exception as error:

        print(
            "Delete history error:",
            error
        )

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# ==========================================================
# CLEAR ALL HISTORY
# ==========================================================

@main.route(
    "/api/history",
    methods=["DELETE"]
)
def clear_history():

    try:

        deleted_count = clear_scan_history()

        return jsonify({

            "success": True,

            "deleted_count": deleted_count,

            "message": "Scan history cleared successfully."

        })

    except Exception as error:

        print(
            "Clear history error:",
            error
        )

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500