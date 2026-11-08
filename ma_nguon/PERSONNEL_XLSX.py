"""Bounded, read-only flat personnel XLSX inspection and import planning."""
import io
import os
import posixpath
import re
import unicodedata
import zipfile
from importlib.metadata import version
from importlib.metadata import PackageNotFoundError
from xml.etree.ElementTree import ParseError

from defusedxml import ElementTree as safe_xml
from defusedxml.common import DefusedXmlException

MAX_UPLOAD = 2 * 1024 * 1024
MAX_TOTAL = 16 * 1024 * 1024
MAX_MEMBER = 4 * 1024 * 1024
ALIASES = {'name': {'họ và tên', 'họ tên', 'tên nhân viên'}, 'code': {'mscđ', 'mã nhân viên'},
           'title': {'chức danh'}, 'group': {'nhóm/ca', 'tổ nhân sự'}}
MAIN = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
OFFICE_REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
ALLOWED_RELS = {'officeDocument', 'worksheet', 'styles', 'theme', 'sharedStrings',
                'core-properties', 'extended-properties', 'custom-properties'}
PINS = {'openpyxl': '3.1.5', 'defusedxml': '0.7.1', 'et_xmlfile': '2.0.0'}


class PersonnelXlsxError(ValueError):
    def __init__(self, code, message, sheet=None, row=None, column=None):
        super().__init__(message)
        self.code, self.message = code, message
        self.sheet, self.row, self.column = sheet, row, column


def _bad(message, sheet=None, row=None, column=None, limit=False):
    raise PersonnelXlsxError('LIMIT_EXCEEDED' if limit else 'INVALID_INPUT', message, sheet, row, column)


def _library():
    """Require the actual defusedxml parser, including in frozen applications."""
    try:
        if any(version(name) != pin for name, pin in PINS.items()):
            _bad('Thiếu hoặc sai phiên bản thư viện đọc Excel.')
        os.environ['OPENPYXL_LXML'] = 'False'
        os.environ['OPENPYXL_DEFUSEDXML'] = 'True'
        import openpyxl
        from openpyxl.xml import functions
        if (openpyxl.LXML or not openpyxl.DEFUSEDXML or
                functions.fromstring is not safe_xml.fromstring or functions.iterparse is not safe_xml.iterparse):
            _bad('Bộ đọc XML đã nạp không an toàn. Hãy khởi động lại bằng môi trường được hỗ trợ.')
        return openpyxl
    except (ImportError, LookupError, PackageNotFoundError) as error:
        raise PersonnelXlsxError('INVALID_INPUT', 'Không có bộ đọc Excel an toàn đúng phiên bản.') from error


def _tag(element):
    return element.tag.rsplit('}', 1)[-1]


def _xml(data):
    return safe_xml.fromstring(data, forbid_dtd=True, forbid_entities=True, forbid_external=True)


def _coord(value):
    match = re.fullmatch(r'([A-Z]{1,3})([1-9][0-9]*)', value or '')
    if not match:
        _bad('Tọa độ ô Excel không hợp lệ.')
    column = 0
    for char in match[1]:
        column = column * 26 + ord(char) - 64
    row = int(match[2])
    if row > 2000 or column > 64:
        _bad('Trang tính vượt giới hạn 2000 dòng hoặc 64 cột.', row=row, column=column, limit=True)
    return row, column


def _preflight(blob):
    if not isinstance(blob, bytes) or not blob:
        _bad('File Excel rỗng hoặc sai kiểu.')
    if len(blob) > MAX_UPLOAD:
        _bad('File Excel vượt 2 MiB.', limit=True)
    members, total = {}, 0
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        infos = archive.infolist()
        if len(infos) > 128:
            _bad('File Excel có quá nhiều thành phần.', limit=True)
        seen = set()
        for info in infos:
            name = info.filename
            if (not name or name.startswith('/') or '\\' in name or ':' in name or
                    any(p in ('', '.', '..') for p in name.split('/')) or name.casefold() in seen):
                _bad('Đường dẫn hoặc thành phần ZIP trùng không hợp lệ.')
            seen.add(name.casefold())
            if info.flag_bits & 1 or info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                _bad('Không hỗ trợ file mã hóa hoặc kiểu nén này.')
            if info.file_size > MAX_MEMBER:
                _bad('Thành phần Excel vượt 4 MiB.', limit=True)
            chunks, size = [], 0
            with archive.open(info) as source:
                while True:
                    chunk = source.read(65536)
                    if not chunk:
                        break
                    size += len(chunk)
                    total += len(chunk)
                    if size > MAX_MEMBER or total > MAX_TOTAL or size > max(1, info.compress_size) * 100:
                        _bad('Dữ liệu giải nén Excel vượt giới hạn.', limit=True)
                    chunks.append(chunk)
            members[name] = b''.join(chunks)
        required = {'[Content_Types].xml', '_rels/.rels', 'xl/workbook.xml', 'xl/_rels/workbook.xml.rels'}
        if not required.issubset(members):
            _bad('Không phải workbook XLSX được hỗ trợ.')
        roots = {}
        for name, data in members.items():
            if not (name.endswith('.xml') or name.endswith('.rels')):
                _bad('Workbook chứa thành phần không được hỗ trợ.')
            if name.startswith('xl/worksheets/') and name.endswith('.xml'):
                roots[name] = None  # Worksheet XML is streamed below before library loading.
            else:
                roots[name] = _xml(data)
        for item in roots['[Content_Types].xml']:
            content = item.get('ContentType', '')
            if any(part in content.lower() for part in ('macro', 'vba', 'activex', 'oleobject', 'externallink')):
                _bad('Không hỗ trợ macro, đối tượng hoặc liên kết ngoài.')
        for name, root in roots.items():
            if not name.endswith('.rels'):
                continue
            source_dir = posixpath.dirname(posixpath.dirname(name)) if name != '_rels/.rels' else ''
            ids = set()
            for link in root:
                kind, target, identifier = link.get('Type', ''), link.get('Target', ''), link.get('Id')
                if (_tag(link) != 'Relationship' or not identifier or identifier in ids or
                        link.get('TargetMode', 'Internal') != 'Internal' or not target or
                        '\\' in target or ':' in target or '#' in target or '?' in target):
                    _bad('Quan hệ workbook không được hỗ trợ.')
                ids.add(identifier)
                suffix = kind.rsplit('/', 1)[-1]
                if suffix not in ALLOWED_RELS or not kind.startswith('http://schemas.openxmlformats.org/'):
                    _bad('Workbook chứa quan hệ không được hỗ trợ.')
                resolved = posixpath.normpath(target.lstrip('/') if target.startswith('/') else posixpath.join(source_dir, target))
                if resolved.startswith('../') or resolved not in members:
                    _bad('Đích quan hệ workbook không hợp lệ.')
        book = roots['xl/workbook.xml']
        sheets = book.find('{'+MAIN+'}sheets')
        if sheets is None or not 1 <= len(sheets) <= 10:
            _bad('Workbook phải có 1 đến 10 trang tính.', limit=True)
        names = set()
        relationships = {r.get('Id'): r for r in roots['xl/_rels/workbook.xml.rels']}
        sheet_paths = {}
        for sheet in sheets:
            name = sheet.get('name', '')
            if not name or len(name) > 31 or any(ord(c) < 32 for c in name) or name.casefold() in names:
                _bad('Tên trang tính không hợp lệ.')
            names.add(name.casefold())
            link = relationships.get(sheet.get('{'+OFFICE_REL.rstrip('/')+'}id'))
            if link is None or link.get('Type') != OFFICE_REL+'worksheet':
                _bad('Trang tính không có quan hệ hợp lệ.')
            target = link.get('Target')
            path = posixpath.normpath(target.lstrip('/') if target.startswith('/') else posixpath.join('xl', target))
            if path in sheet_paths:
                _bad('Nhiều trang tính cùng tham chiếu một nguồn XML.')
            sheet_paths[path] = name
        for path, root in roots.items():
            if path in sheet_paths or (path.startswith('xl/worksheets/') and path.endswith('.xml')):
                sheet_name = sheet_paths.get(path)
                if sheet_name is None:
                    _bad('Thành phần trang tính không được hỗ trợ.')
                coords, physical_rows = set(), set()
                current_row = None
                events = safe_xml.iterparse(io.BytesIO(members[path]), events=('start', 'end'),
                                           forbid_dtd=True, forbid_entities=True, forbid_external=True)
                first = True
                for event, elem in events:
                    tag = _tag(elem)
                    if first:
                        if elem.tag != '{'+MAIN+'}worksheet':
                            _bad('XML trang tính không hợp lệ.', sheet=sheet_name)
                        first = False
                    if event == 'start':
                        if tag == 'row':
                            value = elem.get('r', '')
                            if not value.isdigit() or not 1 <= int(value) <= 2000:
                                _bad('Dòng vật lý vượt giới hạn.', sheet=sheet_name, limit=True)
                            current_row = int(value)
                            if current_row in physical_rows:
                                _bad('Dòng vật lý bị trùng.', sheet=sheet_name, row=current_row)
                            physical_rows.add(current_row)
                        continue
                    if tag == 'row':
                        current_row = None
                        elem.clear()
                    elif tag == 'c':
                        row, column = _coord(elem.get('r'))
                        if row != current_row:
                            _bad('Ô không khớp dòng vật lý.', sheet_name, row, column)
                        if (row, column) in coords:
                            _bad('Tọa độ ô bị trùng.', sheet_name, row, column)
                        coords.add((row, column))
                        if len(''.join(elem.itertext())) > 1000:
                            _bad('Nội dung ô vượt 1000 ký tự.', sheet_name, row, column, True)
                        elem.clear()
                    elif tag == 'mergeCell':
                        points = elem.get('ref', '').split(':')
                        if len(points) not in (1, 2):
                            _bad('Vùng ô gộp không hợp lệ.', sheet=sheet_name)
                        for point in points:
                            _coord(point)
                    elif tag in ('drawing', 'legacyDrawing', 'oleObjects', 'extLst', 'tableParts'):
                        _bad('Trang tính chứa cấu trúc không được hỗ trợ.', sheet=sheet_name)
            if path == 'xl/sharedStrings.xml':
                for elem in root:
                    if len(''.join(elem.itertext())) > 1000:
                        _bad('Chuỗi Excel vượt 1000 ký tự.', limit=True)
        # Inspect the already bounded XML tree, independent of untrusted dimensions.
        for path in sheet_paths:
            if path not in roots:
                _bad('Thiếu XML trang tính.')
    return members


def _workbook(blob):
    library = _library()
    try:
        _preflight(blob)
        return library.load_workbook(io.BytesIO(blob), read_only=False, data_only=False, keep_links=False)
    except PersonnelXlsxError:
        raise
    except (ValueError, KeyError, OSError, EOFError, ParseError, DefusedXmlException, zipfile.BadZipFile, NotImplementedError, TypeError, OverflowError) as error:
        raise PersonnelXlsxError('INVALID_INPUT', 'File Excel hỏng hoặc có cấu trúc không được hỗ trợ.') from error


def _display(cell):
    value = cell.value
    if value is None:
        return ''
    result = str(value)
    if len(result) > 1000:
        _bad('Nội dung ô vượt 1000 ký tự.', cell.parent.title, cell.row, cell.column, True)
    return result


def inspect_workbook(blob):
    workbook = _workbook(blob)
    try:
        return {'sheets': [{'name': sheet.title, 'sample': [
            {'row': row, 'cells': [{'column': col, 'value': _display(sheet.cell(row, col))}
                                   for col in range(1, min(20, sheet.max_column)+1) if sheet.cell(row, col).value is not None]}
            for row in range(1, min(20, sheet.max_row)+1)]} for sheet in workbook]}
    finally:
        workbook.close()


def _normalize(value):
    return unicodedata.normalize('NFC', value.strip())


def _header(value):
    return ' '.join(_normalize(value).split()).casefold() if isinstance(value, str) else ''


def _fold(value):
    return ''.join(c for c in unicodedata.normalize('NFD', value.casefold()) if not unicodedata.combining(c))


def _near(left, right):
    """Only combining-mark equivalence is a warning under the locked contract."""
    return _fold(left) == _fold(right)


def build_plan(blob, sheet, header_row, columns, excluded_rows, existing_names):
    workbook = _workbook(blob)
    try:
        if not isinstance(sheet, str) or sheet not in workbook.sheetnames:
            _bad('Hãy chọn trang tính hợp lệ.')
        if type(header_row) is not int or not 1 <= header_row <= 2000:
            _bad('Hàng tiêu đề không hợp lệ.', sheet)
        if (not isinstance(columns, dict) or set(columns) != set(ALIASES) or type(columns.get('name')) is not int or
                any(v is not None and (type(v) is not int or not 1 <= v <= 64) for v in columns.values())):
            _bad('Ánh xạ cột không hợp lệ.', sheet)
        mapped = [v for v in columns.values() if v is not None]
        if len(set(mapped)) != len(mapped):
            _bad('Mỗi trường phải chọn một cột riêng.', sheet)
        if (not isinstance(excluded_rows, list) or len(excluded_rows) > 500 or
                any(type(r) is not int or not header_row < r <= 2000 for r in excluded_rows) or
                len(set(excluded_rows)) != len(excluded_rows)):
            _bad('Danh sách dòng loại không hợp lệ.', sheet)
        ws = workbook[sheet]
        for key, col in columns.items():
            if col is not None and _header(ws.cell(header_row, col).value) not in ALIASES[key]:
                _bad('Tiêu đề cột không thuộc bảng nhân sự được hỗ trợ.', sheet, header_row, col)
        if len(mapped) < 2:
            _bad('Cần cột tên và ít nhất một cột mã/chức danh/nhóm nhân sự.', sheet, header_row)
        for merged in ws.merged_cells.ranges:
            if merged.max_row >= header_row and merged.min_col <= max(mapped) and merged.max_col >= min(mapped):
                _bad('Không hỗ trợ ô gộp trong vùng bảng đã chọn.', sheet, merged.min_row, merged.min_col)
        rows = []
        existing = {_normalize(name).casefold(): name for name in existing_names}
        for rownum in range(header_row+1, min(2000, ws.max_row)+1):
            cells = {key: ws.cell(rownum, col) for key, col in columns.items() if col is not None}
            for cell in cells.values():
                if cell.data_type == 'f':
                    _bad('Không hỗ trợ công thức tại cột đã ánh xạ, kể cả dòng loại.', sheet, rownum, cell.column)
            if all(cell.value is None or (isinstance(cell.value, str) and not cell.value.strip()) for cell in cells.values()):
                continue
            result = dict(row=rownum, name=None, code=None, title=None, group=None, status='NEW', messages=[])
            for key, cell in cells.items():
                if isinstance(cell.value, str):
                    result[key] = _normalize(cell.value)
                elif cell.value is not None:
                    result['messages'].append('Cột '+key+' phải là văn bản (cột '+str(cell.column)+').')
            name = result['name']
            if (not name or len(name) > 120 or name.startswith('#') or ';' in name or
                    len(name.splitlines()) != 1 or any(ord(c) < 32 for c in name)):
                result['messages'].append('Tên trống, quá dài hoặc chứa ký tự không hợp lệ.')
            if columns['code'] is not None and not result['code']:
                result['messages'].append('Mã nhân viên phải là văn bản không rỗng; không suy đoán số 0 đầu.')
            if result['messages']:
                result['status'] = 'ERROR'
            if rownum in excluded_rows:
                result['status'] = 'EXCLUDED'
            rows.append(result)
        if len(rows) > 500:
            _bad('Bảng có quá 500 dòng dữ liệu.', sheet, limit=True)
        if set(excluded_rows) - {r['row'] for r in rows}:
            _bad('Dòng loại không có dữ liệu ánh xạ.', sheet)
        included = [r for r in rows if r['status'] != 'EXCLUDED']
        names, codes = {}, {}
        for row in included:
            if row['name']:
                names.setdefault(row['name'].casefold(), []).append(row)
            if row['code']:
                codes.setdefault(row['code'].casefold(), []).append(row)
        for group in names.values():
            if len(group) > 1:
                for row in group:
                    row['status'] = 'ERROR'
                    row['messages'].append('Tên bị trùng trong các dòng đang chọn.')
        for group in codes.values():
            if len({r['name'].casefold() for r in group if r['name']}) > 1:
                for row in group:
                    row['status'] = 'ERROR'
                    row['messages'].append('Cùng mã nhân viên có nhiều tên.')
        new_names = []
        for row in included:
            if row['status'] == 'ERROR':
                continue
            key = row['name'].casefold()
            if key in existing:
                row['status'], row['name'] = 'EXISTING', existing[key]
            else:
                near = any(_near(row['name'], name) for name in existing_names)
                if near:
                    row['messages'].append('Tên gần giống danh mục; chỉ đối chiếu tên chính xác, không tự gộp.')
                new_names.append(row['name'])
        if len(existing) + len(new_names) > 500:
            _bad('Danh mục sau nhập vượt 500 người.', sheet, limit=True)
        counts = {key: sum(r['status'] == key.upper() for r in rows) for key in ('new', 'existing', 'error', 'excluded')}
        return dict(sheet=sheet, headerRow=header_row, columns=dict(columns), counts=counts, rows=rows,
                    canConfirm=bool(new_names) and not counts['error'], newNames=new_names)
    finally:
        workbook.close()
