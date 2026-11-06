"""Mẫu phân công ngoài DB schema; không thay đổi báo cáo lịch sử."""
import json
import unicodedata
from NGHIEP_VU import AppError, clean_text

PROFILE_IDS = ('team1', 'team2', 'team3', 'day')


def default_templates():
    return {key: [] for key in PROFILE_IDS}


def parse_templates(text):
    if not isinstance(text, str) or len(text) > 600000:
        raise AppError('MAU_PHAN_CONG.json: dữ liệu sai kiểu hoặc quá dài.')
    try:
        data = json.loads(text)
    except ValueError:
        raise AppError('MAU_PHAN_CONG.json sai định dạng. Mở Mẫu phân công để sửa.')
    if not isinstance(data, dict) or set(data) != set(PROFILE_IDS):
        raise AppError('Mẫu phân công cần đủ Ca 1, Ca 2, Ca 3 và nhân sự ca ngày.')
    result = {}
    for key in PROFILE_IDS:
        rows = data[key]
        if not isinstance(rows, list) or len(rows) > 200:
            raise AppError(key + ': tối đa 200 dòng mẫu phân công.')
        checked, seen = [], set()
        for row in rows:
            if not isinstance(row, dict):
                raise AppError(key + ': dòng phân công sai định dạng.')
            role = unicodedata.normalize('NFC', clean_text(row.get('role', ''), 150))
            if not role or role.casefold() in seen:
                raise AppError(key + ': vị trí trống hoặc trùng trong mẫu phân công.')
            seen.add(role.casefold())
            names = row.get('people')
            if not isinstance(names, list) or len(names) > 500:
                raise AppError(key + ' / ' + role + ': danh sách người sai định dạng.')
            people, named = [], set()
            for value in names:
                if not isinstance(value, str) or any(ord(c)<32 for c in value) or ';' in value:
                    raise AppError(key + ' / ' + role + ': mỗi mục phải là một họ tên.')
                name = unicodedata.normalize('NFC', clean_text(value, 120))
                if not name or name.casefold() in named:
                    raise AppError(key + ' / ' + role + ': tên trống hoặc bị trùng.')
                people.append(name); named.add(name.casefold())
            if len('; '.join(people)) > 3000:
                raise AppError(key + ' / ' + role + ': danh sách người vượt giới hạn báo cáo.')
            checked.append(dict(role=role, people=people))
        result[key] = checked
    return result


def validate_templates(data):
    people, roles = set(data['people']), set(data['roles'])
    for key, rows in data['staff_templates'].items():
        for row in rows:
            if row['role'] not in roles:
                raise AppError(key + ': vị trí ' + row['role'] + ' chưa có trong danh mục Vị trí phân công.')
            for name in row['people']:
                if name not in people:
                    raise AppError(key + ' / ' + row['role'] + ': ' + name + ' chưa có trong danh mục Nhân viên.')


def merge_team_members(data):
    """Trả về bản sao danh sách tổ, thêm người đã chọn trong mẫu của đúng tổ đó.

    Người trong mẫu ca luân phiên cũng phải hiện trong danh sách chọn của tổ.
    Nhân sự ca ngày vẫn độc lập, không tự gán vào tổ nào. Không sửa dữ liệu đầu vào.
    """
    teams = []
    for team in data['teams']:
        people = list(team['people'])
        for row in data['staff_templates'][team['id']]:
            for name in row['people']:
                if name not in people:
                    people.append(name)
        teams.append(dict(team, people=people))
    return teams
