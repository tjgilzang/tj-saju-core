-- ----------------------------------------------------------
-- MDB Tools - A library for reading MS Access database files
-- Copyright (C) 2000-2011 Brian Bruns and others.
-- Files in libmdb are licensed under LGPL and the utilities under
-- the GPL, see COPYING.LIB and COPYING files respectively.
-- Check out http://mdbtools.sourceforge.net
-- ----------------------------------------------------------

-- That file uses encoding UTF-8

CREATE TABLE [datememo]
 (
	[idx]			Long Integer, 
	[u_date]			Text (255), 
	[u_datememo]			Memo/Hyperlink (255)
);

CREATE TABLE [postit]
 (
	[u_idx]			Long Integer, 
	[u_date]			Text (255), 
	[u_memo]			Memo/Hyperlink (255), 
	[u_x]			Text (255), 
	[u_y]			Text (255), 
	[u_w]			Text (255), 
	[u_h]			Text (255), 
	[u_open]			Text (255)
);


