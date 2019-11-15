from database.db import get_db


def seed_db():
    user = {
        'user': 'alexc',
        'password': 'pbkdf2:sha256:150000$KX15dfVi$35b82b679ffd59c339537f0ab0a6c0828eba70358dafcae833b356aaa25787ce'
    }

    items = [
        {
            'user_id': 1,
            'access_token': 'access-development-a76d833e-70ce-45c8-bbb3-9ea2bc6d5bb7',
            'id': 'OEX9y0o4bKIjgKBK98Y6uMjvDw8kzzC8mybay',
            'item_mask': 'ybay'
        },
        {
            'user_id': 1,
            'access_token': 'access-development-e9c83380-03f1-4af8-9dcb-73cad8d3ea0b',
            'id': 'o7bZ5KDnONUeLw0zrEJAIg4mLmXQLofB6gB0g',
            'item_mask': 'gB0g'
        },
        {
            'user_id': 1,
            'access_token': 'access-development-5abb4009-a14d-49d1-8042-15baaeaa7dcb',
            'id': 'LQ8BRZzR7vs6d0KLa5QBFL04K1xj5KH0XxpXK',
            'item_mask': 'xpXK'
        }
    ]

    accounts = [
        {
            'id': 'MgRoBAEb53UmLVrVezxdcZYLkMxPdXtMzD3qY',
            'mask': '3165',
            'name': 'TD SIMPLE SAVINGS',
            'official_name': 'TD SIMPLE SAVINGS',
            'type': 'depository',
            'subtype': 'savings',
            'access_token': 'access-development-a76d833e-70ce-45c8-bbb3-9ea2bc6d5bb7'
        },
        {
            'id': 'OEX9y0o4bKIjgKBK98Y6uMjJpVo4nau8mXKDy',
            'mask': '3667',
            'name': 'TD CONVENIENCE CHECKING',
            'official_name': 'TD CONVENIENCE CHECKING',
            'type': 'depository',
            'subtype': 'checking',
            'access_token': 'access-development-a76d833e-70ce-45c8-bbb3-9ea2bc6d5bb7'
        }
    ]
    db = get_db()

    db.execute('INSERT INTO user (name, password) '
               'VALUES (?,?)', (user['user'],
                                user['password'],))
    db.commit()

    for item in items:
        db.execute('INSERT INTO item (user_id, access_token, id, item_mask) '
                   'VALUES (?, ?, ?, ?)', (item['user_id'],
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
