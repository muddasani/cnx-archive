-- ###
-- Copyright (c) 2013, Rice University
-- This software is subject to the provisions of the GNU Affero General
-- Public License version 3 (AGPLv3).
-- See LICENCE.txt for details.
-- ###

-- arguments:

SELECT row_to_json(combined_rows) AS module
FROM (
SELECT
  name,
  COALESCE(priority, default_priority) AS priority,
  COALESCE(message, default_message) AS message,
  iso8601("start") AS "start",
  iso8601("end") AS "end"
FROM service_state_messages NATURAL LEFT JOIN service_states
WHERE
  "end" > now()
ORDER BY 2 ASC, 4 DESC
) combined_rows ;
