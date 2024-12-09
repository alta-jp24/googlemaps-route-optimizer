import pandas as pd

# CSVファイルを読み込み、"タイトル"列をリストで取得
titles = pd.read_csv("最適化テスト用.csv")["タイトル"].dropna().tolist()

# タイトル一覧を表示
print(titles)
