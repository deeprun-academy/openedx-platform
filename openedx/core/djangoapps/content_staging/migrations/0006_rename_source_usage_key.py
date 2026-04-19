"""
Rename content_staging_userclipboard._source_usage_key -> source_usage_key.

The model declares `source_usage_key` but historical DBs carry the legacy
`_source_usage_key` column, so Studio raises OperationalError (1054) when
rendering the course outline. This migration is idempotent: it only renames
the column when the legacy name still exists, so environments that were
patched out-of-band (e.g. dev via manual ALTER) remain safe.
"""
from django.db import migrations


FORWARD_SQL = """
SET @has_legacy := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'content_staging_userclipboard'
      AND COLUMN_NAME = '_source_usage_key'
);
SET @stmt := IF(
    @has_legacy > 0,
    'ALTER TABLE content_staging_userclipboard '
    'CHANGE `_source_usage_key` `source_usage_key` varchar(255) NOT NULL',
    'DO 0'
);
PREPARE s FROM @stmt; EXECUTE s; DEALLOCATE PREPARE s;
"""

REVERSE_SQL = """
SET @has_new := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'content_staging_userclipboard'
      AND COLUMN_NAME = 'source_usage_key'
);
SET @stmt := IF(
    @has_new > 0,
    'ALTER TABLE content_staging_userclipboard '
    'CHANGE `source_usage_key` `_source_usage_key` varchar(255) NOT NULL',
    'DO 0'
);
PREPARE s FROM @stmt; EXECUTE s; DEALLOCATE PREPARE s;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('content_staging', '0005_stagedcontent_version_num'),
    ]

    operations = [
        migrations.RunSQL(sql=FORWARD_SQL, reverse_sql=REVERSE_SQL),
    ]
