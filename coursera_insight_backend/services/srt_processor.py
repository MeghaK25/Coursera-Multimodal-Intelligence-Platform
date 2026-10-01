import re

def parse_srt(content: str):
    """Convert SRT captions into text segments while preserving timestamps."""
    normalized = content.replace("\r\n", "\n").strip()
    blocks = re.split(r"\n\s*\n", normalized)
    segments = []

    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            continue

        try:
            index = int(lines[0].strip())
        except ValueError:
            continue

        start_time, end_time = [x.strip() for x in lines[1].split("-->", 1)]
        text = " ".join(line.strip() for line in lines[2:] if line.strip())

        segments.append({
            "index": index,
            "start_time": start_time,
            "end_time": end_time,
            "text": text,
        })

    return segments
