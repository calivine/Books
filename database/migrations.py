from database.db import get_db


def seed_db():
    from database.seeders import user, items, accounts, budget

    db = get_db()

    db.execute("INSERT INTO user (name, password) "
               "VALUES (?,?)", (user['user'],
                                user['password'],))
    db.commit()

    for item in items:
        db.execute("INSERT INTO item (user_id, access_token, id, item_mask) "
                   "VALUES (?, ?, ?, ?)", (item['user_id'],
                                           item['access_token'],
                                           item['id'],
                                           item['item_mask'],))
        db.commit()

    for account in accounts:
        db.execute("INSERT INTO account (id, mask, name, official_name, type, subtype, access_token) "
                   "VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (account['id'],
                    account['mask'],
                    account['name'],
                    account['official_name'],
                    account['type'],
                    account['subtype'],
                    account['access_token'],))
        db.commit()

    db.execute("INSERT INTO budget (user_id, category, planned, actual, period)" 
               "VALUES (?, ?, ?, ?, ?)", (budget['user_id'],
                                             budget['category'],
                                             budget['planned'],
                                             budget['actual'],
                                             budget['period'],))
    db.commit()

