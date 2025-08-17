import textwrap

def smart_chunks(text: str, target_tokens: int = 1200) -> list:
    # naive length based chunking with sentence boundaries
    sents = text.replace("\r", " ").split(". ")
    chunks, cur, cur_len = [], [], 0
    for s in sents:
        l = max(1, len(s) // 4)
        if cur_len + l > target_tokens and cur:
            chunks.append(". ".join(cur))
            cur, cur_len = [s], l
        else:
            cur.append(s); cur_len += l
    if cur:
        chunks.append(". ".join(cur))
    return chunks
