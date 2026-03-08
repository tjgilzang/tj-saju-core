-- ----------------------------------------------------------
-- MDB Tools - A library for reading MS Access database files
-- Copyright (C) 2000-2011 Brian Bruns and others.
-- Files in libmdb are licensed under LGPL and the utilities under
-- the GPL, see COPYING.LIB and COPYING files respectively.
-- Check out http://mdbtools.sourceforge.net
-- ----------------------------------------------------------

-- That file uses encoding UTF-8

CREATE TABLE [life12]
 (
	[Txt]			Memo/Hyperlink (255), 
	[Year12]			Memo/Hyperlink (255), 
	[Month12]			Memo/Hyperlink (255), 
	[idx]			Long Integer
);

CREATE TABLE [main]
 (
	[Txt]			Memo/Hyperlink (255), 
	[index]			Memo/Hyperlink (255), 
	[idx]			Long Integer
);

CREATE TABLE [life12Title]
 (
	[Txt]			Memo/Hyperlink (255), 
	[Year12]			Memo/Hyperlink (255), 
	[idx]			Long Integer
);

CREATE TABLE [btype_couple]
 (
	[idx]			Long Integer, 
	[basic]			Memo/Hyperlink (255), 
	[txt]			Memo/Hyperlink (255), 
	[mf]			Memo/Hyperlink (255)
);

CREATE TABLE [dream]
 (
	[txt]			Memo/Hyperlink (255), 
	[idx]			Memo/Hyperlink (255), 
	[index]			Long Integer
);

CREATE TABLE [sal]
 (
	[idx]			Long Integer, 
	[sal]			Memo/Hyperlink (255), 
	[txt]			Memo/Hyperlink (255)
);

CREATE TABLE [sin]
 (
	[idx]			Long Integer, 
	[sin]			Memo/Hyperlink (255), 
	[txt]			Memo/Hyperlink (255)
);

CREATE TABLE [gilbog]
 (
	[idx]			Long Integer, 
	[title]			Text (50), 
	[txt]			Memo/Hyperlink (255)
);

CREATE TABLE [fourbody]
 (
	[four]			Text (50), 
	[txt]			Memo/Hyperlink (255), 
	[idx]			Long Integer
);


