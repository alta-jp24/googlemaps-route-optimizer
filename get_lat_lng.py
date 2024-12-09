import googlemaps

# Google Maps APIキーを設定
googleapikey = 'API keyを設定する'
gmaps = googlemaps.Client(key=googleapikey)

# 入力リスト
places = ['東京ドイツ村', '原岡桟橋 (岡本桟橋)', '道の駅 富楽里とみやま パーキングエリア', '海ほたるPA']

# 出力リストを初期化
lat_lng_list = []

for place in places:
    result = gmaps.geocode(place)
    if result:
        lat = result[0]["geometry"]["location"]["lat"]
        lng = result[0]["geometry"]["location"]["lng"]
        lat_lng_list.append((lat, lng))

print(lat_lng_list)