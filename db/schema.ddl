create table activity_details
(
  id      int auto_increment
    primary key,
  detail  varchar(100)        not null,
  comment text default 'NULL' null,
  constraint use_code_details_code_detail_uindex
  unique (detail)
);

create table activity_focuses
(
  id    int auto_increment
    primary key,
  focus varchar(20) not null,
  constraint activity_focus_types_type_uindex
  unique (focus)
);

create table activity_types
(
  id   int auto_increment
    primary key,
  type varchar(20) not null,
  constraint activity_types_type_uindex
  unique (type)
);

create table activities
(
  id                int auto_increment
    primary key,
  activity_type_id  int default 'NULL'  null,
  activity_focus_id int default 'NULL'  null,
  activity          varchar(20)         not null,
  comment           text default 'NULL' null,
  constraint use_codes_pk
  unique (activity_type_id, activity_focus_id),
  constraint use_codes_code_uindex
  unique (activity),
  constraint use_codes_activity_types_id_fk
  foreign key (activity_type_id) references activity_types (id)
    on update cascade
    on delete set null,
  constraint use_codes_activity_focus_types_id_fk
  foreign key (activity_focus_id) references activity_focuses (id)
    on update cascade
    on delete set null
);

create index use_codes_activity_focus_types_id_fk
  on activities (activity_focus_id);

create table renamings
(
  id            int auto_increment
    primary key,
  type          char(255) default 'NULL' null,
  original_name char(255) default 'NULL' null,
  new_name      char(255) default 'NULL' null,
  created_at    datetime default 'NULL'  null,
  updated_at    datetime default 'NULL'  null
);

create table request_archives
(
  id          int                     not null
    primary key,
  archive_for date default 'NULL'     null,
  created_at  datetime default 'NULL' null,
  updated_at  datetime default 'NULL' null
);

create table source_details
(
  id      int auto_increment
    primary key,
  detail  varchar(200)        not null,
  comment text default 'NULL' null,
  constraint source_code_details_code_detail_uindex
  unique (detail)
);

create table source_languages
(
  id       int auto_increment
    primary key,
  language varchar(20) not null,
  constraint source_languages_abbrivation_uindex
  unique (language)
);

create table sources
(
  id      int auto_increment
    primary key,
  source  varchar(20)         not null,
  comment text default 'NULL' null,
  constraint use_codes_code_name_uindex
  unique (source)
);

create table unsuccessful_codes
(
  id   int auto_increment
    primary key,
  code varchar(100) not null,
  constraint unsuccessful_codes_code_uindex
  unique (code)
);

create table unsuccessful_details
(
  id     int auto_increment
    primary key,
  detail varchar(100) not null,
  constraint unsuccessful_details_detail_uindex
  unique (detail)
);

create table unsuccessful_labels
(
  id    int auto_increment
    primary key,
  label varchar(100) not null,
  constraint unsuccessful_labels_label_uindex
  unique (label)
);

create table users
(
  id               int auto_increment
    primary key,
  type             char(255) default 'NULL'  null,
  wikidata_user_id int default 'NULL'        null,
  name             char(255) default 'NULL'  null,
  has_red_link     tinyint(1) default 'NULL' null,
  is_removed       tinyint(1) default 'NULL' null,
  has_bot_flag     tinyint(1) default 'NULL' null,
  is_extension_bot tinyint(1) default 'NULL' null,
  first_edit       datetime default 'NULL'   null,
  last_edit        datetime default 'NULL'   null,
  life_time        int default 'NULL'        null,
  registered_at    datetime default 'NULL'   null,
  groups           char(255) default 'NULL'  null,
  edit_count       int default 'NULL'        null,
  created_at       datetime default 'NULL'   null,
  updated_at       datetime default 'NULL'   null,
  constraint users_pk
  unique (name, type)
);

create table requests
(
  id                         int auto_increment
    primary key,
  wikidata_page_id           int default 'NULL'        null,
  name                       char(255) default 'NULL'  null,
  has_red_link               tinyint(1) default 'NULL' null,
  is_successful              tinyint(1) default 'NULL' null,
  bot_name                   char(255) default 'NULL'  null,
  bot_name_has_red_link      tinyint(1) default 'NULL' null,
  operator_name              char(255) default 'NULL'  null,
  operator_name_has_red_link tinyint(1) default 'NULL' null,
  request_archive_id         int default 'NULL'        null,
  unsuccessful_code_id       int default 'NULL'        null,
  unsuccessful_detail_id     int default 'NULL'        null,
  unsuccessful_label_id      int default 'NULL'        null,
  closed_at                  datetime default 'NULL'   null,
  created_at                 datetime default 'NULL'   null,
  updated_at                 datetime default 'NULL'   null,
  constraint requests_users_name_fk_2
  foreign key (bot_name) references users (name)
    on update cascade
    on delete cascade,
  constraint requests_users_name_fk
  foreign key (operator_name) references users (name)
    on update cascade
    on delete cascade,
  constraint requests_request_archives_id_fk
  foreign key (request_archive_id) references request_archives (id)
    on update cascade
    on delete cascade,
  constraint requests_unsuccessful_codes_id_fk
  foreign key (unsuccessful_code_id) references unsuccessful_codes (id)
    on update cascade
    on delete cascade,
  constraint requests_unsuccessful_details_id_fk
  foreign key (unsuccessful_detail_id) references unsuccessful_details (id)
    on update cascade
    on delete cascade,
  constraint requests_unsuccessful_labels_id_fk
  foreign key (unsuccessful_label_id) references unsuccessful_labels (id)
    on update cascade
    on delete cascade
);

create table request_edits
(
  editor_id  int default 'NULL'      null,
  request_id int default 'NULL'      null,
  edited_at  datetime default 'NULL' null,
  created_at datetime default 'NULL' null,
  updated_at datetime default 'NULL' null,
  constraint request_edits_users_id_fk
  foreign key (editor_id) references users (id)
    on update cascade
    on delete cascade,
  constraint request_edits_requests_id_fk
  foreign key (request_id) references requests (id)
    on update cascade
    on delete cascade
);

create index request_edits_requests_id_fk
  on request_edits (request_id);

create index request_edits_users_id_fk
  on request_edits (editor_id);

create index requests_request_archives_id_fk
  on requests (request_archive_id);

create index requests_unsuccessful_codes_id_fk
  on requests (unsuccessful_code_id);

create index requests_unsuccessful_details_id_fk
  on requests (unsuccessful_detail_id);

create index requests_unsuccessful_labels_id_fk
  on requests (unsuccessful_label_id);

create index requests_users_name_fk
  on requests (operator_name);

create index requests_users_name_fk_2
  on requests (bot_name);

create table requests_activities
(
  request_id  int not null,
  activity_id int not null,
  primary key (request_id, activity_id),
  constraint requests_activities_requests__id_fk
  foreign key (request_id) references requests (id)
    on update cascade
    on delete cascade,
  constraint requests_activities_activities_id_fk
  foreign key (activity_id) references activities (id)
    on update cascade
    on delete cascade
);

create index classified_request_use_code_use_codes_id_fk
  on requests_activities (activity_id);

create table requests_activity_details
(
  request_id         int not null,
  activity_detail_id int not null,
  primary key (request_id, activity_detail_id),
  constraint requests_activity_details_requests__id_fk
  foreign key (request_id) references requests (id)
    on update cascade
    on delete cascade,
  constraint requests_activity_details_activity_details_id_fk
  foreign key (activity_detail_id) references activity_details (id)
    on update cascade
    on delete cascade
);

create index classified_request_use_code_detail_use_code_details_id_fk
  on requests_activity_details (activity_detail_id);

create table requests_source_details
(
  request_id       int not null,
  source_detail_id int not null,
  primary key (request_id, source_detail_id),
  constraint requests_source_details_requests__id_fk
  foreign key (request_id) references requests (id)
    on update cascade
    on delete cascade,
  constraint requests_source_details_source_details_id_fk
  foreign key (source_detail_id) references source_details (id)
    on update cascade
    on delete cascade
);

create index classified_request_source_code_detail_source_code_details_id_fk
  on requests_source_details (source_detail_id);

create table requests_source_languages
(
  request_id         int not null,
  source_language_id int not null,
  primary key (request_id, source_language_id),
  constraint requests_source_languages_requests__id_fk
  foreign key (request_id) references requests (id)
    on update cascade
    on delete cascade,
  constraint requests_source_languages_source_languages_id_fk
  foreign key (source_language_id) references source_languages (id)
    on update cascade
    on delete cascade
);

create index classified_request_source_language_source_languages_id_fk
  on requests_source_languages (source_language_id);

create table requests_sources
(
  request_id int not null,
  source_id  int not null,
  primary key (request_id, source_id),
  constraint requests_sources_requests__id_fk
  foreign key (request_id) references requests (id)
    on update cascade
    on delete cascade,
  constraint requests_sources_sources_id_fk
  foreign key (source_id) references sources (id)
    on update cascade
    on delete cascade
);

create index classified_request_source_code_source_codes_id_fk
  on requests_sources (source_id);

create table user_relations
(
  bot_id      int default 'NULL' null,
  operator_id int default 'NULL' null,
  constraint user_relations_users_id_fk
  foreign key (bot_id) references users (id)
    on update cascade
    on delete cascade,
  constraint user_relations_users_id_fk_2
  foreign key (operator_id) references users (id)
    on update cascade
    on delete cascade
);

create index user_relations_users_id_fk
  on user_relations (bot_id);

create index user_relations_users_id_fk_2
  on user_relations (operator_id);

