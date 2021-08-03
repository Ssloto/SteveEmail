import datetime
import time
import requests

from pytz import timezone
from xml.etree import ElementTree as ET

DEFAULT_TIMEZONE_NAME = "Us/Eastern"

def get_date_from_item(item):
    return datetime.datetime.strptime(item.find("pubDate").text, '%a, %d %b %Y %H:%M:%S +%f')

class SteveRss:
    def __init__(self, rss_text, timezone_name=DEFAULT_TIMEZONE_NAME):
        self.root = ET.fromstring(rss_text)
        self.text = rss_text # save so we can dump this back to an identical file
        self._timestamp_format = '%a, %d %b %Y %H:%M:%S +%f'
        self._timezone = timezone(timezone_name) # odd syntax, but whatever


    def get_last_build_time(self):
        date_as_string = self.root.find("channel").find("lastBuildDate").text
        return self._timezone.localize(datetime.datetime.strptime(date_as_string, self._timestamp_format))


    def get_items(self):
        return [SteveRssItem(item, self._timezone) for item in self.root.find("channel").findall("item")]


    def get_items_newer_than_old(self, compare_steve_rss):
        curr_items = []
        old_tuples = [i.tuple for i in compare_steve_rss.get_items()]
        
        for i in self.get_items():
            if i.tuple not in old_tuples:
                curr_items.append(i)
        
        return curr_items


    @staticmethod
    def from_url(rss_url="https://where-is-steve.org/rss.xml", num_retries=3):
        for i in range(num_retries):
            print(i)
            r = requests.get(rss_url, allow_redirects=True)
            if r.status_code == 200:
                break
                # make sure this terminates the for loop
            elif i == num_retries - 1:
                raise Exception("Could not get RSS feed url. All retries failed.")
            else:
                time.sleep(5)

        return SteveRss(r.text)


class SteveRssItem:
    def __init__(self, xml_node, timezone_obj):
        self._date_format = '%a, %d %b %Y %H:%M:%S +%f'
        self.title = xml_node.find("title").text.strip()
        self.date = timezone_obj.localize(datetime.datetime.strptime(xml_node.find("pubDate").text, self._date_format))
        self.link = xml_node.find("link").text
        self.text = xml_node.find("description").text
        self.tuple = (self.title, self.date, self.link)