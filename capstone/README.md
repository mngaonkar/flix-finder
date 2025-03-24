### Flix Finder - A movie Recommendation Engine

**Author**
mahadev.gaonkar@gmail.com

### Executive summary
This project aims to develop a personalized movie recommender system that enhances content discovery by leveraging machine learning and natural language processing techniques. By analyzing user interactions and movie-related data from Wikipedia, the system predicts user preferences and suggests relevant movies. The approach integrates multiple methodologies such as TF-IDF, cosine similarity, Doc2Vec embeddings, and classification models to improve recommendation accuracy. The expected outcome includes a publicly accessible website with an intuitive UI, AI-driven search capabilities, and an API for external integrations, ultimately delivering a seamless and engaging movie discovery experience.

### Rationale
With an overwhelming number of movies available across platforms, users often struggle to find content aligned with their interests. A robust recommender system can enhance user experiences, drive platform engagement, and address content discovery challenges, making it valuable for both users and service providers.

### Research Question
Personalized movie recommender system effectively suggest movies based on either a movie name or plot description

### Data Sources
- Wikipedia dumps - https://dumps.wikimedia.org/ Links to an external site.
- Custom processing scripts to filter only movie related content including text and movie poster

### Methodology
The techniques used to solve the challenge

#### TF-IDF (Term Frequency-Inverse Document Frequency)

Extracts important features from movie descriptions (e.g., keywords from plots).
Measures how relevant a feature is to a specific movie.

#### Cosine Similarity

Measures the similarity between the feature vectors of movies.
Suggests movies most similar to the ones a user has liked.

#### Doc2Vec or Embedding models

Vector representations of entire documents or paragraphs

#### Classification
Refinement with classification models whether a user will like a movie based on like/dislike. 

### Results
#### The expected results

A public hosted website for movie recommendation (developed with web technologies HTML, JavaScript and backend Python services)
A visual representation of recommendation/relevant movies with summarized insight (plot, characters etc.) labeled
Movie poster for enhanced user experience
Link to movie details on Wikipedia
AI driven search results based on movie theme, actor, genre or simple text description

### Final Capstone Report
#### Objective
Build a movie recommender project/website for suggesting simlar movies based on movie name or plot description.

#### Exploratory analysis
Movie data for the project is obtained from Wikipedia pages. The data is under permissive license to be used for commercial as well as non-commerical projects (https://dumps.wikimedia.org/legal.html). The movie data primarily contains title, cast and plot information. The size of the data is over 15K movies.

Following is brief summary of all the approaches considered for movie recommender system.

| Approach           | Pros                                      | Cons                                      |
|--------------------|-------------------------------------------|-------------------------------------------|
| TF-IDF             | - Simple<br>- Computationally efficient<br>- No training required | - Limited semantics<br>- Sparse vectors<br>- Works well with small length text |
| Doc2Vec            | - Good semantic understanding<br>- Dense vectors<br>- Works well with long text like movie descriptions | - Computationally expensive to train<br>- High dependency on good data<br>- Less interpretable |
| Large Language Model | - Rich contextualization<br>- Good semantic understanding<br>- Pre-trained model can be tuned for specific data | - Resource intensive<br>- Limited input text length based on context window<br>- Less interpretable |

Large Language Model (LLM) based implmentation has the highest recommendation quality hence it's selected as preferred approach for the recommender system implementation.

Refer - https://github.com/mngaonkar/flix-finder/blob/main/capstone/1_movie_recommender_exploratory_data_analysis.ipynb


#### Large Language Model (LLM) based implementation

Here is sample of final movie dataset [movies.csv](https://github.com/mngaonkar/flix-finder/blob/main/capstone/data/movies.csv) that is be used for foundation for movie recommender system.
| id     | title                     | cast                                      | plot                                      | poster                                     | actors                                     |
|--------|---------------------------|-------------------------------------------|-------------------------------------------|--------------------------------------------|--------------------------------------------|
| 0      | 3947   Blue Velvet (film) |  | College student Jeffery Beaumont returns to hi... |  https://upload.wikimedia.org/wikipedia/en/ff/d...                                          |
| 1      | 4231   Buffy the Vampire Slayer (film) | Appearing in uncredited roles are Ben Affleck ... | Buffy is a cheerleader at Hemery High ... | https://upload.wikimedia.org/wikipedia/en/0/09... | Ben Affleck, Ricki Lake, Seth Green, Alexis Ar... |
| 2      | 4729   Batman & Robin (film) | Arnold Schwarzenegger as Dr. Victor Fries / ... | Batman and his partner Robin encounter a new... | https://upload.wikimedia.org/wikipedia/en/3/37... | Arnold Schwarzenegger, George Clooney, Eric Li... |
| 3      | 11585  Show Me Love (film) | Alexandra Dahlström as Elin Olsson Rebecka Li... | Two girls Agnes and Elin attend school in th... | https://upload.wikimedia.org/wikipedia/en/9/96... | Elin Olsson Rebecka Liljeberg, Agnes Ahlberg E... |
| 4      | 19055  Manufacturing Consent (film) | None | The film presents and illustrates Chomsky and ... | https://upload.wikimedia.org/wikipedia/en/1/11... |                                            |
| ...    | ...                       | ...                                       | ...                                       | ...                                        | ...                                        |
| 15790  | 77243966 Take It to the Limit (film) | Jason BortzLEO Fitzpatrick John Marlo Gretel R... | A troubled teenager goes rock climbing... | https://upload.wikimedia.org/wikipedia/en/4/44... | Jason BortzLEO Fitzpatrick John Marlo Gretel R... |
| 15791  | 77245209 Firefight (film) | Nick MancusoStephen BaldwinSteve Bacic | Bank robbers get involved with a firestorm... | https://upload.wikimedia.org/wikipedia/en/4/44... | Nick MancusoStephen BaldwinSteve Bacic |

The each movie information above is converted to LLM embedding vector by using [Hugging Face sentence transformer all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2) 

The resultant embedding vector is stored in [Milvus vector database](https://milvus.io). Milvus supports inbox similarity search functionality that is used for finding movies with semantically similar plots. 

[LangChain](https://www.langchain.com) is used as preferred platform to build final application as it supports integration with Hugging Face models as well Milvus vector database.

Refer - https://github.com/mngaonkar/flix-finder/blob/main/capstone/3_movie_recommender_mvp.ipynb

Here is an example of finding movies with plot "movies about a wizard with dangerous powers"
- Convert the input text to high dimension vector embedding using sentence transformer all-mpnet-base-v2
- Perform similarity serach with this input embedding vector on Milvus database
- Similarity search returns matching embedded vectors based on nearest distance

Visualization post converting the matching high dimension embeddeding vectors to two dimenstion is as follows:

![Alt text](https://github.com/mngaonkar/flix-finder/blob/main/capstone/images/t-sne-viz.png?raw=true)

#### Outline of project
- [Capstone project main directory](https://github.com/mngaonkar/flix-finder/tree/main/capstone)
- [Capstone Report](https://github.com/mngaonkar/flix-finder/blob/main/capstone/README.md)
- [Capstone Presentation](https://github.com/mngaonkar/flix-finder/blob/main/capstone/presentation/Movie_Recommender_Mahadev_Gaonkar.pptx) 
- [Exploratory analysis](https://github.com/mngaonkar/flix-finder/blob/main/capstone/1_movie_recommender_exploratory_data_analysis.ipynb)
- [PoC with different approaches](https://github.com/mngaonkar/flix-finder/blob/main/capstone/2_movie_recommender_inference.ipynb)
- [Final minumum viable project (MVP) implementation](https://github.com/mngaonkar/flix-finder/blob/main/capstone/3_movie_recommender_mvp.ipynb)



##### Contact and Further Information
- Email: mahadev.gaonkar@gmail.com
- X: @mngaonkar