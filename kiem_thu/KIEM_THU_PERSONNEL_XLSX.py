"""Synthetic contract and adversarial tests for the pure XLSX reader."""
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest
import zipfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ma_nguon'))
from PERSONNEL_XLSX import PersonnelXlsxError, _library, build_plan, inspect_workbook

COLS = dict(name=2, code=1, title=3, group=4)


def fixture(rows=None, extra=False):
    library = _library()
    book = library.Workbook()
    sheet = book.active
    sheet.title = 'Nhân sự'
    sheet.append(['MSCĐ', 'Họ và Tên', 'Chức danh', 'Nhóm/Ca'])
    for row in rows if rows is not None else [['001', 'Người Mới', 'Công nhân', 'Ca 1']]:
        sheet.append(row)
    if extra:
        book.create_sheet('Khác')['A1'] = 'Thông tin'
    output = io.BytesIO()
    book.save(output)
    book.close()
    return output.getvalue()


def rewrite(blob, path, transform):
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(blob)) as source, zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as target:
        for name in source.namelist():
            content = source.read(name)
            target.writestr(name, transform(content) if name == path else content)
    return output.getvalue()


class PersonnelReaderTests(unittest.TestCase):
    def test_three_distinct_observed_report_structures_are_not_personnel_tables(self):
        # Structural-only representatives of the three observed references.
        # Actual hash-bound reference refusal is separately retained in
        # native/report-structure-refusals.json; no source cell values copied.
        profiles = [
            ('Bai cont ca.xlsx', 'N09-9', 27, 9, 1, 0, ['A2:I2', 'A5:H5', 'A22:A23']),
            ('Thu tuc ca.xlsx', 'T10', 581, 6, 6, 151,
             ['A553:B553', 'A560:B560', 'A567:B567', 'A574:B574', 'A581:B581',
              'A511:B511', 'A518:B518', 'A525:B525', 'A532:B532', 'A539:B539',
              'A546:B546', 'A469:B469', 'A476:B476', 'A483:B483', 'A490:B490']),
            ('Dieu hanh ca.xlsx', '10.2025', 77, 7, 4, 0, ['A1:F1', 'A2:F2', 'A3:F3']),
        ]
        for filename, title, last_row, last_col, header, formula_count, merges in profiles:
            with self.subTest(reference=filename):
                book = _library().Workbook()
                sheet = book.active
                sheet.title = title
                sheet.cell(1, 1, 'BÁO CÁO GIẢ LẬP - KHÔNG PHẢI DANH SÁCH NHÂN SỰ')
                sheet.cell(header, 1, 'STT')
                sheet.cell(header, 2, 'CA' if last_col == 7 else 'NỘI DUNG BÁO CÁO')
                sheet.cell(header, last_col, 'GHI CHÚ')
                sheet.cell(last_row, last_col, 'Mốc cuối giả lập')
                for row in range(header+1, last_row):
                    sheet.cell(row, last_col, 'Dữ liệu báo cáo giả lập')
                for row in range(header+1, header+1+formula_count):
                    sheet.cell(row, 4, '=1+1')
                for merge in merges:
                    sheet.merge_cells(merge)
                self.assertEqual((sheet.max_row, sheet.max_column), (last_row, last_col))
                self.assertEqual(sum(cell.data_type == 'f' for row in sheet for cell in row), formula_count)
                output = io.BytesIO()
                book.save(output)
                book.close()
                blob = output.getvalue()
                # Safe inspection may show a bounded sample; it is never admission to import.
                self.assertEqual(inspect_workbook(blob)['sheets'][0]['name'], title)
                with self.assertRaises(PersonnelXlsxError) as caught:
                    build_plan(blob, title, header, dict(name=2, code=1, title=3, group=None), [], [])
                self.assertEqual(caught.exception.code, 'INVALID_INPUT')
                self.assertEqual((caught.exception.sheet, caught.exception.row, caught.exception.column), (title, header, 2))

    def plan(self, blob=None, excluded=None, existing=None):
        return build_plan(blob or fixture(), 'Nhân sự', 1, COLS, excluded or [], existing or [])

    def test_inspect_and_transient_mapping_oracle(self):
        blob = fixture(extra=True)
        result = inspect_workbook(blob)
        self.assertEqual([s['name'] for s in result['sheets']], ['Nhân sự', 'Khác'])
        self.assertEqual(result['sheets'][0]['sample'][1]['cells'][0], {'column': 1, 'value': '001'})
        plan = self.plan(blob)
        self.assertEqual(plan['counts'], dict(new=1, existing=0, error=0, excluded=0))
        self.assertEqual(plan['newNames'], ['Người Mới'])
        self.assertEqual(plan['rows'][0]['code'], '001')
        self.assertTrue(plan['canConfirm'])
        self.assertEqual(self.plan(existing=['NGƯỜI MỚI'])['rows'][0]['name'], 'NGƯỜI MỚI')
        self.assertFalse(self.plan(existing=['NGƯỜI MỚI'])['canConfirm'])

    def test_unicode_duplicates_and_exclusion(self):
        rows = [['001', 'Người Mới', '', ''], ['002', 'Người Mới', '', '']]
        blob = fixture(rows)
        self.assertEqual(self.plan(blob)['counts']['error'], 2)
        result = self.plan(blob, [3])
        self.assertTrue(result['canConfirm'])
        self.assertEqual(result['counts'], dict(new=1, existing=0, error=0, excluded=1))
        self.assertEqual(result['rows'][1]['status'], 'EXCLUDED')

    def test_conflicting_codes_invalid_names_types_and_near_warning(self):
        rows = [['001', 'Alpha', '', ''], ['001', 'Beta', '', ''], [2, 'Gamma', '', ''],
                ['003', 'bad;name', '', ''], ['004', None, 'x', '']]
        self.assertEqual(self.plan(fixture(rows))['counts']['error'], 4)
        for name in ('#comment', 'a\nb', 'x'*121):
            with self.subTest(name=name):
                self.assertEqual(self.plan(fixture([['1', name, '', '']]))['counts']['error'], 1)
        result = self.plan(fixture([['1', 'Nguyen Van A', '', '']]), existing=['Nguyễn Văn A'])
        self.assertEqual(result['counts']['new'], 1)
        self.assertTrue(result['rows'][0]['messages'])

    def test_selected_formula_is_fatal_even_when_excluded(self):
        for col in range(4):
            row = ['1', 'Valid Name', '', '']
            row[col] = '=1+1'
            for excluded in ([], [2]):
                with self.subTest(col=col, excluded=excluded), self.assertRaises(PersonnelXlsxError):
                    self.plan(fixture([row]), excluded)

    def test_report_headers_and_mapping_refused(self):
        blob = rewrite(fixture(), 'xl/worksheets/sheet1.xml', lambda b: b.replace(b'MSC', b'BAD'))
        with self.assertRaises(PersonnelXlsxError):
            self.plan(blob)
        for columns in (dict(name=2, code=2, title=None, group=None), dict(name=2), dict(name=True, code=1, title=3, group=4)):
            with self.subTest(columns=columns), self.assertRaises(PersonnelXlsxError):
                build_plan(fixture(), 'Nhân sự', 1, columns, [], [])
        for excluded in ([9], [2, 2], [True]):
            with self.subTest(excluded=excluded), self.assertRaises(PersonnelXlsxError):
                self.plan(excluded=excluded)

    def test_format_zip_traversal_duplicate_macro_relationship_entities(self):
        for blob in (b'', b'not xlsx', b'PK\x03\x04bad', b'x'*(2*1024*1024+1)):
            with self.subTest(size=len(blob)), self.assertRaises(PersonnelXlsxError):
                inspect_workbook(blob)
        for name in ('../evil.xml', 'xl/../evil.xml', 'XL/WORKBOOK.XML'):
            source = fixture()
            output = io.BytesIO(source)
            with zipfile.ZipFile(output, 'a') as z:
                z.writestr(name, '<root/>')
            with self.subTest(name=name), self.assertRaises(PersonnelXlsxError):
                inspect_workbook(output.getvalue())
        for path, transform in [
            ('[Content_Types].xml', lambda b: b.replace(b'spreadsheetml.sheet.main', b'macroEnabled.main')),
            ('xl/_rels/workbook.xml.rels', lambda b: b.replace(b'Type=', b'TargetMode="External" Type=', 1)),
            ('xl/workbook.xml', lambda b: b'<!DOCTYPE a [<!ENTITY x "xx">]>'+b),
            ('xl/worksheets/sheet1.xml', lambda b: b.replace(b'r="B2"', b'r="BM2"')),
            ('xl/worksheets/sheet1.xml', lambda b: b.replace(b'r="B2"', b'r="A2"')),
            ('xl/worksheets/sheet1.xml', lambda b: b.replace(b'r="2"', b'r="2001"')),
        ]:
            with self.subTest(path=path), self.assertRaises(PersonnelXlsxError):
                inspect_workbook(rewrite(fixture(), path, transform))

    def test_actual_expansion_members_and_cell_limits(self):
        output = io.BytesIO(fixture())
        with zipfile.ZipFile(output, 'a', zipfile.ZIP_DEFLATED) as z:
            z.writestr('huge.xml', 'x'*(4*1024*1024+1))
        with self.assertRaises(PersonnelXlsxError):
            inspect_workbook(output.getvalue())
        output = io.BytesIO(fixture())
        with zipfile.ZipFile(output, 'a', zipfile.ZIP_DEFLATED) as z:
            z.writestr('ratio.xml', '<root>'+'x'*100000+'</root>')
        with self.assertRaises(PersonnelXlsxError):
            inspect_workbook(output.getvalue())
        output = io.BytesIO(fixture())
        with zipfile.ZipFile(output, 'a') as z:
            for i in range(129):
                z.writestr(str(i)+'.xml', '<r/>')
        with self.assertRaises(PersonnelXlsxError):
            inspect_workbook(output.getvalue())
        with self.assertRaises(PersonnelXlsxError):
            inspect_workbook(fixture([['1', 'x'*1001, '', '']]))
        with self.assertRaises(PersonnelXlsxError):
            self.plan(fixture([[str(i), 'Name '+str(i), '', ''] for i in range(501)]))
        with self.assertRaises(PersonnelXlsxError):
            self.plan(existing=['Name '+str(i) for i in range(500)])

    def test_merged_range_and_unselected_sheet_physical_limits(self):
        library = _library()
        book = library.Workbook()
        sheet = book.active
        sheet.title = 'Nhân sự'
        sheet.append(['MSCĐ', 'Họ và Tên', 'Chức danh', 'Nhóm/Ca'])
        sheet.append(['1', 'Good', '', ''])
        sheet.merge_cells('A2:B2')
        output = io.BytesIO()
        book.save(output)
        with self.assertRaises(PersonnelXlsxError):
            self.plan(output.getvalue())
        book.create_sheet('Khác')['A2001'] = 'bad'
        output = io.BytesIO()
        book.save(output)
        book.close()
        with self.assertRaises(PersonnelXlsxError):
            inspect_workbook(output.getvalue())

    def test_parser_provenance_and_unsafe_ambient_fail_closed(self):
        library = _library()
        self.assertFalse(library.LXML)
        self.assertTrue(library.DEFUSEDXML)
        with patch.object(library, 'LXML', True), self.assertRaises(PersonnelXlsxError):
            inspect_workbook(fixture())
        with patch('PERSONNEL_XLSX.version', return_value='bad'), self.assertRaises(PersonnelXlsxError):
            inspect_workbook(b'bad')
        code = "import openpyxl; from PERSONNEL_XLSX import _library; _library()"
        env = dict(os.environ, OPENPYXL_LXML='True', PYTHONPATH=str(Path(__file__).resolve().parents[1]/'ma_nguon'))
        result = subprocess.run([sys.executable, '-B', '-c', code], env=env, capture_output=True, timeout=20)
        # Ambient lxml is optional in the isolated build environment.
        if b'PersonnelXlsxError' in result.stderr:
            self.assertNotEqual(result.returncode, 0)
        else:
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_all_sheet_preflight_finishes_before_library_loader(self):
        library = _library()
        blob = rewrite(fixture(extra=True), 'xl/worksheets/sheet2.xml',
                       lambda b: b.replace(b'r="A1"', b'r="A2001"'))
        with patch.object(library, 'load_workbook') as load, self.assertRaises(PersonnelXlsxError):
            self.plan(blob)
        load.assert_not_called()

    def test_physical_coordinate_boundaries_and_metadata_dimension_ignored(self):
        library = _library()
        book = library.Workbook()
        sheet = book.active
        sheet['BL2000'] = 'boundary'
        output = io.BytesIO()
        book.save(output)
        self.assertEqual(inspect_workbook(output.getvalue())['sheets'][0]['name'], 'Sheet')
        sheet['BM2000'] = 'outside'
        output = io.BytesIO()
        book.save(output)
        book.close()
        with self.assertRaises(PersonnelXlsxError):
            inspect_workbook(output.getvalue())
        blob = rewrite(fixture(), 'xl/worksheets/sheet1.xml',
                       lambda b: b.replace(b'ref="A1:D2"', b'ref="A1:XFD1048576"'))
        self.assertTrue(self.plan(blob)['canConfirm'])

    def test_many_sheets_and_unsafe_merged_metadata(self):
        library = _library()
        book = library.Workbook()
        for index in range(10):
            book.create_sheet('Extra'+str(index))
        output = io.BytesIO()
        book.save(output)
        book.close()
        with self.assertRaises(PersonnelXlsxError):
            inspect_workbook(output.getvalue())
        blob = rewrite(fixture(), 'xl/worksheets/sheet1.xml',
                       lambda b: b.replace(b'</worksheet>', b'<mergeCells><mergeCell ref="A1:XFD1048576"/></mergeCells></worksheet>'))
        with self.assertRaises(PersonnelXlsxError):
            inspect_workbook(blob)

    def test_member_and_total_actual_byte_limits_without_large_library_parse(self):
        library = _library()
        # Lower only test quotas: exercise exact real streaming accounting at each boundary.
        blob = fixture()
        with patch('PERSONNEL_XLSX.MAX_TOTAL', 100), patch.object(library, 'load_workbook') as load, \
                self.assertRaises(PersonnelXlsxError):
            inspect_workbook(blob)
        load.assert_not_called()
        with patch('PERSONNEL_XLSX.MAX_MEMBER', 100), self.assertRaises(PersonnelXlsxError):
            inspect_workbook(blob)

    def test_plain_header_profile_optional_name_only_and_error_locations(self):
        blob = fixture([['001', 'Good', '', ''], ['002', 'Near', '', '']])
        columns = dict(name=2, code=None, title=3, group=None)
        plan = build_plan(blob, 'Nhân sự', 1, columns, [], [])
        self.assertEqual(plan['newNames'], ['Good', 'Near'])
        with self.assertRaises(PersonnelXlsxError) as caught:
            build_plan(blob, 'Nhân sự', 1, dict(name=2, code=None, title=None, group=None), [], [])
        self.assertEqual((caught.exception.sheet, caught.exception.row), ('Nhân sự', 1))

    def test_relationship_target_cannot_bypass_sheet_preflight(self):
        output = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(fixture())) as source, zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as target:
            for name in source.namelist():
                data = source.read(name)
                if name == 'xl/worksheets/sheet1.xml':
                    name = 'custom/sheet.xml'
                    data = data.replace(b'r="2"', b'r="2001"')
                    for column in b'ABCD':
                        data = data.replace(('r="%s2"' % chr(column)).encode(), ('r="%s2001"' % chr(column)).encode())
                elif name in ('[Content_Types].xml', 'xl/_rels/workbook.xml.rels'):
                    data = data.replace(b'/xl/worksheets/sheet1.xml', b'/custom/sheet.xml')
                target.writestr(name, data)
        with patch.object(_library(), 'load_workbook') as load, self.assertRaises(PersonnelXlsxError):
            inspect_workbook(output.getvalue())
        load.assert_not_called()

    def test_line_separators_and_locked_near_name_policy(self):
        for separator in ('\u0085', '\u2028', '\u2029'):
            with self.subTest(separator=repr(separator)):
                plan = self.plan(fixture([['1', 'Alpha'+separator+'Beta', '', '']]))
                self.assertEqual(plan['counts']['error'], 1)
                self.assertFalse(plan['canConfirm'])
        for new, existing in [('Alpha', 'Alphb'), ('Đan', 'Dan')]:
            with self.subTest(new=new):
                plan = self.plan(fixture([['1', new, '', '']]), existing=[existing])
                self.assertEqual(plan['rows'][0]['messages'], [])
        plan = self.plan(fixture([['1', 'Nguyen', '', '']]), existing=['Nguyễn'])
        self.assertTrue(plan['rows'][0]['messages'])

    def test_numeric_codes_and_safe_formats(self):
        book = _library().Workbook(); sheet = book.active; sheet.title = 'Nhân sự'
        sheet.append(['MSCĐ', 'Họ và Tên', 'Chức danh', 'Nhóm/Ca'])
        for value, fmt in [(42, 'General'), (43, '@'), (7, '0000'), (1.5, 'General'), (-1, 'General'), (10, '0.0'), (10**15, 'General')]:
            sheet.append([value, 'Name '+str(sheet.max_row), '', '']); sheet.cell(sheet.max_row, 1).number_format = fmt
        output = io.BytesIO(); book.save(output); book.close()
        plan = self.plan(output.getvalue())
        self.assertEqual(plan['counts']['error'], 4)
        self.assertEqual([r['code'] for r in plan['rows'][:3]], ['42', '43', '0007'])
        self.assertTrue(all(r['messages'] and r['status'] == 'NEW' for r in plan['rows'][:3]))

    def test_bounded_printer_settings_relationship(self):
        def printer(target='../printerSettings/printerSettings1.bin', kind='printerSettings', content='application/vnd.openxmlformats-officedocument.spreadsheetml.printerSettings', name='xl/printerSettings/printerSettings1.bin', data=b'printer'):
            output = io.BytesIO()
            with zipfile.ZipFile(io.BytesIO(fixture())) as source, zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as dest:
                for item in source.infolist():
                    value = source.read(item.filename)
                    if item.filename == '[Content_Types].xml':
                        value = value.replace(b'</Types>', ('<Default Extension="bin" ContentType="'+content+'"/></Types>').encode())
                    dest.writestr(item.filename, value)
                rel = ('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/'+kind+'" Target="'+target+'"/></Relationships>')
                dest.writestr('xl/worksheets/_rels/sheet1.xml.rels', rel)
                dest.writestr(name, data)
            return output.getvalue()
        self.assertTrue(self.plan(printer())['canConfirm'])
        for blob in (printer(kind='styles'), printer(content='application/octet-stream'),
                     printer(name='xl/printerSettings/other.bin'), printer(data=b'x'*65537),
                     printer(target='https://example.invalid/a')):
            with self.subTest(size=len(blob)), self.assertRaises(PersonnelXlsxError):
                inspect_workbook(blob)


if __name__ == '__main__':
    unittest.main()
