"""
Advanced Conversions Database — File Converter Pro
converter/advanced_db.py

Separate SQLite database that stores only conversions performed through the
AdvancedConversionsDialog (documents, images, audio/video).

Why a separate DB?
    - Keeps the main database (file_converter_stats.db) clean and focused on
      the core conversion history shown on the existing dashboard.
    - Lets the user pick which database to visualise in StatisticsDashboard
      without mixing basic and advanced data.

Tables:
    adv_conversion_history : one row per advanced conversion attempt
    adv_daily_stats        : aggregated daily counters

Author: Hyacinthe
Version: 1.0
"""

import sqlite3
import csv
import json
from datetime import datetime, timedelta

# Default DB file at application root
DEFAULT_DB_PATH = "file_converter_advanced.db"

class AdvancedDatabaseManager:
    """
    Manages the dedicated SQLite database for advanced conversions.

    Usage
    -----
    db = AdvancedDatabaseManager()                  # default path
    db = AdvancedDatabaseManager("custom/path.db")  # custom path
    db.add_record(...)
    """

    # Conversion-type categories tracked in daily_stats
    _CATEGORY_COLUMNS = {
        "document" : "doc_conversions",
        "image"    : "img_conversions",
        "audio"    : "audio_conversions",
        "video"    : "video_conversions",
    }

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self._init_database()

    # Schema
    def _init_database(self) -> None:
        with self._connect() as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS adv_conversion_history (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
                source_file     TEXT,
                source_format   TEXT,
                target_file     TEXT,
                target_format   TEXT,
                conversion_type TEXT,
                category        TEXT,
                file_size       INTEGER DEFAULT 0,
                conversion_time REAL    DEFAULT 0.0,
                success         BOOLEAN DEFAULT 1,
                error_message   TEXT    DEFAULT ''
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS adv_daily_stats (
                date              DATE PRIMARY KEY,
                total_conversions INTEGER DEFAULT 0,
                total_size        INTEGER DEFAULT 0,
                doc_conversions   INTEGER DEFAULT 0,
                img_conversions   INTEGER DEFAULT 0,
                audio_conversions INTEGER DEFAULT 0,
                video_conversions INTEGER DEFAULT 0
            )
            """)

            conn.commit()

    # Connection helper
    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    # Write
    def add_record(
        self,
        source_file: str,
        source_format: str,
        target_file: str,
        target_format: str,
        conversion_type: str,
        category: str,          # "document" | "image" | "audio" | "video"
        file_size: int   = 0,
        conversion_time: float = 0.0,
        success: bool    = True,
        error_message: str = "",
    ) -> int:
        """
        Insert one conversion record and update daily aggregates.
        Returns the new row id.
        """
        today = datetime.now().date().isoformat()

        with self._connect() as conn:
            cur = conn.cursor()

            cur.execute("""
            INSERT INTO adv_conversion_history
                (source_file, source_format, target_file, target_format,
                 conversion_type, category, file_size, conversion_time,
                 success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source_file, source_format, target_file, target_format,
                conversion_type, category, file_size, conversion_time,
                int(success), error_message,
            ))
            new_id = cur.lastrowid

            # Ensure today's row exists
            cur.execute(
                "INSERT OR IGNORE INTO adv_daily_stats (date) VALUES (?)", (today,)
            )

            col = self._CATEGORY_COLUMNS.get(category, "doc_conversions")
            cur.execute(f"""
            UPDATE adv_daily_stats
            SET total_conversions = total_conversions + 1,
                total_size        = total_size + ?,
                {col}             = {col} + 1
            WHERE date = ?
            """, (file_size, today))

            conn.commit()

        return new_id

    # Read
    def get_history(
        self,
        limit: int = 200,
        search_query: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        category: str | None = None,
    ) -> list[tuple]:
        """
        Return conversion history rows, most recent first.

        Columns (in order):
            id, timestamp, source_file, source_format, target_file,
            target_format, conversion_type, category, file_size,
            conversion_time, success, error_message
        """
        query = """
        SELECT id, timestamp, source_file, source_format,
               target_file, target_format, conversion_type, category,
               file_size, conversion_time, success, error_message
        FROM adv_conversion_history
        WHERE 1=1
        """
        params: list = []

        if search_query:
            query += " AND (source_file LIKE ? OR target_file LIKE ? OR conversion_type LIKE ?)"
            p = f"%{search_query}%"
            params.extend([p, p, p])

        if start_date:
            query += " AND DATE(timestamp) >= ?"
            params.append(start_date)

        if end_date:
            query += " AND DATE(timestamp) <= ?"
            params.append(end_date)

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.fetchall()

    def get_statistics(self, days: int = 30) -> dict:
        """
        Return aggregated statistics for the last *days* days.

        Keys in the returned dict:
            general       : (total, total_size, total_time, avg_time)
            top_types     : [(conversion_type, count), ...]
            by_category   : [(category, count), ...]
            daily_stats   : [(date, total, size, doc, img, audio, video), ...]
        """
        end_date   = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        with self._connect() as conn:
            cur = conn.cursor()

            cur.execute("""
            SELECT COUNT(*), SUM(file_size), SUM(conversion_time), AVG(conversion_time)
            FROM adv_conversion_history
            WHERE success = 1
            """)
            general = cur.fetchone()

            cur.execute("""
            SELECT conversion_type, COUNT(*) AS cnt
            FROM adv_conversion_history
            WHERE success = 1
            GROUP BY conversion_type
            ORDER BY cnt DESC
            LIMIT 10
            """)
            top_types = cur.fetchall()

            cur.execute("""
            SELECT category, COUNT(*) AS cnt
            FROM adv_conversion_history
            WHERE success = 1
            GROUP BY category
            ORDER BY cnt DESC
            """)
            by_category = cur.fetchall()

            cur.execute("""
            SELECT date, total_conversions, total_size,
                   doc_conversions, img_conversions,
                   audio_conversions, video_conversions
            FROM adv_daily_stats
            WHERE date BETWEEN ? AND ?
            ORDER BY date
            """, (start_date.isoformat(), end_date.isoformat()))
            daily_stats = cur.fetchall()

        return {
            "general"    : general,
            "top_types"  : top_types,
            "by_category": by_category,
            "daily_stats": daily_stats,
        }

    # Export
    def export_history(self, filepath: str, fmt: str = "csv") -> None:
        """Export full history to *filepath* in 'csv' or 'json' format."""
        rows = self.get_history(limit=100_000)

        if fmt == "csv":
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "ID", "Date/Time", "Source File", "Source Format",
                    "Target File", "Target Format", "Conversion Type",
                    "Category", "Size (bytes)", "Time (s)", "Success", "Error"
                ])
                writer.writerows(rows)

        elif fmt == "json":
            keys = [
                "id", "timestamp", "source_file", "source_format",
                "target_file", "target_format", "conversion_type", "category",
                "file_size", "conversion_time", "success", "error_message"
            ]
            data = [dict(zip(keys, row)) for row in rows]
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        else:
            raise ValueError(f"Unknown export format: {fmt!r}")

    # Compatibility shim for StatisticsDashboard
    def get_conversion_history(
        self,
        limit: int = 200,
        search_query: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[tuple]:
        """
        Compatibility wrapper so StatisticsDashboard can swap db_manager
        without any code change.  Columns mirror DatabaseManager.get_conversion_history():
            id, timestamp, source_file, source_format, target_file,
            target_format, operation_type, file_size, conversion_time,
            success, notes
        """
        rows = self.get_history(
            limit=limit,
            search_query=search_query,
            start_date=start_date,
            end_date=end_date,
        )
        # remap: drop category col (index 7), rename error_message → notes
        return [
            (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[8], r[9], r[10], r[11])
            for r in rows
        ]

    def _get_statistics_raw(self, days: int = 30) -> dict:
        """Internal — calls the real SQL queries. Never monkey-patched."""
        return AdvancedDatabaseManager.get_statistics(self, days)

    def get_statistics_compat(self, days: int = 30) -> dict:
        """
        Compatibility wrapper returning the same dict shape as
        DatabaseManager.get_statistics() so StatisticsDashboard works unchanged.

        DatabaseManager.get_statistics() returns:
            general       : (total_conversions, total_size, total_time_s, avg_time_s)
            top_formats   : [(format_str, count), ...]
            top_operations: [(operation_str, count), ...]
            daily_stats   : [(date, total_conversions, total_size, total_time_saved_min), ...]

        Notes:
          - top_formats   → we use top_types (the actual conversion names, e.g. "txt_to_pdf")
          - top_operations→ same top_types list (best match: most frequent conversions)
          - daily_stats[3] = total_time_saved in minutes (dashboard multiplies back to seconds)
                             We store conversion_time in seconds, convert to minutes here.
        """
        stats   = self._get_statistics_raw(days)
        general = stats["general"]  # (count, total_size, total_time_s, avg_time_s)
        daily   = stats["daily_stats"]

        # general: keep shape identical
        # (total, total_size, total_time_s, avg_time_s) — dashboard uses index [2] as total_time
        general_compat = general  # already (count, size, time_s, avg_s) — perfect match

        # daily_stats compat: (date, total_conversions, total_size, total_time_saved_minutes)
        # dashboard does: total_time = stats['general'][2]  → seconds directly
        # daily row[3] = total_time_saved (minutes) used only for tooltip, not critical
        daily_compat = [
            (d[0], d[1], d[2], int((d[1] or 0) * 0.5))   # estimate 0.5 min saved per conversion
            for d in daily
        ]

        # top_formats → use conversion_type strings as "format" labels
        # top_operations → same list (dashboard shows both identically styled)
        top_types = stats["top_types"]   # [(conversion_type, count), ...]

        # Also enrich with human-readable labels
        _LABELS = {
            "txt_to_pdf":"TXT→PDF","rtf_to_pdf":"RTF→PDF",
            "txt_to_docx":"TXT→DOCX","rtf_to_docx":"RTF→DOCX",
            "csv_to_json":"CSV→JSON","json_to_csv":"JSON→CSV",
            "xlsx_to_pdf":"XLSX→PDF","xlsx_to_json":"XLSX→JSON",
            "xlsx_to_csv":"XLSX→CSV","pptx_to_pdf":"PPTX→PDF",
            "html_to_pdf":"HTML→PDF","pdf_to_html":"PDF→HTML",
            "epub_to_pdf":"EPUB→PDF",
            "jpeg_to_png":"JPEG→PNG","png_to_jpg":"PNG→JPG",
            "jpg_to_png":"JPG→PNG","webp_to_png":"WEBP→PNG",
            "bmp_to_png":"BMP→PNG","tiff_to_png":"TIFF→PNG",
            "wav_to_mp3":"WAV→MP3","mp3_to_wav":"MP3→WAV",
            "acc_to_mp3":"AAC→MP3","mp3_to_acc":"MP3→AAC",
            "flac_to_mp3":"FLAC→MP3","ogg_to_mp3":"OGG→MP3",
            "avi_to_mp4":"AVI→MP4","webm_to_mp4":"WEBM→MP4",
            "mkv_to_mp4":"MKV→MP4","mov_to_mp4":"MOV→MP4",
            "mp4_to_mp3":"MP4→MP3",
            "avi_to_mp3":"AVI→MP3","webm_to_mp3":"WEBM→MP3",
            "mkv_to_mp3":"MKV→MP3",
        }
        top_labeled = [(_LABELS.get(t, t), c) for t, c in top_types]

        return {
            "general"       : general_compat,
            "top_formats"   : top_labeled,
            "top_operations": top_labeled,
            "daily_stats"   : daily_compat,
        }