import os
from google.oauth2 import service_account
from google.cloud import aiplatform
from google import genai
import pandas as pd



class GeminiModel:

    def __init__(self, api_key):
        self.api_key = api_key
        self.summary_prompt = "Create a 30 word summary of the following executive order: "
        self.classification_prompt = "Classify this executive order into one of the following issues that it is attempting to solve: "
        self.orders = None
        self.issues = """inflation, jobs and wages, housing affordability, government spending, taxation, healthcare, 
                  education, crime, gun control, drug crisis, homelessness, social security, medicare, political polarization
                  election integrity, government corruption, election integrity, immigration, free speech, climate change, 
                  energy policy, infrastructure, China, Russia, Middle East, LGBTQ+ rights"""
        

    def summarize_executive_order(self, order_text):
        """
            Summarize a single executive order. 
        """

        client = genai.Client(api_key=self.api_key)

        response = client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=[self.summary_prompt + order_text]
        )
        final = ""
        for chunk in response:
            print(chunk.text, end="")
            final += chunk.text

        return final
    
    def read_in_all_orders(self, path_to_csv):
        self.orders = pd.read_csv(path_to_csv)


    def classify_order(self, order):
        """
            Summarize a single executive order. 
        """

        client = genai.Client(api_key=self.api_key)

        response = client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=[self.classification_prompt + self.issues + order]
        )
        final = ""
        for chunk in response:
            print(chunk.text, end="")
            final += chunk.text

        return final

    def classify_all_orders(self, orders):
        pass



