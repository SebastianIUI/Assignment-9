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
        return ''
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


def find_header_index(header, keywords):
    for i, h in enumerate(header):
        low = h.lower().strip()
        for key in keywords:
            if key in low:
                return i
    return None


def create_sorted_tvshow_csv(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    if not lines:
        raise ValueError("Input file is empty.")

    header = parse_csv_line(lines[0])
    col_count = len(header)

    name_idx   = find_header_index(header, ['name', 'title', 'show']) or 0
    genres_idx = find_header_index(header, ['genre']) or min(1, col_count - 1)
    lang_idx   = find_header_index(header, ['language', 'lang']) or min(2, col_count - 1)
    rate_idx   = find_header_index(header, ['rating', 'score']) or min(3, col_count - 1)

    def get_field(fields, idx):
        return fields[idx].strip() if idx < len(fields) else ''

    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue

        fields = parse_csv_line(line)
        if len(fields) < col_count:
            fields += [''] * (col_count - len(fields))

        name     = get_field(fields, name_idx)
        genres   = get_field(fields, genres_idx)
        language = get_field(fields, lang_idx)
        rating   = get_field(fields, rate_idx)

        ordered = ordered_unique((name, genres, language, rating))
        ordered_str = " | ".join(x for x in ordered if x)

        rows.append((name, genres, language, rating, ordered_str))

    rows.sort(key=lambda r: r[0].lower() if r[0] else "")

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        out_header = ['Name', 'Genres', 'Language', 'Rating', 'OrderedSet']
        f.write(",".join(escape_field(h) for h in out_header) + "\n")

        for row in rows:
            f.write(",".join(escape_field(v) for v in row) + "\n")

    return output_path


# -------------------------------------
# FIXED INPUT AND OUTPUT PATHS HERE ↓↓
# -------------------------------------

input_file  = r"C:\Users\sebas\Downloads\TV_show_data.csv"
output_file = r"C:\Users\sebas\Downloads\TV_show_data_sorted.csv"

# Run automatically:
create_sorted_tvshow_csv(input_file, output_file)
print("Finished! Wrote sorted CSV to:", output_file)
