### Flix Finder - A movie Recommendation Engine

**Author**
mahadev.gaonkar@gmail.com

#### Executive summary
This project aims to develop a personalized movie recommender system that enhances content discovery by leveraging machine learning and natural language processing techniques. By analyzing user interactions and movie-related data from Wikipedia, the system predicts user preferences and suggests relevant movies. The approach integrates multiple methodologies such as TF-IDF, cosine similarity, Doc2Vec embeddings, and classification models to improve recommendation accuracy. The expected outcome includes a publicly accessible website with an intuitive UI, AI-driven search capabilities, and an API for external integrations, ultimately delivering a seamless and engaging movie discovery experience.

#### Rationale
With an overwhelming number of movies available across platforms, users often struggle to find content aligned with their interests. A robust recommender system can enhance user experiences, drive platform engagement, and address content discovery challenges, making it valuable for both users and service providers.

#### Research Question
Personalized movie recommender system effectively predict user preferences based on past interactions

#### Data Sources
- Wikipedia dumps - https://dumps.wikimedia.org/ Links to an external site.
- Custom processing scripts to filter only movie related content including text and movie poster

#### Methodology
The techniques used to solve the challenge

##### TF-IDF (Term Frequency-Inverse Document Frequency)

Extracts important features from movie descriptions (e.g., keywords from plots).
Measures how relevant a feature is to a specific movie.

##### Cosine Similarity

Measures the similarity between the feature vectors of movies.
Suggests movies most similar to the ones a user has liked.

##### Doc2Vec or Embedding models

Vector representations of entire documents or paragraphs

##### Classification
Refinement with classification models whether a user will like a movie based on like/dislike. 

#### Results
##### The expected results

A public hosted website for movie recommendation (developed with web technologies HTML, JavaScript and backend Python services)
A visual representation of recommendation/relevant movies with summarized insight (plot, characters etc.) labeled
Movie poster for enhanced user experience
Link to movie details on Wikipedia
AI driven search results based on movie theme, actor, genre or simple text description
API for integration with external applications 
Customized top 10 movie lists to watch for users 

##### Final results

#### Next steps
What suggestions do you have for next steps?

#### Outline of project

- [Link to notebook 1]()
- [Link to notebook 2]()
- [Link to notebook 3]()


##### Contact and Further Information