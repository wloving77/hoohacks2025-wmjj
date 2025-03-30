import orders_scrape
import json
from pprint import pprint

if __name__ == "__main__":
    recent_orders = orders_scrape.get_recent_ten_orders()

    print(recent_orders)
    

    
    