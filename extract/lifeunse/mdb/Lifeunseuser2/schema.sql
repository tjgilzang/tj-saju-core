-- ----------------------------------------------------------
-- MDB Tools - A library for reading MS Access database files
-- Copyright (C) 2000-2011 Brian Bruns and others.
-- Files in libmdb are licensed under LGPL and the utilities under
-- the GPL, see COPYING.LIB and COPYING files respectively.
-- Check out http://mdbtools.sourceforge.net
-- ----------------------------------------------------------

-- That file uses encoding UTF-8

CREATE TABLE [data]
 (
	[u_address]			Text (255), 
	[u_memo]			Memo/Hyperlink (255), 
	[id]			Long Integer, 
	[u_name]			Text (50), 
	[u_namehanja]			Text (50), 
	[u_year]			Text (4), 
	[u_month]			Text (2), 
	[u_day]			Text (2), 
	[u_hour]			Text (50), 
	[u_sex]			Text (2), 
	[u_solar]			Text (2), 
	[u_hometel]			Text (50), 
	[u_handtel]			Text (50), 
	[u_job]			Text (50), 
	[u_minute]			Text (50)
);


