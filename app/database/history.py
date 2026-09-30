# ==========================================================
# DEVGUARD - SCAN HISTORY DATABASE
# ==========================================================

import sqlite3
from pathlib import Path


# ==========================================================
# DATABASE CONFIGURATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_DIR = BASE_DIR / "database"

DATABASE_PATH = DATABASE_DIR / "devguard.db"


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_connection():
    """
    Create and return a SQLite database connection.
    """

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

def init_history_database():
    """
    Create the scan history table if it does not exist.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                repository_name TEXT NOT NULL,

                repository_url TEXT NOT NULL,

                overall_score REAL NOT NULL,

                overall_status TEXT NOT NULL,

                code_quality_score REAL NOT NULL,

                security_score REAL NOT NULL,

                project_health_score REAL NOT NULL,

                scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()

    finally:

        connection.close()


# ==========================================================
# SAVE SCAN
# ==========================================================

def save_scan_history(
    repository_name,
    repository_url,
    overall_score,
    overall_status,
    code_quality_score,
    security_score,
    project_health_score
):
    """
    Save a repository analysis result.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO scan_history (
                repository_name,
                repository_url,
                overall_score,
                overall_status,
                code_quality_score,
                security_score,
                project_health_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                repository_name,
                repository_url,
                overall_score,
                overall_status,
                code_quality_score,
                security_score,
                project_health_score
            )
        )

        connection.commit()

        return cursor.lastrowid

    finally:

        connection.close()


# ==========================================================
# GET SCAN HISTORY
# ==========================================================

def get_scan_history(limit=20):
    """
    Return the most recent repository scans.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                repository_name,
                repository_url,
                overall_score,
                overall_status,
                code_quality_score,
                security_score,
                project_health_score,
                scanned_at
            FROM scan_history
            ORDER BY scanned_at DESC, id DESC
            LIMIT ?
            """,
            (limit,)
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# ==========================================================
# GET SINGLE SCAN
# ==========================================================

def get_scan_by_id(scan_id):
    """
    Return a single scan history record.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                repository_name,
                repository_url,
                overall_score,
                overall_status,
                code_quality_score,
                security_score,
                project_health_score,
                scanned_at
            FROM scan_history
            WHERE id = ?
            """,
            (scan_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:

        connection.close()


# ==========================================================
# DELETE SCAN
# ==========================================================

def delete_scan_history(scan_id):
    """
    Delete one scan history record.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM scan_history
            WHERE id = ?
            """,
            (scan_id,)
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:

        connection.close()


# ==========================================================
# CLEAR HISTORY
# ==========================================================

def clear_scan_history():
    """
    Delete all scan history records.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM scan_history
            """
        )

        connection.commit()

        return cursor.rowcount

    finally:

        connection.close()