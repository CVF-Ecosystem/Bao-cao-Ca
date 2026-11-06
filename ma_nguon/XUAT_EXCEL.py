# -*- coding: utf-8 -*-
"""Bộ xuất XLSX của ứng dụng: dùng nguyên kiểu dáng từ mẫu người dùng."""
import copy
import datetime as dt
import io
import math
import re
import textwrap
import xml.etree.ElementTree as E
import zipfile

NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
E.register_namespace('', NS)
E.register_namespace('r', REL)

# Số dòng khuôn trong sheet1 của MAU_BAO_CAO.xlsx. Đổi bố cục file mẫu thì phải chỉnh các số này;
# thiếu dòng khuôn thì Template báo lỗi rõ thay vì xuất sai bố cục.
HEADER_ROWS = 8
HEADER_MERGES = ['A1:H1', 'A2:H2', 'B5:H5', 'A7:H7', 'A8:D8', 'E8:H8']
STAFF_FIRST, STAFF_MIDDLE, STAFF_LAST = 9, 10, 20
STAFF_GAP, JOB_TITLE, JOB_HEADER = 21, 22, 23
JOB_FIRST, JOB_MIDDLE, JOB_LAST, JOB_TOTAL = 24, 25, 33, 34
NOTE_GAP, NOTE_TITLE = 35, 36
NOTE_FIRST, NOTE_MIDDLE, NOTE_LAST = 37, 38, 39
FOOTER_GAP, FOOTER = 40, 41
REQUIRED_TEMPLATE_ROWS = tuple(range(1, FOOTER + 1))


class TemplateError(ValueError):
    """File mẫu báo cáo thiếu hoặc sai bố cục khuôn."""


def tag(name):
    return '{' + NS + '}' + name


def text_value(cell, shared):
    if cell.get('t') == 's':
        value = cell.find(tag('v'))
        return shared[int(value.text)] if value is not None else ''
    if cell.get('t') == 'inlineStr':
        return ''.join(cell.find(tag('is')).itertext())
    value = cell.find(tag('v'))
    return value.text if value is not None else ''


def line_count(value, width):
    return sum(max(1, len(textwrap.wrap(line, width=max(1, width), break_long_words=True)))
               for line in str(value or '').split('\n'))


class Template:
    def __init__(self, path):
        with zipfile.ZipFile(path) as z:
            self.source = E.fromstring(z.read('xl/worksheets/sheet1.xml'))
            self.styles_raw = z.read('xl/styles.xml')
            self.theme = z.read('xl/theme/theme1.xml') if 'xl/theme/theme1.xml' in z.namelist() else None
            self.shared = []
            if 'xl/sharedStrings.xml' in z.namelist():
                self.shared = [''.join(si.itertext()) for si in E.fromstring(z.read('xl/sharedStrings.xml')).findall(tag('si'))]
        self.rows = {int(r.get('r')): r for r in self.source.find(tag('sheetData'))}
        missing = [n for n in REQUIRED_TEMPLATE_ROWS if n not in self.rows]
        if missing:
            raise TemplateError('MAU_BAO_CAO.xlsx thiếu dòng khuôn số ' + ', '.join(map(str, missing))
                                + '. Dùng lại file mẫu gốc hoặc chỉnh các hằng số trong XUAT_EXCEL.py.')
        self.style_root = E.fromstring(self.styles_raw)
        self.wrap_styles = {}
        self.base_style_count = len(self.style_root.find(tag('cellXfs')))

    def wrap_style(self, sid):
        sid = int(sid)
        if sid not in self.wrap_styles:
            xfs = self.style_root.find(tag('cellXfs'))
            xf = copy.deepcopy(xfs[sid])
            alignment = xf.find(tag('alignment'))
            if alignment is None:
                alignment = E.SubElement(xf, tag('alignment'))
            alignment.set('wrapText', '1')
            alignment.set('vertical', 'center')
            xf.set('applyAlignment', '1')
            self.wrap_styles[sid] = len(xfs)
            xfs.append(xf)
            xfs.set('count', str(len(xfs)))
        return str(self.wrap_styles[sid])

    def styles_bytes(self):
        # Keep original namespace declarations (including mc:Ignorable prefixes).
        raw = self.styles_raw.decode('utf-8')
        additions = list(self.style_root.find(tag('cellXfs')))[self.base_style_count:]
        if not additions:
            return self.styles_raw
        # New XF fragments use only the spreadsheet namespace inherited at root.
        fragments = ''.join(E.tostring(x, encoding='unicode') for x in additions)
        fragments = fragments.replace(' xmlns="' + NS + '"', '')
        raw = raw.replace('</cellXfs>', fragments + '</cellXfs>')
        count = len(self.style_root.find(tag('cellXfs')))
        raw = re.sub(r'<cellXfs count="\d+"', '<cellXfs count="' + str(count) + '"', raw, count=1)
        return raw.encode('utf-8')

    def row(self, source_number, number, values=None, height=None):
        row = copy.deepcopy(self.rows[source_number])
        row.set('r', str(number))
        for c in row.findall(tag('c')):
            c.set('r', re.sub(r'\d+$', str(number), c.get('r')))
            if c.get('t') == 's':
                self.cell(row, re.sub(r'\d+$', '', c.get('r')), text_value(c, self.shared))
        if values is not None:
            for c in row.findall(tag('c')):
                for child in list(c):
                    c.remove(child)
                c.attrib.pop('t', None)
            for col, value in values.items():
                self.cell(row, col, value)
        if height is not None:
            row.set('ht', str(min(409, max(20.1, height))))
            row.set('customHeight', '1')
        return row

    def cell(self, row, col, value, formula=None):
        ref = col + row.get('r')
        c = next((c for c in row if c.get('r') == ref), None)
        if c is None:
            c = E.SubElement(row, tag('c'), {'r': ref, 's': '1'})
        for child in list(c):
            c.remove(child)
        c.attrib.pop('t', None)
        if value is None:
            return c
        if formula:
            E.SubElement(c, tag('f')).text = formula
            E.SubElement(c, tag('v')).text = str(value)
        elif isinstance(value, (int, float)):
            E.SubElement(c, tag('v')).text = str(value)
        else:
            c.set('t', 'inlineStr')
            inline = E.SubElement(c, tag('is'))
            E.SubElement(inline, tag('t'), {'{http://www.w3.org/XML/1998/namespace}space': 'preserve'}).text = str(value)
            c.set('s', self.wrap_style(c.get('s', '1')))
        return c

    def report(self, report):
        root = E.Element(tag('worksheet'))
        for name in ('sheetPr', 'sheetViews', 'sheetFormatPr', 'cols'):
            source = self.source.find(tag(name))
            if source is not None:
                element = copy.deepcopy(source)
                if name == 'sheetViews':
                    for view in element:
                        view.attrib.pop('tabSelected', None)
                        for child in list(view):
                            view.remove(child)
                root.append(element)
        props=root.find(tag('sheetPr'))
        if props is not None:E.SubElement(props,tag('pageSetUpPr'),{'fitToPage':'1'})
        data = E.SubElement(root, tag('sheetData'))
        merges = []
        for n in range(1, HEADER_ROWS + 1):
            data.append(self.row(n, n))
        merges.extend(HEADER_MERGES)
        row4 = data[3]
        self.cell(row4, 'B', (dt.date.fromisoformat(report['date'])-dt.date(1899,12,30)).days)
        self.cell(row4, 'D', 'Ngày (06:00–18:00)' if report['shift']=='DAY' else 'Đêm (18:00–06:00 hôm sau)')
        self.cell(row4, 'F', 'Đã chốt' if report['status']=='closed' else 'Nháp')
        self.cell(row4, 'H', report['actor'])
        row4.set('ht', str(max(21.95, line_count(report['actor'], 17)*13+8,
                               line_count('Đêm (18:00–06:00 hôm sau)' if report['shift']=='NIGHT' else 'Ngày (06:00–18:00)', 25)*13+8)))
        allships = list(report.get('ships', []))
        for row in report['staffing'] + report['jobs']:
            allships.extend(row.get('ships', []))
        allships = list(dict.fromkeys(allships))
        updated = report['updated_at'].replace('T', ' ').replace('+07:00', '')
        if allships:
            updated += '\nTàu trong ca: ' + '; '.join(allships)
        self.cell(data[4], 'B', updated)
        data[4].set('ht', str(max(21.95, line_count(updated, 118)*13+8)))
        staffing = report['staffing'] or [{'role':'', 'people':''}]
        number = HEADER_ROWS + 1
        for i, staff in enumerate(staffing):
            label = staff['role']
            if staff.get('ships'):
                label += '\nTàu: ' + '; '.join(staff['ships'])
            h = max(20.1, max(line_count(label, 75), line_count(staff['people'], 48))*13+7)
            src = STAFF_FIRST if i==0 else STAFF_LAST if i==len(staffing)-1 else STAFF_MIDDLE
            data.append(self.row(src, number, {'A':label, 'E':staff['people']}, h))
            merges.extend([f'A{number}:D{number}', f'E{number}:H{number}'])
            number += 1
        data.append(self.row(STAFF_GAP, number, {})); number += 1
        data.append(self.row(JOB_TITLE, number)); merges.append(f'A{number}:H{number}'); number += 1
        data.append(self.row(JOB_HEADER, number)); number += 1
        start = number
        jobs = report['jobs'] or [dict(name='',detail='',xn=False,rtg=False,f20=None,f40=None,e20=None,e40=None)]
        for i,j in enumerate(jobs):
            detail = '\n'.join(filter(None, ['; '.join(j.get('ships', [])), j['detail']]))
            values = {'A':j['name'], 'B':detail, 'C':'X' if j['xn'] else '', 'D':'X' if j['rtg'] else '',
                      **{col:j[key] for col,key in zip('EFGH',['f20','f40','e20','e40'])}}
            height = max(21, max(line_count(j['name'],24),line_count(detail,30))*13+7)
            data.append(self.row(JOB_FIRST if i==0 else JOB_LAST if i==len(jobs)-1 else JOB_MIDDLE, number, values, height))
            number += 1
        total = self.row(JOB_TOTAL, number)
        for col,key in zip('EFGH',['f20','f40','e20','e40']):
            self.cell(total, col, sum(j[key] or 0 for j in jobs), f'SUM({col}{start}:{col}{number-1})')
        data.append(total); number += 1
        data.append(self.row(NOTE_GAP, number, {})); number += 1
        data.append(self.row(NOTE_TITLE, number)); merges.append(f'A{number}:H{number}'); number += 1
        notes = '\n'.join(filter(None, [report['notes'], *[('[Đã xử lý] ' if t['done'] else '[Chưa xử lý] ')+t['text'] for t in report['handover']]]))
        nlines = line_count(notes, 137)
        note_rows = max(3, math.ceil(nlines/20))
        first_note = number
        for i in range(note_rows):
            src = NOTE_FIRST if i==0 else NOTE_LAST if i==note_rows-1 else NOTE_MIDDLE
            data.append(self.row(src, number, {'A':notes} if i==0 else {}, max(15,(nlines*13+10)/note_rows)))
            number += 1
        merges.append(f'A{first_note}:H{number-1}')
        if report.get('attachments'):
            data.append(self.row(NOTE_TITLE,number,{'A':'TỆP ĐÍNH KÈM'}));merges.append(f'A{number}:H{number}');number+=1
            for a in report['attachments']:
                text = a['name'] + (' — '+a.get('caption','') if a.get('caption') else '')
                data.append(self.row(NOTE_FIRST,number,{'A':text},max(21,line_count(text,137)*13+8)))
                merges.append(f'A{number}:H{number}');number+=1
        data.append(self.row(FOOTER_GAP,number,{}));number+=1
        data.append(self.row(FOOTER,number));merges.append(f'B{number}:H{number}')
        # Cells are emitted in column order after adding any new anchor.
        for row in data:
            row[:] = sorted(row, key=lambda c:(len(re.sub(r'\d','',c.get('r',''))),re.sub(r'\d','',c.get('r',''))))
        merged = E.SubElement(root,tag('mergeCells'),{'count':str(len(merges))})
        for ref in merges:E.SubElement(merged,tag('mergeCell'),{'ref':ref})
        margins=self.source.find(tag('pageMargins'))
        if margins is not None:root.append(copy.deepcopy(margins))
        E.SubElement(root,tag('pageSetup'),{'paperSize':'9','orientation':'landscape','fitToWidth':'1','fitToHeight':'0'})
        return E.tostring(root,encoding='utf-8',xml_declaration=True), number

    def summary(self, xml):
        root=E.fromstring(xml)
        for view in root.findall(tag('sheetViews')+'/'+tag('sheetView')):
            view.set('showGridLines','0')
        widths=[14,27,22,36,52,11,11,11,11,13,20]
        cols=root.find(tag('cols'))
        for c in list(cols):cols.remove(c)
        for i,w in enumerate(widths,1):E.SubElement(cols,tag('col'),{'min':str(i),'max':str(i),'width':str(w),'customWidth':'1'})
        data=root.find(tag('sheetData'))
        merges=[]
        monthly=text_value(data[0][0],[]).startswith('BÁO CÁO THÁNG')
        in_jobs=False
        for row in data:
            values={re.sub(r'\d','',c.get('r')):text_value(c,[]) for c in row}
            first=values.get('A','')
            header=first in ('Công việc','Ngày','Ngày báo cáo')
            if monthly:
                if first=='Công việc':in_jobs=True
                elif not first:in_jobs=False
                if row.get('r')=='1':
                    merges.append('A1:K1')
                    for col in 'BCDEFGHIJK':self.cell(row,col,None)
                elif in_jobs:merges.append('A'+row.get('r')+':E'+row.get('r'))
                elif first=='Lưu ý':merges.append('B'+row.get('r')+':K'+row.get('r'))
            lines=1
            for cell in row:
                cell.set('s',self.wrap_style('25' if row.get('r')=='1' else '9' if header else '49' if first=='Lưu ý' else '1'))
                label=re.sub(r'\d','',cell.get('r'))
                index=0
                for char in label:index=index*26+ord(char)-64
                width=int(widths[min(index-1,len(widths)-1)])
                if monthly and ((index==1 and (in_jobs or row.get('r')=='1')) or (index==2 and first=='Lưu ý')):width=140
                lines=max(lines,line_count(text_value(cell,[]),width))
            row.set('ht',str(min(409,max(34 if row.get('r')=='1' else 24,lines*13+8))))
        if merges:
            merged=E.Element(tag('mergeCells'),{'count':str(len(merges))})
            for ref in merges:E.SubElement(merged,tag('mergeCell'),{'ref':ref})
            root.insert(list(root).index(data)+1,merged)
        return E.tostring(root,encoding='utf-8',xml_declaration=True),len(data)


def export_workbook(tables, reports, template_path, generic_export):
    template=Template(template_path)
    skeleton=generic_export(tables)
    out=io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(skeleton)) as source, zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as target:
        extents=[]
        for i,(name,_) in enumerate(tables,1):
            xml,last=(template.report(reports[name]) if name in reports else template.summary(source.read(f'xl/worksheets/sheet{i}.xml')))
            target.writestr(f'xl/worksheets/sheet{i}.xml',xml)
            extents.append((name,last))
        for path in source.namelist():
            if path.startswith('xl/worksheets/') or path=='xl/styles.xml':continue
            content=source.read(path)
            if path=='xl/workbook.xml':
                root=E.fromstring(content)
                defs=E.SubElement(root,tag('definedNames'))
                for i,(name,last) in enumerate(extents):
                    d=E.SubElement(defs,tag('definedName'),{'name':'_xlnm.Print_Area','localSheetId':str(i)})
                    d.text="'"+name.replace("'","''")+"'!$A$1:$"+('H' if name in reports else 'K')+'$'+str(last)
                E.SubElement(root,tag('calcPr'),{'fullCalcOnLoad':'1'})
                content=E.tostring(root,encoding='utf-8',xml_declaration=True)
            elif template.theme and path=='[Content_Types].xml':
                content=content.replace(b'</Types>',b'<Override PartName="/xl/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/></Types>')
            elif template.theme and path=='xl/_rels/workbook.xml.rels':
                content=content.replace(b'</Relationships>',b'<Relationship Id="reportTheme" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/></Relationships>')
            target.writestr(path,content)
        target.writestr('xl/styles.xml',template.styles_bytes())
        if template.theme:target.writestr('xl/theme/theme1.xml',template.theme)
    return out.getvalue()
