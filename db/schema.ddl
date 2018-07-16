CREATE TABLE requests_for_permissions (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    url                   TEXT UNIQUE,
    bot_url               TEXT,
    bot_name              TEXT,
    bot_has_red_link      INTEGER,
    operator_url          TEXT,
    operator_name         TEXT,
    operator_has_red_link TEXT,
    is_successful         INTEGER,
    first_edit            DATE,
    last_edit             DATE,
    closed_at             DATE,
    revision_count        INTEGER,
    editor_count          INTEGER,
    comment_symbol_count  INTEGER,
    question_symbol_count INTEGER,
    oppose_symbol_count   INTEGER,
    answer_symbol_count   INTEGER,
    support_symbol_count  INTEGER,
    html                  TEXT,
    task                  TEXT,
    code                  TEXT,
    function              TEXT,
    archive_comment       TEXT,
    summary               TEXT,
    retrieved_at          DATE
);
CREATE TABLE bots (
    id               INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    userid           INTEGER UNIQUE,
    name             TEXT UNIQUE,
    has_botflag      INTEGER,
    is_extension_bot INTEGER,
    is_blocked       INTEGER,
    blockid          INTEGER,
    blockedby        TEXT,
    blockedbyid      INTEGER,
    blockedtimestamp DATE,
    blockreason      TEXT,
    blockexpiry      TEXT,
    groups           TEXT,
    implicitgroups   TEXT,
    rights           TEXT,
    editcount        INTEGER,
    registration     TEXT,
    redirect_to      INTEGER,
    retrieved_at     DATE
);