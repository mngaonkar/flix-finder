import sys
import xml.etree.ElementTree as ET
import bz2
import re
import hashlib
import urllib.parse

WIKI_DUMP_FILE = "C:\\Users\\mahad\\Downloads\\enwiki-latest-pages-articles-multistream.xml.bz2"
BLOCK_SIZE = 256*1024*10

def load_index(index_file):
    """load movie index """
    index_list = []
    try:
        file = open(index_file, "r", encoding="utf-8")
    except Exception as e:
        print(e)
        
    for line in file.readlines():
        # offset, ID, title
        parsed = line.strip().split(":")
        index_list.append((parsed[0], parsed[1], "".join(parsed[2:]))) # handle colon in title
    
    file.close()
    return index_list

def extract_plot_section(wiki_text):
    # Regular expression to match content between "== Plot ==" and the next "== <any word> =="
    pattern = re.compile(r'==\s*(Plot|Overview|Contents|Synopsis)\s*==(.*?)\n==\s*\w+\s*==', re.DOTALL)

    # Search for the pattern in the content
    match = pattern.search(wiki_text)

    # If a match is found, return the content, else return an appropriate message
    if match:
        content = match.group(2).replace('\n', '')
        content = content.replace(',', ' ')
        return content
    else:
        return None

def extract_poster_url(wiki_text):
    pattern = re.compile(r'image\s+=\s+(.+)\n', re.MULTILINE)

    # Search for the pattern in the content
    match = pattern.search(wiki_text)

    # If a match is found, return the content, else return an appropriate message
    if match:
        image_name = match.group(1).strip()
        image_name = image_name.replace(" ", "_")
        md5_hash = hashlib.md5()
        md5_hash.update(image_name.encode())
        hash_string = md5_hash.hexdigest()
        print("MD5 hash = ", hash_string)
        
        print("Image name = ", image_name)
        image_name_encoded = urllib.parse.quote(image_name, safe='')
        # example - https://upload.wikimedia.org/wikipedia/en/3/3b/Pulp_Fiction_%281994%29_poster.jpg
        image_url = "https://upload.wikimedia.org/wikipedia/en/" + hash_string[0] + "/" + hash_string[0:2] + "/" + image_name_encoded
       
        return image_url
    else:
        return None
        
        
def get_wiki_text(uncompressed_text, page_id, title=None, namespace_id=None):
    xml_data = "<root>" + uncompressed_text + "</root>"
        
    root = ET.fromstring(xml_data)
    for page in root.findall("page"):
        if title is not None:
            if title != page.find("title").text:
                continue
        if namespace_id is not None:
            if namespace_id != int(page.find("ns").text):
                continue
        if page_id is not None:
            if page_id != int(page.find("id").text):
                current_page_id = int(page.find("id").text)
                # print(f"page id {page_id} not matching with {current_page_id}")
                continue                                                                                                                                                                
        revision = page.find("revision")
        wikitext = revision.find("text")
        
        return wikitext.text
            
def main():
    print("loading index...")
    index_list = load_index("movie_index.txt")
    print("index loaded.")
    
    print("open output CSV file...")
    try:
        out_file = open("movies.csv", "w", encoding="utf-8")
        out_file.write("id, title, plot, poster\n")
    except Exception as e:
        print(e)
        return sys.exit(1)
    print("out file opened")
                                                                                                                                                        
    print("open wiki dump file...")
    try:
        infile = open(WIKI_DUMP_FILE, "rb")
    except Exception as e:
        print(e)
        sys.exit(1)
    print("wiki dump file opened.")
    
    
    for (offset, page_id, title) in index_list:
        print(f"processing title: {title} id: {page_id} offset: {offset}...")
        infile.seek(int(offset))
        print(f"current file pointer {infile.tell()}")
        
        unzipper = bz2.BZ2Decompressor()
        uncompressed_data = b""
        while True:
            compressed_data = infile.read(BLOCK_SIZE)
            if not compressed_data:
                break
                
            try:
                uncompressed_data += unzipper.decompress(compressed_data)
                if unzipper.eof:
                    break
            except Exception as e:
                print(e)
                break                                                                                                                                                     
                
        uncompressed_text = uncompressed_data.decode("utf-8")
        wiki_text = get_wiki_text(uncompressed_text, int(page_id))
        if wiki_text is None:
            print("no wiki text found")
            continue
            
        movie_plot = extract_plot_section(wiki_text)
        if movie_plot is None:
            print("plot not found")
            continue
        movie_poster_url = extract_poster_url(wiki_text)
        print(f"poster = {movie_poster_url}")
        if movie_poster_url is None:
            print("poster not found")
            continue
        
        out_file.write(f"{page_id},{title},{movie_plot},{movie_poster_url}\n")
     
    infile.close()
    out_file.close()
    print("wiki data processed")
        
if __name__ == '__main__':
    main()