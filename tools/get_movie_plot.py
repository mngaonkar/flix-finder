import re

def extract_plot_section(file_path):
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Regular expression to match content between "== Plot ==" and the next "== <any word> =="
    pattern = re.compile(r'== Plot ==(.*?)\n== \w+ ==', re.DOTALL)

    # Search for the pattern in the content
    match = pattern.search(content)

    # If a match is found, return the content, else return an appropriate message
    if match:
        return match.group(1).strip()
    else:
        return "Plot section not found."

# Specify the path to your text file
file_path = 'pulp_fiction_movie_content.txt'

# Extract and print the plot section
plot_section = extract_plot_section(file_path)
print("Plot Section:\n", plot_section)
