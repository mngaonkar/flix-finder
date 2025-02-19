import sys
import argparse

WIKI_INDEX_FILE = "C:\\Users\\mahad\\Downloads\\enwiki-latest-pages-articles-multistream-index.txt\\enwiki-latest-pages-articles-multistream-index.txt"
MOVIE_INDEX_FILE = "movie_index.txt"

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--index_file", help="Path to the wiki index file")
    argparser.add_argument("--out_file", help="Path to the movie index file")
    args = argparser.parse_args()
    if args.index_file:
        WIKI_INDEX_FILE = args.index_file

    if args.out_file:
        MOVIE_INDEX_FILE = args.out_file

    try:
        file = open(WIKI_INDEX_FILE, "r", encoding="utf-8")
    except Exception as e:
        print(e)
        sys.exit(1)
        

    fout = open(MOVIE_INDEX_FILE, "w", encoding="utf-8")
    for line in file.readlines():
        if "(film)" in line:
            fout.write(line)
            
    file.close()
    fout.close()



if __name__ == '__main__':
    main()
