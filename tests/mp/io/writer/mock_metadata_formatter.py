def mock_formatter(md):
    if md:
        return str(md.dict())
    else:
        return None
