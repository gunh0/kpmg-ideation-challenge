# Snapshot of the collected topics

`patents.json.gz` holds the topics (with their keywords) and their patents, each patent once with the slugs of the topics it belongs to. It is written by `python manage.py dump_seed` after a full `collect_patents`, and loaded by `load_seed` into an empty database on the first start, so the dashboard is complete without waiting for a collection. Topics deleted later do not come back.

| | |
|---|---|
| Source | [Google Patents Public Data](https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data), table `patents.publications`, read from the Parquet copy [`labofsahil/patents-publications-dataset`](https://huggingface.co/datasets/labofsahil/patents-publications-dataset) |
| Revision | `4b67cee3bc34ec78f7d2173c227b6c827d038f20` |
| Scope | US publications from 2015-01-01 whose title or abstract matches a topic's keywords, merged to one record per application: 32,862 patents (drones 11,428, autonomous driving 14,893, cybersecurity 6,964; 422 in more than one) |
| Citations | applications citing each patent, counted over all publications of the revision |
| Figures | Representative figures of the latest patents that have one, at least 12 per topic (`fetch_figures`), linked from Google's patent image host; the others are looked up when first shown. Publications since August 2025 have no image on Google yet. |
| License | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — Google Patents Public Data by IFI CLAIMS Patent Services and Google |
