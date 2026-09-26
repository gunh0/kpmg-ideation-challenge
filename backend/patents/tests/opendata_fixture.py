"""A tiny Parquet file shaped like the Google Patents publications table."""
import duckdb


def publication(number, application, kind, title, abstract="", country="US", assignees=(), assignee_country="US",
                inventors=(), priority=20170301, filing=20180305, published=20190103, granted=0, cites=()):
    return {
        "publication_number": number, "application_number": application, "kind_code": kind, "family_id": "1",
        "title": title, "abstract": abstract, "country_code": country, "priority_date": priority,
        "filing_date": filing, "publication_date": published, "grant_date": granted,
        "assignee": list(assignees), "assignee_country": assignee_country, "inventor": list(inventors),
        "cites": list(cites),
    }


ROWS = [
    publication("US-2019000001-A1", "US-201816000001-A", "A1", "Drone delivery of parcels",
                "A drone lowers parcels on a tether.", assignees=["Example Robotics Inc."],
                inventors=["DOE, JANE", "ROE, JOHN"]),
    publication("US-10000001-B2", "US-201816000001-A", "B2", "Drone delivery of parcels to balconies",
                "A drone lowers parcels onto balconies.", assignees=["Example Robotics Inc."],
                inventors=["DOE, JANE", "ROE, JOHN"], published=20200602, granted=20200602),
    # cybersecurity by its title, autonomous driving by its abstract
    publication("US-2021000002-A1", "US-202016000002-A", "A1", "Intrusion detection for vehicle networks",
                "Watches the bus of an autonomous vehicle for injected messages.",
                assignees=["Example Security LLC", "Example Motors"], assignee_country="KR",
                inventors=["Miles, Richard"], priority=20190901, filing=20200901, published=20210304),
    publication("US-2021000003-A1", "US-202016000003-A", "A1", "Coffee machine", "Brews coffee.",
                assignees=["Example Kitchens"], inventors=["MAJOR, MARY"], published=20210304,
                cites=["US-2019000001-A1"]),
    publication("EP-3000004-A1", "EP-20000004-A", "A1", "Drone landing pad", country="EP",
                assignees=["Example Robotics Inc."], published=20210304),
    publication("US-2014000005-A1", "US-201313000005-A", "A1", "Early drone", published=20140304),
    # drones by its abstract only
    publication("US-2022000006-A1", "US-202117000006-A", "A1", "Parcel locker",
                "A locker that receives parcels from drones.", assignees=["Example Lockers Co."],
                assignee_country="CN", published=20220106, cites=["US-10000001-B2", "US-2021000002-A1"]),
]


def write(path):
    connection = duckdb.connect()
    connection.execute("""
        CREATE TABLE publications (
            publication_number VARCHAR, application_number VARCHAR, kind_code VARCHAR, family_id VARCHAR,
            title_localized STRUCT(text VARCHAR, "language" VARCHAR, truncated BOOLEAN)[],
            abstract_localized STRUCT(text VARCHAR, "language" VARCHAR, truncated BOOLEAN)[],
            country_code VARCHAR, priority_date BIGINT, filing_date BIGINT, publication_date BIGINT,
            grant_date BIGINT, assignee VARCHAR[], assignee_harmonized STRUCT(name VARCHAR, country_code VARCHAR)[],
            inventor VARCHAR[], citation STRUCT(publication_number VARCHAR, category VARCHAR)[]
        )
    """)
    for row in ROWS:
        connection.execute(
            """INSERT INTO publications VALUES (
                ?, ?, ?, ?, [{'text': ?, 'language': 'en', 'truncated': false}],
                [{'text': ?, 'language': 'en', 'truncated': false}], ?, ?, ?, ?, ?, ?,
                list_transform(?::VARCHAR[], name -> {'name': upper(name), 'country_code': ?}), ?,
                list_transform(?::VARCHAR[], number -> {'publication_number': number, 'category': ''})
            )""",
            [row["publication_number"], row["application_number"], row["kind_code"], row["family_id"],
             row["title"], row["abstract"], row["country_code"], row["priority_date"], row["filing_date"],
             row["publication_date"], row["grant_date"], row["assignee"], row["assignee"],
             row["assignee_country"], row["inventor"], row["cites"]],
        )
    connection.execute(f"COPY publications TO '{path}' (FORMAT parquet)")
    return path
