from dataclasses import replace

from contract import Case, CaseInput
from plugin.read_case import read_case
from verifier.rules import expected


def test_duplicate_site_key_abstains(tmp_path):
    data = read_case(CaseInput(Case.STANDARD), tmp_path)
    one = data.registry[1]
    assert (
        expected(replace(data, registry=[one, replace(one, id="DUP")], incoming=[data.incoming[0]]))["rows"][0][
            "method"
        ]
        == "ambiguous"
    )


def test_unknown_strong_key_never_falls_back(tmp_path):
    data = read_case(CaseInput(Case.STANDARD), tmp_path)
    assert expected(replace(data, incoming=[data.incoming[3]]))["rows"][0]["facility_id"] is None


def test_leading_zero_zip_is_not_coerced(tmp_path):
    data = read_case(CaseInput(Case.STANDARD), tmp_path)
    incoming = replace(data.incoming[4], zip_code="501")
    assert expected(replace(data, incoming=[incoming]))["rows"][0]["method"] == "unmatched"


def test_empty_keys_never_match(tmp_path):
    data = read_case(CaseInput(Case.STANDARD), tmp_path)
    empty = data.incoming[6]
    assert expected(replace(data, registry=[empty], incoming=[empty]))["rows"][0]["method"] == "unmatched"
