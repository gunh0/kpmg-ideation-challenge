"""A tiny Parquet file shaped like the Google Patents publications table."""
import duckdb

ROWS = [
    # publication, application, kind, family, title, lang, country, priority, filing, published, granted, assignees, inventors
    ("US-2019000001-A1", "US-201816000001-A", "A1", "1", "Drone delivery of parcels", "en", "US",
     20170301, 20180305, 20190103, 0, ["Example Robotics Inc."], ["DOE, JANE", "ROE, JOHN"]),
    ("US-10000001-B2", "US-201816000001-A", "B2", "1", "Drone delivery of parcels to balconies", "en", "US",
     20170301, 20180305, 20200602, 20200602, ["Example Robotics Inc."], ["DOE, JANE", "ROE, JOHN"]),
    ("US-2021000002-A1", "US-202016000002-A", "A1", "2", "Intrusion detection for vehicle networks", "en", "US",
     20190901, 20200901, 20210304, 0, ["Example Security LLC", "Example Motors"], ["Miles, Richard"]),
    ("US-2021000003-A1", "US-202016000003-A", "A1", "3", "Coffee machine", "en", "US",
     20190901, 20200901, 20210304, 0, ["Example Kitchens"], ["MAJOR, MARY"]),
    ("EP-3000004-A1", "EP-20000004-A", "A1", "4", "Drone landing pad", "en", "EP",
     20190901, 20200901, 20210304, 0, ["Example Robotics Inc."], ["DOE, JANE"]),
    ("US-2014000005-A1", "US-201313000005-A", "A1", "5", "Early drone", "en", "US",
     20120901, 20130901, 20140304, 0, ["Example Robotics Inc."], ["DOE, JANE"]),
]


def write(path):
    connection = duckdb.connect()
    connection.execute("""
        CREATE TABLE publications (
            publication_number VARCHAR, application_number VARCHAR, kind_code VARCHAR, family_id VARCHAR,
            title_localized STRUCT(text VARCHAR, "language" VARCHAR, truncated BOOLEAN)[], country_code VARCHAR,
            priority_date BIGINT, filing_date BIGINT, publication_date BIGINT, grant_date BIGINT,
            assignee VARCHAR[], inventor VARCHAR[]
        )
    """)
    for (number, application, kind, family, title, language, country,
         priority, filing, published, granted, assignees, inventors) in ROWS:
        connection.execute(
            "INSERT INTO publications VALUES (?, ?, ?, ?, [{'text': ?, 'language': ?, 'truncated': false}], ?, ?, ?, ?, ?, ?, ?)",
            [number, application, kind, family, title, language, country, priority, filing, published, granted,
             assignees, inventors],
        )
    connection.execute(f"COPY publications TO '{path}' (FORMAT parquet)")
    return path
