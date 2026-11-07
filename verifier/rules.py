def expected(data):
    rows = []
    for item in sorted(data.incoming, key=lambda row: row.id):
        if item.site_key:
            matches = [row for row in data.registry if row.site_key == item.site_key]
            method = "site_key"
        else:
            keys = (item.name_key, item.address_key, item.zip_code)
            matches = (
                [row for row in data.registry if (row.name_key, row.address_key, row.zip_code) == keys]
                if all(keys)
                else []
            )
            method = "composite"
        if len(matches) == 1:
            facility, decision = matches[0].id, method
        else:
            facility, decision = None, "ambiguous" if len(matches) > 1 else "unmatched"
        rows.append({"record_id": item.id, "facility_id": facility, "method": decision})
    return {"rows": rows}
