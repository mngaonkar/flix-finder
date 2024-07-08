import xml.etree.ElementTree as ET
import bz2

def get_wikitext(dump_filename, offset, page_id=None, title=None, namespace_id=None, verbose=True, block_size=256*1024*10):
    """Extract content from a multistream dump file.                                                                                                                                                        
                                                                                                                                                                                                             
    offset: offset in bzip compressed file. Index file has the offset for all the articles.
    blocksize: chunk of data to read from the offset. Specify large enough value to have all matching XML tags.                                                                                                                                                                                                                                                                                                                                              
                                                                                                                                                                                 
    """
    unzipper = bz2.BZ2Decompressor()
                                                                                                                                                        
    uncompressed_data = b""
    with open(dump_filename, "rb") as infile:
        infile.seek(int(offset))

        while True:
            compressed_data = infile.read(block_size)
            try:
                uncompressed_data += unzipper.decompress(compressed_data)
            except EOFError:                                                                                                                                                        
                break
                                                                                                                                                            
            if compressed_data == '':
                break
                                                                                                                                                                                      

    uncompressed_text = uncompressed_data.decode("utf-8")
    # print(uncompressed_data)
    
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
                continue                                                                                                                                                                
        revision = page.find("revision")
        wikitext = revision.find("text")
        return wikitext.text
                                                                                                                                                             
    return None


def find_content():
    index_line = "18576985806:57445456:Raising the Bar (film)"
    offset, page_id, title = index_line.split(":")
    dump_file = "C:\\Users\\mahad\\Downloads\\enwiki-latest-pages-articles-multistream.xml.bz2"

    wikitext = get_wikitext(dump_file, int(offset), page_id=int(page_id))
    print(wikitext)
    
find_content()