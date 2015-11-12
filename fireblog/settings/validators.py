def max_rss_item_validator(item: int):
    return 1<= item <= 99999

def post_preview_len_validator(item: int):
    return 1 <= item <= 99999

def sitename_validator(item: str):
    return 1 <= len(item) <= 100
