import sys

def main():
    try:
        file = open("C:\\Users\\mahad\\Downloads\\enwiki-latest-pages-articles-multistream-index.txt\\enwiki-latest-pages-articles-multistream-index.txt", "r", encoding="utf-8")
    except Exception as e:
        print(e)
        sys.exit(1)
        

    fout = open("movie_index.txt", "w", encoding="utf-8")
    for line in file.readlines():
        if "(film)" in line:
            fout.write(line)
            
    file.close()
    fout.close()



if __name__ == '__main__':
    main()