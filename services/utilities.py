def format_date(date):
    split_date = date.split('-')
    month = split_date[0]
    day = split_date[1]

    year = split_date[2]
    response_date = '-'.join([year, month, day])
    return response_date
