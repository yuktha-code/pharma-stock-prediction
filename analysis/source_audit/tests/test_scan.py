"""Synthetic fixtures; no actual research data bundled or fabricated results."""
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from analysis.source_audit.scan import (
    audit_archive, normalize, discover_header, grade, preview_workbook, main
)


class ArchiveAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.dir=Path(self.tmp.name)
        self.zip=self.dir/"test_sources.zip"

    def tearDown(self):
        self.tmp.cleanup()

    def write_zip(self, files):
        with zipfile.ZipFile(self.zip,"w",compression=zipfile.ZIP_DEFLATED) as z:
            for k,v in files.items():
                z.writestr(k,v)

    def test_identifies_candidate_company_quarter_target_without_filing_proof(self):
        data="ticker,quarter,roe,target_label\nA,2025-03-31,0.2,1\n"
        self.write_zip({"panel_master.csv":data})
        result=audit_archive(self.zip)
        self.assertEqual(result["records_inspected"],1)
        c=result["priority_candidates"][0]
        self.assertEqual(c["classification"],"candidate_labelled_panel_missing_proof")
        self.assertIn("FISCAL_PERIOD_IS_NOT_FILING_PUBLICATION_DATE",c["issues"])
        self.assertFalse(result["is_empirical_thesis_result"])

    def test_header_only_candidate_does_not_certify_availability(self):
        s="company,prediction_asof,target_label,published_at,label_available_at,revenue\nA,2024-01-01,0,2023-12-31,2024-04-01,4\n"
        self.write_zip({"actual-looking.csv":s})
        result=audit_archive(self.zip)
        c=result["priority_candidates"][0]
        self.assertEqual(c["classification"],"candidate_point_in_time_panel_schema_only")
        self.assertIn("COLUMN_NAMES_DO_NOT_PROVE_VALID_RELEASE_TIMES_OR_CORPORATE_ACTIONS",c["issues"])
        self.assertFalse(result["is_source_verification"])

    def test_excel_first_twelve_rows_scanned(self):
        from openpyxl import Workbook
        wb=Workbook()
        ws=wb.active
        ws.title="Financial Model"
        ws.append(["company","quarter","net income","revenue"])
        ws.append(["X","2024-03-31",10,100])
        stream=io.BytesIO()
        wb.save(stream)
        self.write_zip({"company_financials.xlsx":stream.getvalue()})
        result=audit_archive(self.zip)
        self.assertEqual(result["records_inspected"],1)
        c=result["priority_candidates"][0]
        self.assertEqual(c["sheet"],"Financial Model")
        self.assertIn("company",c["headers"])
        self.assertIn("revenue",c["headers"])

    def test_nested_zip_recognized(self):
        internal=io.BytesIO()
        with zipfile.ZipFile(internal,"w") as f:
            f.writestr("quarterly_table.csv","symbol,date,adj_close\nX,2025-01-01,10")
        self.write_zip({"work_archive.zip":internal.getvalue()})
        result=audit_archive(self.zip,max_depth=1)
        self.assertEqual(result["records_inspected"],1)
        self.assertIn("::work_archive.zip::",result["priority_candidates"][0]["path"])

    def test_disabled_nested_zip_does_not_parse(self):
        internal=io.BytesIO()
        with zipfile.ZipFile(internal,"w") as f:
            f.writestr("inside.csv","company,asof,value\nX,2025-01-01,10")
        self.write_zip({"nested.zip":internal.getvalue()})
        result=audit_archive(self.zip,max_depth=0)
        self.assertEqual(result["records_inspected"],0)

    def test_member_limit_stops_scan(self):
        self.write_zip({f"c{i}.csv":"ticker,date,close\nA,2025-01-01,2" for i in range(10)})
        result=audit_archive(self.zip,max_members=3)
        self.assertEqual(result["records_inspected"],3)
        self.assertIn("max_members_reached",result["warnings"])

    def test_does_not_scan_non_tables(self):
        self.write_zip({"thesis.pdf":"private paper", "source.txt":"internal", "model.csv":"ticker,year,revenue\nX,2023,4"})
        result=audit_archive(self.zip)
        self.assertEqual(result["records_inspected"],1)
        self.assertEqual(result["by_extension"][".pdf"],1)

    def test_csv_with_utf8_bom(self):
        h=discover_header(b"\xef\xbb\xbfticker,quarter,target_label\nA,2024-Q1,1",".csv")
        self.assertEqual(h[0],"ticker")
        self.assertIn("target_label",h)

    def test_json_records(self):
        self.write_zip({"panel.json":json.dumps([{"ticker":"ABC","date":"2020-01-01","roe":4}])})
        result=audit_archive(self.zip)
        self.assertEqual(result["records_inspected"],1)
        self.assertIn("roe",result["priority_candidates"][0]["headers"])

    def test_no_false_label_from_fiscal_period(self):
        c=grade(["company","fiscal_quarter","revenue","leverage"],"finance.csv")
        self.assertEqual(c["classification"],"candidate_company_time_table")
        self.assertIn("public_release_timestamp_not_recognized",c["issues"])

    def test_invalid_zip_rejected(self):
        self.zip.write_text("invalid",encoding="utf-8")
        with self.assertRaises(ValueError): audit_archive(self.zip)

    def test_cli_creates_private_metadata_report(self):
        self.write_zip({"stock.csv":"company,prediction_asof,price\nA,2023-01-01,50"})
        out=self.dir/"private_audit.json"
        self.assertEqual(main(["--archive",str(self.zip),"--out",str(out)]),0)
        report=json.loads(out.read_text(encoding="utf-8"))
        self.assertNotIn("A,2023-01-01,50",out.read_text())
        self.assertEqual(report["records_inspected"],1)

    def test_normalization(self):
        self.assertEqual(normalize("Adjusted Close"),"adjusted_close")
        self.assertEqual(normalize(" ISIN / Ticker "),"isin_ticker")

    def test_nonexistent_input_rejected(self):
        with self.assertRaises(FileNotFoundError):audit_archive(self.dir/"unknown.zip")


if __name__=="__main__":unittest.main()
