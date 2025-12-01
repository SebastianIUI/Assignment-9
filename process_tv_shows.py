# Pure-Python CSV processor — auto-detects CSV in Downloads
# No imports used.

def parse_csv_line(line):
    line = line.rstrip('\n').rstrip('\r')
    fields = []
    cur = ''
    in_quotes = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            if in_quotes and i + 1 < len(line) and line[i + 1] == '"':
                cur += '"'
                i += 1
            else:
                in_quotes = not in_quotes
        elif ch == ',' and not in_quotes:
            fields.append(cur)
            cur = ''
        else:
            cur += ch
        i += 1
    fields.append(cur)
    return fields


def escape_field(field):
    if field is None:
        field = ''
    field = str(field)
    if any(c in field for c in ['"', ',', '\n', '\r']):
        return '"' + field.replace('"', '""') + '"'
    return field


def ordered_unique(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


# -----------------------
# AUTO-DETECT CSV IN DOWNLOADS
# -----------------------
def find_csv_in_downloads():
    downloads = "C:\\Users\\sebas\\Downloads\\"
    # manually list files in Downloads without using os.listdir
    try:
        test = open(downloads + "dummy_check.txt", "w")
        test.write("x")
        test.close()
    except:
        return None

    # brute-force check for common filenames
    candidates = [
        "TV_show_data.csv",
        "tv_show_data.csv",
        "TV_show_data (1).csv",
        "TV shows.csv",
        "shows.csv",
        "data.csv"
    ]

    for c in candidates:
        path = downloads + c
        try:
            f = open(path, "r", encoding="utf-8", errors="replace")
            f.close()
            return path
        except:
            continue

    return None


def process_tv_csv(input_path, output_path):
    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    if not lines:
        raise ValueError("Input file empty")

    header = parse_csv_line(lines[0])

    def find_header(header, keywords, default):
        for i, h in enumerate(header):
            low = h.lower().strip()
            for k in keywords:
                if k in low:
                    return i
        return default

    name_idx = find_header(header, ["name", "title", "show"], 0)
    genre_idx = find_header(header, ["genre"], 1)
    lang_idx = find_header(header, ["language", "lang"], 2)
    rating_idx = find_header(header, ["rating", "score"], 3)

    rows = []

    for line in lines[1:]:
        if line.strip() == "":
            continue
        fields = parse_csv_line(line)
        while len(fields) < len(header):
            fields.append("")

        name = fields[name_idx].strip()
        genres = fields[genre_idx].strip()
        language = fields[lang_idx].strip()
        rating = fields[rating_idx].strip()

        ordered = ordered_unique([name, genres, language, rating])
        ordered_str = " | ".join([x for x in ordered if x != ""])

        rows.append((name, genres, language, rating, ordered_str))

    rows.sort(key=lambda r: r[0].lower())

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        out_head = ["Name", "Genres", "Language", "Rating", "OrderedSet"]
        f.write(",".join(escape_field(x) for x in out_head) + "\n")
        for r in rows:
            f.write(",".join(escape_field(x) for x in r) + "\n")

    return output_path


# -----------------------
# MAIN (AUTO-DETECT INPUT)
# -----------------------

print("Searching Downloads folder for CSV file...")

input_path = find_csv_in_downloads()

if input_path is None:
    print("No CSV found in Downloads. Check file name.")
else:
    output_path = "C:\\Users\\sebas\\Downloads\\TV_show_data_output.csv"
    try:
        result = process_tv_csv(input_path, output_path)
        print("Success! Wrote:", result)
    except Exception as e:
        print("Error:", e)
