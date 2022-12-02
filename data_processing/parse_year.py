import os
import glob
import pandas as pd
from tqdm import tqdm
import re
import subprocess

def parse_year_published():
    ''' Parse the original data to extract the year the book was published.
        This only returns an estimated year based on the idea that the publication
        year will usually be at the top of the book. For example: Copyright (c) 2008.
        So there is a fair chance that the year picked up may not be accurate, but
        this is a close approximation.
    '''
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__).split('data_processing')[0])
    raw_dataset_path = f"{ROOT_DIR}/data/raw/books1/epubtxt"
    columns = ["year_published",  "filename", "title"]
    output = pd.DataFrame(columns=columns)
    # get all filenames
    all_books = glob.glob(f"{raw_dataset_path}/*.txt")

    year_published_regex = [r'20\d{2}$', r'20\d{2}', r'\d{4}$', r'\d{4}']
    for book in tqdm(all_books):
        # get the first couple of lines (300 here) in the novel and see if there is a publication year
        # we use regular expressions that are consecutively less constraining until we find a match
        LINES = min(300, int(subprocess.check_output(['wc', '-l', book]).split()[0]))
        with open(book, "r", errors="ignore") as bk:
            top_lines = "".join(next(bk) for _ in range(LINES))
            publication_year = None
            for reg in year_published_regex:
                year = re.findall(reg, top_lines)
                # get the first match we find
                if len(year) >= 1:
                    # filter years between 2000 and 2023
                    year = [yr for yr in year if ((int(yr) >= 1990) and (int(yr) <= 2023))]
                    if len(year) >= 1:
                        publication_year = year[0]
                        break
            # do some minor cleanup and append everything to the data frame
            output = pd.concat([output, pd.Series({
                "year_published": publication_year if publication_year else 1111,
                "filename": book.split("/")[-1],
                "title": book.split("/")[-1].split(".", -2)[0].replace("-", " ").capitalize(),}).to_frame().T],
                ignore_index=True)
    # write output to CSV file
    output.to_csv(f"{ROOT_DIR}/data/metadata/year_published.csv", index=False)

if __name__ == "__main__":
    parse_year_published()
