# Snapshot of the collected topics

One gzipped JSON file per topic of [`patents/topics.py`](../topics.py), written by `python manage.py dump_seed` after a full `collect_patents`. A new instance loads them on its first start (`load_seed`), so the dashboard is complete without waiting for a collection.

| | |
|---|---|
| Source | [Google Patents Public Data](https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data), table `patents.publications`, read from the Parquet copy [`labofsahil/patents-publications-dataset`](https://huggingface.co/datasets/labofsahil/patents-publications-dataset) |
| Revision | `4b67cee3bc34ec78f7d2173c227b6c827d038f20` |
| Scope | US publications from 2015-01-01 whose title matches a topic, merged to one record per application |
| Figures | Representative figures of the 24 latest patents per topic (`fetch_figures`), linked from Google's patent image host; the others are looked up when first shown |
| License | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — Google Patents Public Data by IFI CLAIMS Patent Services and Google |
