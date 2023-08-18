import streamlit as st
import pandas as pd
import subprocess
import os
import threading
import time
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras import switch_page_button
import streamlit_extras
from scrapy.crawler import CrawlerProcess  # Import CrawlerProcess from Scrapy
from spiders.data_info import DataInfoSpider #Import



data_csv_path = 'data_ret.csv'
data_available = threading.Event()

def check_for_csv():
    global data_available
    while True:
        if os.path.exists(data_csv_path):
            print("CSV file found.")
            data_available.set()
        else:
            print("CSV file not found.")
        time.sleep(1)

def main():
    global data_csv_path
    global data_available
    st.title("Step 1: Data Scraping ")

    url = st.text_input("Enter the URL to scrape:")
    tags = st.text_input("Enter HTML tags to scrape data from (comma-separated):").split(',')
    num_columns = st.number_input("Enter the number of columns:", min_value=1, step=1)
    column_headings = [st.text_input(f"Enter heading for column {i+1}:") for i in range(num_columns)]

    if st.button("Scrape Data"):
        if url and tags and num_columns > 0 and len(column_headings) == num_columns:
            #cmd = ['scrapy', 'crawl', 'data_info', '-a', f'url={url}', '-a', f'tags={",".join(tags)}', '-a', f'num_columns={num_columns}', '-a', f'column_headings={",".join(column_headings)}']
            #subprocess.run(cmd)
            process = CrawlerProcess()
            process.crawl(DataInfoSpider, url=url, tags=tags, num_columns=num_columns, column_headings=column_headings)
            process.start()
            st.success("Data scraping started. Please wait for it to finish.")
            data_available.wait()

            if os.path.exists(data_csv_path):
                data_df = pd.read_csv(data_csv_path)
                st.write("Scraped Data:")
                st.write(data_df)
                if st.button("Submit"):
                    switch_page_button("Analysis", "data_analysis.py")
                    with open(data_csv_path, 'rb') as f:
                        st.download_button(
                            label="Download CSV",
                            data=f.read(),
                            file_name='scraped_data.csv',
                            mime='text/csv'
                        )


                if st.button("Try Again"):
                    st.text_input("Enter the URL to scrape:", value="")
                    # Clear other input fields as well
            else:
                st.warning("Data file not found.")

if __name__ == '__main__':
    print("Starting the check_for_csv thread.")
    threading.Thread(target=check_for_csv).start()
    print("Starting the main function.")
    main()

























