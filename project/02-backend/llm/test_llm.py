import pandas as pd
import io
import requests
import fitz
import time
import llm
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables


if __name__ == "__main__":
    df = pd.read_csv("project/exec-dev/executive_orders.csv")
    df = df.head(5)

    single_order = df.iloc[0]['order_text']

    llm_obj = llm.GeminiModel(api_key = os.getenv("GEM_API_KEY"))

    llm_obj.classify_order(single_order)






