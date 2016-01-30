# -*- coding: utf-8 -*-
"""\
- Add a ``media_type`` column to the ``files`` table.
- Move the mimetype value from ``module_files`` to ``files``.
- Remove the ``mimetype`` column from the ``module_files`` table.

"""
import warnings


def up(cursor):
    # Add a ``media_type`` column to the ``files`` table.
    cursor.execute("ALTER TABLE files ADD COLUMN media_type TEXT")

    # Move the mimetype value from ``module_files`` to ``files``.
    cursor.execute("UPDATE files AS f SET media_type = mf.mimetype "
                   "FROM module_files AS mf "
                   "WHERE mf.fileid = f.fileid")

    # Warn about missing mimetype.
    cursor.execute("select fileid, sha1 "
                   "from files as f "
                   "where f.fileid not in (select fileid from module_files)")
    rows = '\n'.join(['{}, {}'.format(fid, sha1)
                      for fid, sha1 in cursor.fetchall()])
    warnings.warn("These files (fileid, sha1) do not have a corresponding "
                  "module_files entry:\n{}\n"
                  .format(rows))

    # Remove the ``mimetype`` column from the ``module_files`` table.
    cursor.execute("ALTER TABLE module_files DROP COLUMN mimetype")


def down(cursor):
    # Add a ``mimetype`` column to the ``module_files`` table.
    cursor.execute("ALTER TABLE module_files ADD COLUMN mimetype TEXT")

    # Move the mimetype value from ``files`` to ``module_files``.
    warnings.warn("Rollback cannot accurately replace mimetype values that "
                  "were in the ``modules_files`` table.")
    cursor.execute("UPDATE module_files AS mf SET mimetype = f.media_type "
                   "FROM files AS f "
                   "WHERE f.fileid = mf.fileid")

    # Remove the ``mimetype`` column from the ``files`` table.
    cursor.execute("ALTER TABLE files DROP COLUMN media_type")
