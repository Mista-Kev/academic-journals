import csv
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from logic import openalex_three_path_prolog as paths


def article(work_id, date, journal_id, parent_publisher_id, authors):
    return paths.Article(
        work_id=work_id,
        publication_date=date,
        journal_id=journal_id,
        parent_publisher_id=parent_publisher_id,
        author_ids=tuple(authors),
    )


class PathwayEvaluationTests(unittest.TestCase):
    def test_finds_independent_temporal_pathways_for_focal_author_pairs(self):
        articles = [
            article("W1", "2019-01-01", "S1", "P1", ["A1", "A3"]),
            article("W2", "2020-01-01", "S2", "P1", ["A1"]),
            article("W3", "2020-06-01", "S1", "P1", ["A2"]),
            article("W4", "2021-01-01", "S1", "P1", ["A1", "A2"]),
        ]

        results = {
            (row.focal_work_id, row.focal_author_id): row
            for row in paths.evaluate_pathways(articles)
        }

        focal_a1 = results[("W4", "A1")]
        self.assertTrue(focal_a1.journal_path)
        self.assertTrue(focal_a1.publisher_path)
        self.assertTrue(focal_a1.coauthor_path)
        self.assertEqual(["W1"], [e.prior_work_id for e in focal_a1.journal_evidence])
        self.assertEqual(["W2"], [e.prior_work_id for e in focal_a1.publisher_evidence])
        self.assertEqual(["W3"], [e.prior_work_id for e in focal_a1.coauthor_evidence])

        focal_a2 = results[("W4", "A2")]
        self.assertTrue(focal_a2.journal_path)
        self.assertFalse(focal_a2.publisher_path)
        self.assertTrue(focal_a2.coauthor_path)
        self.assertEqual(["A1"], [e.prior_author_id for e in focal_a2.coauthor_evidence])

    def test_requires_strictly_earlier_evidence(self):
        articles = [
            article("W1", "2021-01-01", "S1", "P1", ["A1"]),
            article("W2", "2021-01-01", "S1", "P1", ["A1", "A2"]),
            article("W3", "2021-01-02", "S1", "P1", ["A2"]),
        ]

        results = {
            (row.focal_work_id, row.focal_author_id): row
            for row in paths.evaluate_pathways(articles)
        }

        self.assertFalse(results[("W2", "A1")].journal_path)
        self.assertFalse(results[("W2", "A2")].coauthor_path)
        self.assertTrue(results[("W3", "A2")].journal_path)

    def test_publisher_path_requires_known_same_parent_and_different_journal(self):
        articles = [
            article("W1", "2018-01-01", "S1", "P1", ["A1"]),
            article("W2", "2019-01-01", "S2", "P1", ["A1"]),
            article("W3", "2018-01-01", "S3", None, ["A2"]),
            article("W4", "2019-01-01", "S4", None, ["A2"]),
        ]

        results = {
            (row.focal_work_id, row.focal_author_id): row
            for row in paths.evaluate_pathways(articles)
        }

        self.assertTrue(results[("W2", "A1")].publisher_path)
        self.assertEqual(["S1"], [e.prior_journal_id for e in results[("W2", "A1")].publisher_evidence])
        self.assertFalse(results[("W4", "A2")].publisher_path)

    def test_ignores_missing_author_ids(self):
        articles = [
            article("W1", "2018-01-01", "S1", "P1", [None]),
            article("W2", "2019-01-01", "S1", "P1", ["A1", None]),
        ]

        results = paths.evaluate_pathways(articles)

        self.assertEqual([("W2", "A1")], [(row.focal_work_id, row.focal_author_id) for row in results])
        self.assertFalse(results[0].journal_path)
        self.assertFalse(results[0].coauthor_path)

    def test_filters_focal_years_without_removing_history(self):
        articles = [
            article("W1", "2019-01-01", "S1", "P1", ["A1"]),
            article("W2", "2020-01-01", "S1", "P1", ["A1"]),
        ]

        results = paths.evaluate_pathways(articles, focal_start_year=2020)

        self.assertEqual([("W2", "A1")], [(row.focal_work_id, row.focal_author_id) for row in results])
        self.assertTrue(results[0].journal_path)


class PublisherMappingTests(unittest.TestCase):
    def test_uses_last_lineage_entry_as_normalized_parent(self):
        self.assertEqual(
            "Pparent",
            paths.normalized_parent_publisher_id(
                ["https://openalex.org/Pchild", "https://openalex.org/Pparent"]
            ),
        )
        self.assertIsNone(paths.normalized_parent_publisher_id([]))

    def test_loads_journal_parent_publishers_from_raw_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw_path = Path(tmp) / "raw.jsonl"
            records = [
                {
                    "id": "https://openalex.org/W1",
                    "primary_location": {
                        "source": {
                            "id": "https://openalex.org/S1",
                            "display_name": "Journal 1",
                            "host_organization": "https://openalex.org/Pchild",
                            "host_organization_name": "Child Publisher",
                            "host_organization_lineage": [
                                "https://openalex.org/Pchild",
                                "https://openalex.org/Pparent",
                            ],
                            "host_organization_lineage_names": [
                                "Child Publisher",
                                "Parent Publisher",
                            ],
                        }
                    },
                },
                {
                    "id": "https://openalex.org/W2",
                    "primary_location": {
                        "source": {
                            "id": "https://openalex.org/S2",
                            "display_name": "Journal 2",
                            "host_organization_lineage": [],
                            "host_organization_lineage_names": [],
                        }
                    },
                },
            ]
            raw_path.write_text(
                "\n".join(json.dumps(record) for record in records) + "\n",
                encoding="utf-8",
            )

            mappings = paths.load_journal_parent_publishers(raw_path)

        self.assertEqual("Pparent", mappings["S1"].parent_publisher_id)
        self.assertEqual("Parent Publisher", mappings["S1"].parent_publisher_name)
        self.assertTrue(mappings["S2"].is_unresolved)


class CsvLoadingTests(unittest.TestCase):
    def test_loads_articles_from_semiclean_csv_and_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "works.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["work_id", "publication_date", "journal_id", "authorships_json"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "work_id": "W1",
                        "publication_date": "2020-01-01",
                        "journal_id": "S1",
                        "authorships_json": json.dumps(
                            [{"author_id": "A1"}, {"author_id": None}, {"author_id": "A2"}]
                        ),
                    }
                )

            mappings = {
                "S1": paths.PublisherMapping(
                    journal_id="S1",
                    journal_name="Journal 1",
                    immediate_publisher_id="Pchild",
                    immediate_publisher_name="Child Publisher",
                    parent_publisher_id="Pparent",
                    parent_publisher_name="Parent Publisher",
                    lineage_ids=("Pchild", "Pparent"),
                    lineage_names=("Child Publisher", "Parent Publisher"),
                )
            }

            loaded = paths.load_articles_from_semiclean_csv(csv_path, mappings)

        self.assertEqual(
            [
                article("W1", "2020-01-01", "S1", "Pparent", ["A1", "A2"]),
            ],
            loaded,
        )


class DataPathResolutionTests(unittest.TestCase):
    def test_default_data_dir_falls_back_to_script_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            script_dir = base / "project"
            data_dir = script_dir / "openalex_ai_dataset_v1_0"
            other_cwd = base / "other-cwd"
            data_dir.mkdir(parents=True)
            other_cwd.mkdir()
            (data_dir / paths.RAW_FILENAME).write_text("", encoding="utf-8")

            original_cwd = Path.cwd()
            original_file = paths.__file__
            try:
                os.chdir(other_cwd)
                paths.__file__ = str(script_dir / "openalex_three_path_prolog.py")
                with mock.patch.dict(os.environ, {"OPENALEX_DATA_DIR": ""}):
                    self.assertEqual(data_dir, paths.default_data_dir())
            finally:
                paths.__file__ = original_file
                os.chdir(original_cwd)

    def test_default_output_dir_is_relative_to_script_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            script_dir = Path(tmp) / "project"
            script_dir.mkdir()
            original_file = paths.__file__
            try:
                paths.__file__ = str(script_dir / "openalex_three_path_prolog.py")
                self.assertEqual(
                    script_dir / "openalex_three_path_output",
                    paths.default_output_dir(),
                )
            finally:
                paths.__file__ = original_file


class PrologRenderingTests(unittest.TestCase):
    def test_renders_facts_for_articles_and_focal_pairs(self):
        articles = [article("W1", "2020-01-01", "S1", "P1", ["A1", "A2"])]

        rendered = paths.render_prolog_facts(articles, focal_start_year=2020)

        self.assertIn(":- discontiguous work/4.", rendered)
        self.assertIn(":- discontiguous authorship/2.", rendered)
        self.assertIn("work('W1','2020-01-01','S1','P1').", rendered)
        self.assertIn("authorship('W1','A1').", rendered)
        self.assertIn("focal_pair('W1','A2').", rendered)


class PrologIntegrationTests(unittest.TestCase):
    def test_prolog_flags_match_python_reference(self):
        try:
            paths.find_swipl_executable()
        except FileNotFoundError:
            self.skipTest("SWI-Prolog was not found; set SWIPL_PATH to run this integration test.")

        articles = [
            article("W1", "2019-01-01", "S1", "P1", ["A1", "A3"]),
            article("W2", "2020-01-01", "S2", "P1", ["A1"]),
            article("W3", "2020-06-01", "S1", "P1", ["A2"]),
            article("W4", "2021-01-01", "S1", "P1", ["A1", "A2"]),
            article("W5", "2020-02-01", "S3", "P2", ["A4"]),
        ]
        python_results = paths.evaluate_pathways(articles, focal_start_year=2020)
        expected = {
            (row.focal_work_id, row.focal_author_id): (
                row.journal_path,
                row.publisher_path,
                row.coauthor_path,
            )
            for row in python_results
        }

        with tempfile.TemporaryDirectory() as tmp:
            temp_dir = Path(tmp)
            facts_path = temp_dir / "facts.pl"
            rules_path = temp_dir / paths.RULES_FILENAME
            facts_path.write_text(
                paths.render_prolog_facts(articles, focal_start_year=2020),
                encoding="utf-8",
            )
            rules_path.write_text(
                Path(paths.__file__).with_name(paths.RULES_FILENAME).read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            prolog_results = paths.run_prolog_analysis(facts_path, rules_path, articles)

        actual = {
            (row.focal_work_id, row.focal_author_id): (
                row.journal_path,
                row.publisher_path,
                row.coauthor_path,
            )
            for row in prolog_results
        }

        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
