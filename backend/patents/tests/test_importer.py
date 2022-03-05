from io import StringIO
from pathlib import Path

from django.core.management import CommandError, call_command
from django.test import TestCase

from patents.csv_import import CSVFormatError
from patents.importer import dataset_name, import_export
from patents.models import Dataset, Patent

FIXTURE = Path(__file__).parent / "fixtures" / "export.csv"


class ImportExportTests(TestCase):
    def test_creates_dataset_named_after_the_query(self):
        result = import_export(FIXTURE.read_text())

        self.assertEqual(result.dataset.name, "(drone delivery)")
        self.assertEqual(result.imported, 3)
        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.dataset.patents.count(), 3)

    def test_explicit_name_wins(self):
        result = import_export(FIXTURE.read_text(), name="  Drones  ")

        self.assertEqual(result.dataset.name, "Drones")

    def test_duplicate_rows_are_stored_once_with_the_last_values(self):
        text = "id,title\nZZ-1-A1,First title\nZZ-1-A1,Corrected title\n"

        result = import_export(text)

        self.assertEqual(result.imported, 1)
        self.assertEqual(result.duplicates, 1)
        self.assertEqual(Patent.objects.get().title, "Corrected title")

    def test_same_patent_can_appear_in_two_datasets(self):
        import_export(FIXTURE.read_text())
        import_export(FIXTURE.read_text())

        self.assertEqual(Dataset.objects.count(), 2)
        self.assertEqual(Patent.objects.filter(patent_id="ZZ-0000001-B2").count(), 2)

    def test_invalid_file_leaves_no_dataset(self):
        with self.assertRaises(CSVFormatError):
            import_export("name,value\n")

        self.assertFalse(Dataset.objects.exists())

    def test_dataset_name_falls_back_to_the_import_time(self):
        self.assertTrue(dataset_name("").startswith("Import "))
        self.assertEqual(dataset_name("https://patents.google.com/?q=lidar&oq=lidar"), "lidar")


class ImportPatentsCommandTests(TestCase):
    def test_imports_a_file(self):
        out = StringIO()

        call_command("import_patents", str(FIXTURE), "--name", "Drones", stdout=out)

        self.assertIn('Imported 3 patents into dataset', out.getvalue())
        self.assertEqual(Dataset.objects.get().name, "Drones")

    def test_reports_unreadable_and_invalid_files(self):
        with self.assertRaisesMessage(CommandError, "cannot read"):
            call_command("import_patents", "does-not-exist.csv")

        bad = Path(self.id().replace(".", "_") + ".csv")
        bad.write_text("name,value\n")
        self.addCleanup(bad.unlink)
        with self.assertRaisesMessage(CommandError, "is not a Google Patents export"):
            call_command("import_patents", str(bad))
