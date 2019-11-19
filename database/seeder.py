from database.db import get_db


def seed_db():
    user = {
        'user': 'alexc',
        'password': 'pbkdf2:sha256:150000$KX15dfVi$35b82b679ffd59c339537f0ab0a6c0828eba70358dafcae833b356aaa25787ce'
    }

    items = [
        {
            'user_id': 1,
            'access_token': 'access-development-6aab33ce-a540-4bf0-a9d1-5db9e7011936',
            'id': 'EPQdNaz4mBh493EEvVmoUADK0ZgrjMHpM46d6',
            'item_mask': '46d6'
        },
        {
            'user_id': 1,
            'access_token': 'access-development-5abb4009-a14d-49d1-8042-15baaeaa7dcb',
            'id': 'LQ8BRZzR7vs6d0KLa5QBFL04K1xj5KH0XxpXK',
            'item_mask': 'xpXK'
        },
        {
            'user_id': 1,
            'access_token': 'access-development-a95f3a36-87b6-4107-96b1-5768a1361658',
            'id': 'bOXYMqJbJETBorONbvMxULbxY6dm77IqZnKwn',
            'item_mask': 'nKwn'
        }
    ]

    accounts = [
        {
            'id': 'gnVYadbybXIP6yvXDKnoHmwvj39JAktqYB1OV',
            'mask': '3165',
            'name': 'TD SIMPLE SAVINGS',
            'official_name': 'TD SIMPLE SAVINGS',
            'type': 'depository',
            'subtype': 'savings',
            'access_token': 'access-development-a95f3a36-87b6-4107-96b1-5768a1361658'
        },
        {
            'id': 'bOXYMqJbJETBorONbvMxULbODgj9yPFqZN7Ln',
            'mask': '3667',
            'name': 'TD CONVENIENCE CHECKING',
            'official_name': 'TD CONVENIENCE CHECKING',
            'type': 'depository',
            'subtype': 'checking',
            'access_token': 'access-development-a95f3a36-87b6-4107-96b1-5768a1361658'
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
