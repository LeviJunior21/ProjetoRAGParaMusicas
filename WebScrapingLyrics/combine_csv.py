import pandas as pd
import argparse

def merge_csv(csv1, csv2, file_name="song_lyrics.csv"):
    df1 = pd.read_csv(csv1)
    df2 = pd.read_csv(csv2)

    combined_df = pd.concat([df1, df2])
    combined_df = combined_df.drop_duplicates(subset=['author', 'music', 'lyrics'])
    combined_df = combined_df.sample(frac=1).reset_index(drop=True)
    combined_df.to_csv(file_name, index=False)
    print(f"File saved as {file_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This combine the two CSVs without duplicates and do a shuffle.")
    parser.add_argument("csv1", help="Path of the first CSV")
    parser.add_argument("csv2", help="Path of the second CSV")
    parser.add_argument("-o", "--output", default="song_lyrics.csv", help="Output CSV name (default: song_lyrics.csv)")
    args = parser.parse_args()
    merge_csv(args.csv1, args.csv2, args.output)