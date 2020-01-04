DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS activity;
DROP TABLE IF EXISTS budget;


CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    password TEXT
);

CREATE TABLE item (
    user_id INTEGER,
    access_token TEXT,
    id TEXT,
    item_mask TEXT,
    institution TEXT,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE account (
    id TEXT,
    mask TEXT,
    name TEXT,
    official_name TEXT,
    type TEXT,
    subtype TEXT,
    access_token TEXT
);

CREATE TABLE activity (
    account_id TEXT,
    amount INTEGER,
    category TEXT,
    category_id TEXT,
    date TEXT,
    iso_currency_code TEXT,
    name TEXT,
    pending INTEGER,
    pending_transaction TEXT,
    transaction_id TEXT,
    transaction_type TEXT,
    budget TEXT,
    category_type TEXT,
    category_name TEXT,
    sub_category TEXT
);

CREATE TABLE budget (
    user_id INTEGER,
    category TEXT NOT NULL,
    planned INTEGER NOT NULL,
    actual INTEGER NOT NULL,
    period TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE category (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
