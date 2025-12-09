
import csv
import re
import sys
from pathlib import Path

input_file = sys.argv[1] if len(sys.argv) > 1 else 'tr_big9.csv'
output_file = sys.argv[2] if len(sys.argv) > 2 else None

input_path = Path(input_file)
if output_file is None:
    output_file = input_path.parent / f"{input_path.stem}_clean{input_path.suffix}"
output_path = Path(output_file)

with open(input_path, 'r', encoding='utf-8') as infile, \
     open(output_path, 'w', encoding='utf-8', newline='') as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    header = next(reader)
    writer.writerow(header)

    team1_comp_idx = header.index('Team1_Composition')
    team2_comp_idx = header.index('Team2_Composition')

    row_count = 0
    for row in reader:
        # remove trailing numbers from species names
        species1 = [re.sub(r'\d+$', '', s.strip()) for s in row[team1_comp_idx].split(',')]
        species2 = [re.sub(r'\d+$', '', s.strip()) for s in row[team2_comp_idx].split(',')]

        row[team1_comp_idx] = ', '.join(species1)
        row[team2_comp_idx] = ', '.join(species2)

        writer.writerow(row)
        row_count += 1

print(f"processed {row_count} rows")
print(f"output: {output_path}")
