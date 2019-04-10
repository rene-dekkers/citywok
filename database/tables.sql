create table cw_users (
	user_id		integer		primary key
,	username	varchar		not null
,	password	varchar
,	user_enabled	boolean		not null default true
,	auth_externally	boolean		not null default false
,	auth_by_url	varchar
);
