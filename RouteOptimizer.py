import pandas as pd
import googlemaps
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import webbrowser

def extract_titles(file_path):
    # CSVファイルを読み込み、"タイトル"列をリストで取得
    return pd.read_csv(file_path)["タイトル"].dropna().tolist()

def get_lat_lng_list(places, gmaps):
    # 緯度と経度を取得
    lat_lng_list = []
    for place in places:
        result = gmaps.geocode(place)
        if result:
            lat = result[0]["geometry"]["location"]["lat"]
            lng = result[0]["geometry"]["location"]["lng"]
            lat_lng_list.append((lat, lng))
    return lat_lng_list

def get_distance_matrix(locations, gmaps, chunk_size=10):
    # 距離行列をチャンクに分けて取得
    n = len(locations)
    distance_matrix = [[0]*n for _ in range(n)]
    
    for i in range(0, n, chunk_size):
        for j in range(0, n, chunk_size):
            origins = locations[i:i+chunk_size]
            destinations = locations[j:j+chunk_size]
            response = gmaps.distance_matrix(
                origins=origins, 
                destinations=destinations, 
                mode="driving"
            )
            for oi, origin_row in enumerate(response['rows']):
                for di, element in enumerate(origin_row['elements']):
                    distance_matrix[i+oi][j+di] = element['distance']['value']
    
    return distance_matrix

def create_data_model(distance_matrix):
    """Stores the data for the problem."""
    data = {}
    data["distance_matrix"] = distance_matrix
    data["num_vehicles"] = 1
    data["depot"] = 0
    return data

def print_solution(manager, routing, solution,titles):
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue()} miles")
    index = routing.Start(0)
    plan_output = "Route for vehicle 0:\n"
    route =[] #ルート順序を格納
    route_distance = 0
    while not routing.IsEnd(index):
        route.append(manager.IndexToNode(index))  # ルート順序を収集
        plan_output += f" {titles[manager.IndexToNode(index)]} ->"
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    route.append(manager.IndexToNode(index))  # 最後にデポ地点を追加
    plan_output += f" {manager.IndexToNode(index)}\n"
    print(plan_output)
    plan_output += f"Route distance: {route_distance}miles\n"

    # Google Maps URLを生成して表示
    generate_google_maps_url(route, titles)

def solve_tsp(data,titles):
    """TSPを解く"""
     # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(manager, routing, solution,titles)

def generate_google_maps_url(route, titles):
    """
    Generate a Google Maps URL to display the optimized route and open it in the browser.
    """
    # ルート情報から出発地、目的地、および経由地を設定
    origin = titles[route[0]]  # 出発地
    destination = titles[route[-1]]  # 目的地
    waypoints = "|".join(titles[i] for i in route[1:-1])  # 経由地（途中地点）

    # Google MapsのURLを生成
    url = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={origin}"
        f"&destination={destination}"
        f"&waypoints={waypoints}"
        f"&travelmode=driving"
    )

    # URLをブラウザで開く
    print("Generated Google Maps URL:", url)
    webbrowser.open(url)

def main(file_path, api_key):
    """エントリーポイント"""
    gmaps = googlemaps.Client(key=api_key)

    # タイトル列を取得
    titles = extract_titles(file_path)

    # 緯度経度を取得
    locations = get_lat_lng_list(titles, gmaps)

    # 距離行列を取得
    distance_matrix = get_distance_matrix(locations, gmaps)
    #print(distance_matrix)

    # TSPを解く
    data = create_data_model(distance_matrix)
    solve_tsp(data,titles)

if __name__ == "__main__":
    # 入力パラメータ
    FILE_PATH = "./最適化テスト用.csv"
    API_KEY = "API keyを設定する"  # Google Maps APIキーを設定

    main(FILE_PATH, API_KEY)