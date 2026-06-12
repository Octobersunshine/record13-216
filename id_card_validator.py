import re
import random
from datetime import date, datetime

WEIGHTS = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
CHECK_CODES = ('1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2')

REGION_CODES = {
    '11': '北京市', '12': '天津市', '13': '河北省', '14': '山西省', '15': '内蒙古自治区',
    '21': '辽宁省', '22': '吉林省', '23': '黑龙江省',
    '31': '上海市', '32': '江苏省', '33': '浙江省', '34': '安徽省', '35': '福建省', '36': '江西省', '37': '山东省',
    '41': '河南省', '42': '湖北省', '43': '湖南省', '44': '广东省', '45': '广西壮族自治区',
    '50': '重庆市', '51': '四川省', '52': '贵州省', '53': '云南省', '54': '西藏自治区',
    '61': '陕西省', '62': '甘肃省', '63': '青海省', '64': '宁夏回族自治区', '65': '新疆维吾尔自治区',
    '71': '台湾省', '81': '香港特别行政区', '82': '澳门特别行政区',
}


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    if year % 4 == 0:
        return True
    return False


def validate_birth_date(year: int, month: int, day: int) -> tuple[bool, str]:
    if year < 1900 or year > 9999:
        return False, f'年份 {year} 超出有效范围'
    if month < 1 or month > 12:
        return False, f'月份 {month} 无效'
    if day < 1:
        return False, f'日期 {day} 不能小于1'

    days_in_month = {
        1: 31, 2: 29 if is_leap_year(year) else 28,
        3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31,
        11: 30, 12: 31,
    }

    max_day = days_in_month[month]
    if day > max_day:
        if month == 2 and day == 29:
            return False, f'{year}年不是闰年，2月没有29日'
        return False, f'{month}月最多有{max_day}天'

    return True, '出生日期有效'


def validate_id_card(id_card: str) -> bool:
    return validate_id_card_with_reason(id_card)[0]


def validate_id_card_with_reason(id_card: str) -> tuple[bool, str]:
    if not isinstance(id_card, str):
        return False, '身份证号必须是字符串类型'
    id_card = id_card.strip().upper()
    if not re.match(r'^\d{17}[\dX]$', id_card):
        return False, '身份证号格式不正确，必须为18位数字或末尾为X'
    region_code = id_card[:2]
    if region_code not in REGION_CODES:
        return False, f'地区代码 {region_code} 无效'

    birth_str = id_card[6:14]
    try:
        year = int(birth_str[:4])
        month = int(birth_str[4:6])
        day = int(birth_str[6:8])
    except ValueError:
        return False, f'出生日期 {birth_str} 无法解析'

    date_valid, date_reason = validate_birth_date(year, month, day)
    if not date_valid:
        return False, f'出生日期 {birth_str} 无效: {date_reason}'

    birth_date = date(year, month, day)
    if birth_date > date.today():
        return False, f'出生日期 {birth_date} 不能晚于今天'

    check_sum = sum(int(id_card[i]) * WEIGHTS[i] for i in range(17))
    expected_check_code = CHECK_CODES[check_sum % 11]
    if id_card[17] != expected_check_code:
        return False, f'校验位错误，应为 {expected_check_code}，实际为 {id_card[17]}'
    return True, '身份证号有效'


def extract_birth_date(id_card: str) -> date:
    valid, reason = validate_id_card_with_reason(id_card)
    if not valid:
        raise ValueError(f'Invalid ID card number: {reason}')
    birth_str = id_card[6:14]
    year = int(birth_str[:4])
    month = int(birth_str[4:6])
    day = int(birth_str[6:8])
    return date(year, month, day)


def extract_gender(id_card: str) -> str:
    valid, reason = validate_id_card_with_reason(id_card)
    if not valid:
        raise ValueError(f'Invalid ID card number: {reason}')
    gender_code = int(id_card[16])
    return '男' if gender_code % 2 == 1 else '女'


def calculate_age(id_card: str, today: date = None) -> int:
    return calculate_age_detail(id_card, today=today)['years']


def calculate_age_detail(id_card: str, today: date = None) -> dict:
    birth_date = extract_birth_date(id_card)
    if today is None:
        today = date.today()

    if today < birth_date:
        return {
            'years': 0,
            'months': 0,
            'days': 0,
            'total_months': 0,
            'total_days': 0,
            'summary': '未出生',
        }

    birth_year = birth_date.year
    birth_month = birth_date.month
    birth_day = birth_date.day

    def get_effective_birthday(target_year: int) -> date:
        if birth_month == 2 and birth_day == 29 and not is_leap_year(target_year):
            return date(target_year, 3, 1)
        return date(target_year, birth_month, birth_day)

    def days_in_month(year: int, month: int) -> int:
        if month == 2:
            return 29 if is_leap_year(year) else 28
        elif month in (4, 6, 9, 11):
            return 30
        else:
            return 31

    years = today.year - birth_year
    this_year_birthday = get_effective_birthday(today.year)

    if today < this_year_birthday:
        years -= 1

    if years < 0:
        years = 0

    last_anniversary = get_effective_birthday(birth_year + years)
    next_full_anniversary = get_effective_birthday(birth_year + years + 1)

    effective_today = today
    if effective_today >= next_full_anniversary:
        effective_today = date.fromordinal(next_full_anniversary.toordinal() - 1)

    anniv_day = last_anniversary.day

    month_diff = (effective_today.year - last_anniversary.year) * 12 + (effective_today.month - last_anniversary.month)

    today_month_max = days_in_month(effective_today.year, effective_today.month)
    month_anniv_day = min(anniv_day, today_month_max)

    if effective_today.day >= month_anniv_day:
        months = month_diff
        days = effective_today.day - month_anniv_day
    else:
        months = month_diff - 1
        prev_month_year = effective_today.year
        prev_month = effective_today.month - 1
        if prev_month < 1:
            prev_month = 12
            prev_month_year -= 1
        days_in_prev = days_in_month(prev_month_year, prev_month)
        prev_anniv_day = min(anniv_day, days_in_prev)
        days = days_in_prev - prev_anniv_day + effective_today.day

    if months < 0:
        months = 0

    total_months = years * 12 + months
    total_days = (today - birth_date).days

    return {
        'years': years,
        'months': months,
        'days': days,
        'total_months': total_months,
        'total_days': total_days,
        'summary': f'{years}岁{months}个月零{days}天',
    }


def days_until_birthday(id_card: str, today: date = None) -> int:
    birth_date = extract_birth_date(id_card)
    if today is None:
        today = date.today()

    birth_month = birth_date.month
    birth_day = birth_date.day

    def get_effective_birthday(target_year: int) -> date:
        if birth_month == 2 and birth_day == 29 and not is_leap_year(target_year):
            return date(target_year, 3, 1)
        return date(target_year, birth_month, birth_day)

    this_year_birthday = get_effective_birthday(today.year)

    if this_year_birthday > today:
        next_birthday = this_year_birthday
    else:
        next_birthday = get_effective_birthday(today.year + 1)

    return (next_birthday - today).days


def total_days_alive(id_card: str, today: date = None) -> int:
    birth_date = extract_birth_date(id_card)
    if today is None:
        today = date.today()
    return (today - birth_date).days


def extract_region(id_card: str) -> str:
    valid, reason = validate_id_card_with_reason(id_card)
    if not valid:
        raise ValueError(f'Invalid ID card number: {reason}')
    region_code = id_card[:2]
    return REGION_CODES.get(region_code, '未知地区')


def get_id_card_info(id_card: str, detail: bool = True) -> dict:
    valid, reason = validate_id_card_with_reason(id_card)
    if not valid:
        raise ValueError(f'Invalid ID card number: {reason}')

    age_detail = calculate_age_detail(id_card)

    result = {
        'id_card': id_card.upper(),
        'valid': True,
        'birth_date': extract_birth_date(id_card).strftime('%Y-%m-%d'),
        'gender': extract_gender(id_card),
        'age': age_detail['years'],
        'age_verbose': age_detail['summary'],
        'region': extract_region(id_card),
    }

    if detail:
        result['age_detail'] = age_detail
        result['days_until_birthday'] = days_until_birthday(id_card)
        result['total_days_alive'] = total_days_alive(id_card)

    return result


def calculate_check_code(id_card_17: str) -> str:
    if len(id_card_17) != 17 or not id_card_17.isdigit():
        raise ValueError('必须提供17位数字')
    check_sum = sum(int(id_card_17[i]) * WEIGHTS[i] for i in range(17))
    return CHECK_CODES[check_sum % 11]


def generate_test_id_card(
    region_code: str = '11',
    birth_year: int = None,
    birth_month: int = None,
    birth_day: int = None,
    gender: str = None,
) -> str:
    if region_code not in REGION_CODES:
        raise ValueError(f'无效的地区代码: {region_code}')

    if birth_year is None:
        birth_year = random.randint(1950, 2010)
    if birth_month is None:
        birth_month = random.randint(1, 12)
    if birth_day is None:
        max_day = 29 if (birth_month == 2 and is_leap_year(birth_year)) else (
            28 if birth_month == 2 else (
                30 if birth_month in (4, 6, 9, 11) else 31
            )
        )
        birth_day = random.randint(1, max_day)

    date_valid, date_reason = validate_birth_date(birth_year, birth_month, birth_day)
    if not date_valid:
        raise ValueError(f'无效的出生日期: {date_reason}')

    birth_date = date(birth_year, birth_month, birth_day)
    if birth_date > date.today():
        raise ValueError('出生日期不能晚于今天')

    city_code = f'{region_code}{random.randint(1, 99):02d}'
    district_code = f'{city_code}{random.randint(1, 99):02d}'
    birth_str = f'{birth_year:04d}{birth_month:02d}{birth_day:02d}'
    sequence = random.randint(1, 999)

    if gender == '男':
        sequence = sequence if sequence % 2 == 1 else sequence + 1
    elif gender == '女':
        sequence = sequence if sequence % 2 == 0 else sequence + 1

    sequence_str = f'{sequence:03d}'
    first_17 = f'{district_code}{birth_str}{sequence_str}'
    check_code = calculate_check_code(first_17)

    return f'{first_17}{check_code}'
