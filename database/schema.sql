DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS activity;

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
