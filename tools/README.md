# Generating `movies.csv` from Wikipedia Dumps

This guide explains how to extract, parse, and generate the `database/movies.csv` dataset from raw Wikipedia multistream dumps using the scripts in the [`tools/`](.) directory.

---

## 1. Prerequisites & Dependencies

Ensure you have Python 3.10+ installed and install the required dependencies:

```bash
pip install loguru pandas
```

---

## 2. Download Raw Wikipedia Dumps

The movie dataset is generated using official Wikimedia database dumps available at [Wikimedia Downloads](https://dumps.wikimedia.org/enwiki/latest/):

1. **Multistream Articles Archive**:
   * File: `enwiki-latest-pages-articles-multistream.xml.bz2` (~22 GB compressed)
   * Contains all English Wikipedia article contents compressed in discrete bz2 chunks.
2. **Multistream Articles Index**:
   * File: `enwiki-latest-pages-articles-multistream-index.txt.bz2` (~250 MB compressed)
   * Contains the byte offset mappings for each article.

Decompress the index file:
```bash
bzip2 -d enwiki-latest-pages-articles-multistream-index.txt.bz2
```

---

## 3. Extraction Pipeline

### Step 1: Filter Movie Articles (`parse_movie_index.py`)

Filter the raw index file down to movie articles by selecting entries containing `(film)` in their title.

```bash
python tools/parse_movie_index.py \
  --index_file path/to/enwiki-latest-pages-articles-multistream-index.txt \
  --out_file movie_index.txt
```

* **Input**: Full Wikipedia index file with rows structured as `<byte_offset>:<page_id>:<article_title>`.
* **Output**: `movie_index.txt` containing only film-related article references.

---

### Step 2: Stream & Extract Movie Content (`process_wiki_dump.py`)

Extract movie details from the compressed dump using byte offsets (without having to decompress the entire 100+ GB uncompressed XML archive).

```bash
python tools/process_wiki_dump.py \
  --index_file movie_index.txt \
  --dump_file path/to/enwiki-latest-pages-articles-multistream.xml.bz2 \
  --out_file database/movies.csv
```

#### What this step does:
1. **Random-Access Seeking**: Uses the byte offset from `movie_index.txt` to `seek()` directly to the compressed chunk in `enwiki-...multistream.xml.bz2`.
2. **Decompression & XML Parsing**: Decompresses only the matching 2.5 MB block and parses the XML `<page>` wikitext.
3. **Section Extraction**:
   * **Plot**: Extracts text between `== Plot ==`, `== Synopsis ==`, `== Overview ==`, or `== Premise ==`.
   * **Cast**: Extracts text from the `== Cast ==` section.
   * **Poster URL**: Extracts the image filename from the infobox (`image = ...`), computes its MD5 hash, and generates the live Wikimedia URL:
     ```text
     https://upload.wikimedia.org/wikipedia/en/<hash[0]>/<hash[0:2]>/<urlencoded_filename>
     ```
4. **CSV Export**: Writes the structured records to CSV.

---

## 4. Output Schema (`movies.csv`)

The output file is written to [`database/movies.csv`](../database/movies.csv) with the following schema:

| Column | Description | Example |
| :--- | :--- | :--- |
| **`id`** | Wikipedia Page ID | `3947` |
| **`title`** | Movie title as listed on Wikipedia | `Blue Velvet (film)` |
| **`cast`** | Extracted cast members | `{{cast listing... Isabella Rossellini...}}` |
| **`plot`** | Full movie plot summary text | `College student Jeffrey Beaumont returns to his hometown...` |
| **`poster`** | Wikimedia Commons / Wikipedia poster URL | `https://upload.wikimedia.org/wikipedia/en/f/fd/Blue_Velvet_%281986%29.png` |

---

## 5. Helper & Diagnostic Scripts

* [`tools/get_wiki_article.py`](./get_wiki_article.py): Debug tool to inspect raw wikitext for a specific byte offset and page ID.
* [`tools/get_movie_plot.py`](./get_movie_plot.py): Tests regex extraction on a local text sample of a movie article.
* [`tools/get_movie_poster_link.py`](./get_movie_poster_link.py): Tests poster image hash calculation and Wikimedia URL synthesis.
* [`tools/movie_database.py`](./movie_database.py): Pandas utility to merge additional metadata or external movie datasets.
