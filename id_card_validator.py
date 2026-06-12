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
    try:
        birth_date = datetime.strptime(id_card[6:14], '%Y%m%d').date()
    except ValueError:
        return False, f'出生日期 {id_card[6:14]} 无效'
    if birth_date > date.today():
        return False, f'出生日期 {birth_date} 不能晚于今天'
    check_sum = sum(int(id_card[i]) * WEIGHTS[i] for i in range(17))
    expected_check_code = CHECK_CODES[check_sum % 11]
    if id_card[17] != expected_check_code:
        return False, f'校验位错误，应为 {expected_check_code}，实际为 {id_card[17]}'
    return True, '身份证号有效'


def extract_birth_date(id_card: str) -> date:
    if not validate_id_card(id_card):
        raise ValueError('Invalid ID card number')
    return datetime.strptime(id_card[6:14], '%Y%m%d').date()


def extract_gender(id_card: str) -> str:
    if not validate_id_card(id_card):
        raise ValueError('Invalid ID card number')
    gender_code = int(id_card[16])
    return '男' if gender_code % 2 == 1 else '女'


def calculate_age(id_card: str) -> int:
    birth_date = extract_birth_date(id_card)
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def extract_region(id_card: str) -> str:
    if not validate_id_card(id_card):
        raise ValueError('Invalid ID card number')
    region_code = id_card[:2]
    return REGION_CODES.get(region_code, '未知地区')


def get_id_card_info(id_card: str) -> dict:
    if not validate_id_card(id_card):
        valid, reason = validate_id_card_with_reason(id_card)
        raise ValueError(f'Invalid ID card number: {reason}')
    return {
        'id_card': id_card.upper(),
        'valid': True,
        'birth_date': extract_birth_date(id_card).strftime('%Y-%m-%d'),
        'gender': extract_gender(id_card),
        'age': calculate_age(id_card),
        'region': extract_region(id_card),
    }


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
        birth_day = random.randint(1, 28)

    try:
        birth_date = date(birth_year, birth_month, birth_day)
    except ValueError as e:
        raise ValueError(f'无效的出生日期: {e}')

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
