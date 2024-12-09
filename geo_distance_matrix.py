import googlemaps

# Google Maps APIキーを設定
API_KEY = "API keyを設定する"
gmaps = googlemaps.Client(key=API_KEY)

# 地点リスト
locations = [(35.4056432, 140.0539067), (35.044254, 139.8311644), (35.1002396, 139.8560761), (35.4637979, 139.8753237)]

# Google Maps Distance Matrix API を使用して距離行列を取得
matrix_response = gmaps.distance_matrix(
    origins=locations, 
    destinations=locations, 
    mode="driving"
)

# 距離行列を抽出して配列に整形
distance_matrix = []
for row in matrix_response['rows']:
    distance_row = [element['distance']['value'] for element in row['elements']]
    distance_matrix.append(distance_row)

print(distance_matrix)
