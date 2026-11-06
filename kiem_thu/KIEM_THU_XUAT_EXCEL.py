# -*- coding: utf-8 -*-
"""Kiểm tra bố cục khuôn MAU_BAO_CAO.xlsx và vị trí các dòng xuất ra."""
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile

from BAO_CAO_EXCEL import report_table, styled_xlsx
from LUU_TRU import Store
from NGHIEP_VU import AppError
from THIET_LAP import ASSETS
from XUAT_EXCEL import REQUIRED_TEMPLATE_ROWS, Template, TemplateError

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
TEMPLATE = ASSETS / 'MAU_BAO_CAO.xlsx'


def without_row(source, row_number, target):
    """Sao chép file mẫu nhưng xóa một dòng khuôn."""
    with zipfile.ZipFile(source) as z_in, zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z_out:
        for name in z_in.namelist():
            data = z_in.read(name)
            if name == 'xl/worksheets/sheet1.xml':
                root = ET.fromstring(data)
                sheet = root.find('m:sheetData', NS)
                for row in list(sheet):
                    if int(row.get('r')) == row_number:
                        sheet.remove(row)
                ET.register_namespace('', NS['m'])
                data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            z_out.writestr(name, data)


class TemplateLayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_shipped_template_has_every_required_row(self):
        template = Template(TEMPLATE)
        self.assertEqual([n for n in REQUIRED_TEMPLATE_ROWS if n not in template.rows], [])

    def test_template_missing_a_row_is_rejected_clearly(self):
        broken = self.root / 'mau_thieu_dong.xlsx'
        without_row(TEMPLATE, 30, broken)
        with self.assertRaises(TemplateError) as raised:
            Template(broken)
        self.assertIn('30', str(raised.exception))

    def test_missing_row_reaches_the_user_as_app_error(self):
        folder = self.root / 'assets_hong'
        folder.mkdir()
        without_row(TEMPLATE, 25, folder / 'MAU_BAO_CAO.xlsx')
        store = Store(self.root / 'DU_LIEU' / 'BAO_CAO_CA.db')
        report = store.save(self.report(), 0)
        with patch('BAO_CAO_EXCEL.ASSETS', folder), self.assertRaises(AppError) as raised:
            styled_xlsx([('Bao cao ca', report_table(report))], {'Bao cao ca': report})
        self.assertIn('25', str(raised.exception))

    @staticmethod
    def report():
        job = dict(detail='', xn=False, rtg=False, f20=None, f40=None, e20=None, e40=None)
        return dict(date='2026-11-04', shift='DAY', actor='Người kiểm thử', status='draft', notes='ghi chú',
                    staffing=[dict(role='PHỤ TRÁCH CHUNG', people='Trưởng ca'), dict(role='TALLY', people='An')],
                    jobs=[dict(job, name='VIỆC 1', f20=1, f40=2), dict(job, name='VIỆC 2', f20=3, e40=4),
                          dict(job, name='VIỆC 3', f20=5)],
                    handover=[])

    def test_job_rows_and_total_formulas_follow_the_template_layout(self):
        store = Store(self.root / 'DU_LIEU' / 'BAO_CAO_CA.db')
        report = store.save(self.report(), 0)
        data = styled_xlsx([('Bao cao ca', report_table(report))], {'Bao cao ca': report})
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        rows = {int(r.get('r')): r for r in sheet.findall('m:sheetData/m:row', NS)}
        # 8 dòng đầu + 2 dòng nhân sự + dòng trống, tiêu đề, cột = công việc bắt đầu ở dòng 14, tổng ở dòng 17.
        def text(row, col):
            cell = next((c for c in rows[row] if c.get('r') == col + str(row)), None)
            return ''.join(cell.itertext()) if cell is not None else ''
        self.assertEqual(text(14, 'A'), 'VIỆC 1')
        self.assertEqual(text(16, 'A'), 'VIỆC 3')
        formula = rows[17].find("m:c[@r='E17']/m:f", NS)
        self.assertIsNotNone(formula)
        self.assertEqual(formula.text, 'SUM(E14:E16)')
        self.assertEqual(rows[17].find("m:c[@r='E17']/m:v", NS).text, '9')


if __name__ == '__main__':
    unittest.main()
