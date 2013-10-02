CREATE OR REPLACE FUNCTION tree_to_json(TEXT, TEXT) RETURNS TEXT as $$
select string_agg(toc,'
'
) from (
WITH RECURSIVE t(node, title, path,value, depth, corder) AS (
    SELECT nodeid, title, ARRAY[nodeid], documentid, 1, ARRAY[childorder]
    FROM trees tr, modules m
    WHERE m.uuid::text = $1 AND
      CASE
        WHEN m.portal_type = 'Collection'
          THEN m.major_version || '.' || m.minor_version
        ELSE m.major_version || ''
      END = $2 AND
      tr.documentid = m.module_ident
UNION ALL
    SELECT c1.nodeid, c1.title, t.path || ARRAY[c1.nodeid], c1.documentid, t.depth+1, t.corder || ARRAY[c1.childorder] /* Recursion */
    FROM trees c1 JOIN t ON (c1.parent_id = t.node)
    WHERE not nodeid = any (t.path)
)
SELECT
    REPEAT('    ', depth - 1) || '{"id":"' || COALESCE(m.uuid::text,'subcol') ||COALESCE('@'||
      CASE WHEN m.portal_type = 'Collection' THEN m.major_version || '.' || m.minor_version ELSE m.major_version || '' END,
      '') ||'",' ||
      '"title":'||to_json(COALESCE(title,name))||
      CASE WHEN (depth < lead(depth,1,0) over(w)) THEN ', "contents":['
           WHEN (depth > lead(depth,1,0) over(w) AND lead(depth,1,0) over(w) = 0 ) THEN '}'||REPEAT(']}',depth - lead(depth,1,0) over(w) - 1)
           WHEN (depth > lead(depth,1,0) over(w) AND lead(depth,1,0) over(w) != 0 ) THEN '}'||REPEAT(']}',depth - lead(depth,1,0) over(w))||','
           ELSE '},' END
      AS "toc"
FROM t left join  modules m on t.value = m.module_ident
    WINDOW w as (ORDER BY corder) order by corder ) tree ;
$$ LANGUAGE SQL;

--
-- Name: modules_in_tree(uuid, text); Type: FUNCTION; Schema: public; Owner: rhaptos
--

CREATE FUNCTION modules_in_tree(treeid int) RETURNS SETOF integer
    LANGUAGE sql
    AS $_$

WITH RECURSIVE t(node, path, value) AS (
    SELECT nodeid, ARRAY[nodeid], documentid
    FROM trees
    WHERE documentid = treeid
UNION ALL
    SELECT c1.nodeid, t.path || ARRAY[c1.nodeid], c1.documentid /* Recursion */
    FROM trees c1 JOIN t ON (c1.parent_id = t.node)
    WHERE not nodeid = any (t.path)
)
SELECT
    value
FROM t where value != treeid
     ;
$_$;

