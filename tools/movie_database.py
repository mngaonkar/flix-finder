import pandas as pd

# Load the CSV files into DataFrames
movies1_df = pd.read_csv('database/movies.csv')
movies2_df = pd.read_csv('database/final_data.csv')

# Extract year from the release_date column in movies1_df
movies1_df['release_year'] = pd.to_datetime(movies1_df['release_date'], errors='coerce').dt.year

# Extract year from the DatePublished column in movies2_df
movies2_df['publish_year'] = pd.to_datetime(movies2_df['DatePublished'], errors='coerce').dt.year

# Display the first few rows to understand the structure
print("Movies1 DataFrame:")
print(movies1_df.head())
print("\nMovies2 DataFrame:")
print(movies2_df.head())

# Merge the DataFrames on the matching columns and the year
merged_df = pd.merge(movies1_df, movies2_df[['Name', 'PosterLink', 'publish_year']], 
                     left_on=['original_title', 'release_year'], 
                     right_on=['Name', 'publish_year'], 
                     how='left')

# Drop the redundant columns
merged_df = merged_df.drop(columns=['Name', 'publish_year'])

# Save the updated DataFrame back to a new CSV file
merged_df.to_csv('movies1_with_poster.csv', index=False)

print("\nMerged DataFrame with PosterLink:")
print(merged_df.head())
