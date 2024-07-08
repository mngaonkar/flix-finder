import re
import hashlib
import urllib.parse

def extract_image_section(file_path):
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    pattern = re.compile(r'image\s+=\s+(.+)\n', re.MULTILINE)

    # Search for the pattern in the content
    match = pattern.search(content)

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
        return "Image section not found."

# Specify the path to your text file
file_path = "C:\\Users\\mahad\\Downloads\\pulp_fiction_movie_content.txt"

# Extract and print the plot section
image_section = extract_image_section(file_path)
print("Poster URL:\n", image_section)
