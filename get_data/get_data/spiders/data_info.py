import scrapy
import csv
from urllib.parse import urlparse

class DataInfoSpider(scrapy.Spider):
    name = 'data_info'
    allowed_domains = []  # We will set this dynamically
    start_urls = []

    def __init__(self, url=None, tags=None, num_columns=None, column_headings=None, *args, **kwargs):
    super(DataInfoSpider, self).__init__(*args, **kwargs)
    if url:
        self.start_urls = [url]
        parsed_url = urlparse(url)
        self.allowed_domains = [parsed_url.netloc]  # Extract and set the domain

    if tags is not None:
        self.tags = tags.split(',')  # Convert to a list
    else:
        self.tags = []
        
    self.num_columns = int(num_columns)
    self.column_headings = column_headings.split(',') if column_headings else []  # Convert to a list


    def parse(self, response):
        css_selectors = [f'{tag}::text' for tag in self.tags]

        # Extract column headings
        column_headings = self.column_headings

        # Extract data items
        data_items = response.css(','.join(css_selectors)).getall()

        csv_file_path = 'data_ret.csv'

        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_headings)  # Write column headings

            for i in range(0, len(data_items), self.num_columns):
                row_data = data_items[i:i + self.num_columns]
                writer.writerow(row_data)

        return {'message': 'CSV file generated successfully.'}















