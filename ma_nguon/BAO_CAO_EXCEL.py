"""Tổng hợp tháng và điều phối xuất báo cáo Excel."""
import calendar
import datetime as dt
import io
import re
import zipfile
from xml.sax.saxutils import escape
from THIET_LAP import ASSETS, KEYS
from NGHIEP_VU import shift_label, AppError, report_ships, chief_people

def aggregate(rows):
    groups = {}
    for r in rows:
        for j in r['jobs']:
            name = j['name'].strip()
            if not name:
                continue
            if name not in groups:
                groups[name] = dict(name=name, **{k: 0 for k in KEYS})
            for k in KEYS:
                groups[name][k] += j[k] or 0
    return list(groups.values())


def monthly_tables(store, month):
    if not isinstance(month, str) or not re.fullmatch(r'\d{4}-\d{2}', month):
        raise AppError('Chọn tháng theo định dạng YYYY-MM.')
    try:
        start = dt.date.fromisoformat(month + '-01')
    except ValueError:
        raise AppError('Tháng không hợp lệ.')
    last = calendar.monthrange(start.year, start.month)[1]
    rows = store.list({'from': start.isoformat(), 'to': month + '-' + str(last)})
    rows.sort(key=lambda r: (r['date'], r['shift'] == 'NIGHT'))
    by_id = {r['id']: r for r in rows}
    summary = [['BÁO CÁO THÁNG ' + month + ' — GỒM NHÁP VÀ ĐÃ CHỐT'],
               ['Số ca đã lưu', len(rows)], ['Đã chốt', sum(r['status']=='closed' for r in rows)],
               ['Nháp', sum(r['status']=='draft' for r in rows)], [],
               ['Công việc', '', '', '', '', 'F20', 'F40', 'E20', 'E40'],
               *[[g['name'], '', '', '', '', *[g[k] for k in KEYS]] for g in aggregate(rows)], [],
               ['Lưu ý', 'Tổng lượt công việc. Một công việc chọn nhiều tàu vẫn chỉ tính số lượng một lần.'], [],
               ['Ngày', 'Ca', 'Trạng thái', 'Phụ trách chung', 'Tàu', 'F20', 'F40', 'E20', 'E40', 'Số tệp', 'Sheet báo cáo']]
    tables = []
    for day in range(1, last+1):
        date = month + f'-{day:02d}'
        for shift in ('DAY', 'NIGHT'):
            r = by_id.get(date+'_'+shift)
            if not r:
                summary.append([date, shift_label(shift), 'Chưa có báo cáo'])
                continue
            name = f'{day:02d}-{start.month:02d}_' + ('Ngay' if shift=='DAY' else 'Dem')
            chief = chief_people(r['staffing'])
            summary.append([date, shift_label(shift), 'Đã chốt' if r['status']=='closed' else 'Nháp', chief,
                            '; '.join(report_ships(r)), *[sum(j[k] or 0 for j in r['jobs']) for k in KEYS],
                            len(r.get('attachments', [])), name])
            tables.append((name, report_table(r)))
    return [('Tong_hop_thang', summary)] + tables


def xlsx_bytes(tables):
    """Small OOXML exporter. Text remains text, including leading '=' and identifiers."""
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        types = ['<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
                 '<Default Extension="xml" ContentType="application/xml"/>',
                 '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
                 '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>']
        sheets, rels = [], []
        for i, (name, rows) in enumerate(tables, 1):
            types.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
            sheets.append(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>')
            rels.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>')
            body = []
            for ri, row in enumerate(rows, 1):
                cells = []
                for ci, v in enumerate(row, 1):
                    col, n = '', ci
                    while n:
                        n, m = divmod(n - 1, 26)
                        col = chr(65 + m) + col
                    ref = f'{col}{ri}'
                    style = '1' if ri == 1 else '0'
                    if v is None:
                        continue
                    if isinstance(v, (int, float)):
                        cells.append(f'<c r="{ref}" s="{style}"><v>{v}</v></c>')
                    else:
                        cells.append(f'<c r="{ref}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{escape(str(v))}</t></is></c>')
                height = max(27, min(150, 18 * max([len(str(v)) // 45 + str(v).count('\n') + 1 for v in row] or [1])))
                body.append(f'<row r="{ri}" ht="{height}" customHeight="1">' + ''.join(cells) + '</row>')
            widths = '<cols><col min="1" max="1" width="36" customWidth="1"/><col min="2" max="2" width="52" customWidth="1"/><col min="3" max="10" width="15" customWidth="1"/></cols>'
            xml = '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"/></sheetViews>' + widths + '<sheetData>' + ''.join(body) + '</sheetData><pageSetup paperSize="9" orientation="landscape" fitToWidth="1" fitToHeight="0"/></worksheet>'
            z.writestr(f'xl/worksheets/sheet{i}.xml', xml)
        z.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' + ''.join(types) + '</Types>')
        z.writestr('_rels/.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr('xl/workbook.xml', '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' + ''.join(sheets) + '</sheets></workbook>')
        rels.append('<Relationship Id="styles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>')
        z.writestr('xl/_rels/workbook.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(rels) + '</Relationships>')
        z.writestr('xl/styles.xml', '''<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="12"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF153E4B"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf></cellXfs></styleSheet>''')
    return out.getvalue()


def styled_xlsx(tables, reports=None):
    from XUAT_EXCEL import export_workbook, TemplateError
    template = ASSETS / 'mau' / 'MAU_BAO_CAO.xlsx'
    if not template.is_file():
        raise AppError('Thiếu MAU_BAO_CAO.xlsx. Chép đủ các file chương trình hoặc đóng gói EXE lại.')
    try:
        return export_workbook(tables, reports or {}, template, xlsx_bytes)
    except TemplateError as exc:
        raise AppError(str(exc)) from exc


def report_table(r):
    return [
        ['BÁO CÁO SẢN XUẤT CUỐI CA', 'BỘ PHẬN BÃI CONTAINER'],
        ['Ngày báo cáo', r['date']], ['Ca', shift_label(r['shift'])],
        ['Tàu trong ca', '; '.join(report_ships(r))],
        ['Trạng thái', 'Đã chốt' if r['status'] == 'closed' else 'Nháp'],
        ['Người nhập / Lưu lần cuối', r['actor'] + ' / ' + r['updated_at']], [],
        ['PHÂN CÔNG NHÂN SỰ', 'NGƯỜI THỰC HIỆN', 'TÀU'],
        *[[s['role'], s['people'], '; '.join(s.get('ships', []))] for s in r['staffing']], [],
        ['CÔNG VIỆC', 'CHI TIẾT / TÀU', 'XN', 'RTG', 'F20', 'F40', 'E20', 'E40'],
        *[[j['name'], '\n'.join(filter(None, ['; '.join(j.get('ships', [])), j['detail']])), 'X' if j['xn'] else '', 'X' if j['rtg'] else '', *[j[k] for k in KEYS]] for j in r['jobs']],
        ['TỔNG LƯỢT DỜI DỌN', '', '', '', *[sum(j[k] or 0 for j in r['jobs']) for k in KEYS]], [],
        ['GHI CHÚ BÀN GIAO', r['notes']],
        *[['Đã xử lý' if t['done'] else 'Chưa xử lý', t['text']] for t in r['handover']],
        [], ['ẢNH / BIÊN BẢN ĐÍNH KÈM', 'CHÚ THÍCH (tệp gốc nằm trong DB)'],
        *[[a['name'], a.get('caption', '')] for a in r.get('attachments', [])],
        [], ['Lưu ý', 'Số lượng là lượt công việc đã báo cáo, không phải số container duy nhất.']]
