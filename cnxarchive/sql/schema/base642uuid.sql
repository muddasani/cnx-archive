CREATE OR REPLACE FUNCTION base642uuid (identifier character(24))
  RETURNS uuid
AS $$
  from cnxarchive.utils import base642uuid 
  return base642uuid(identifier)
$$ LANGUAGE plpythonu;