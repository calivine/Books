import os

ALLOWED_EXTENSIONS = {'csv'}

UPLOAD_FOLDER = 'storage/temp'

PLAID_ENV = os.getenv('PLAID_ENV', 'development')

MONTH_STRING = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
]

month_shortened = [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec'
]

COLORS = [
    'rgba(220, 20, 60, 1)',
    'rgba(255, 165, 0, 1)',
    'rgba(255, 255, 0, 1)',
    'rgba(127, 255, 0, 1)',
    'rgba(0, 128, 0, 1)',
    'rgba(0, 255, 255, 1)',
    'rgba(0, 128, 128, 1)',
    'rgba(0, 0, 255, 1)',
    'rgba(0, 191, 255, 1)',
    'rgba(255, 0, 255, 1)',
    'rgba(75, 0, 130, 1)'
]
