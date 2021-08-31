import sys
import datetime
import logging
import azure.functions as func
import traceback
from azure.cosmosdb.table.tableservice import TableService

from steve_constants import ACCOUNT_KEY, ACCOUNT_NAME, TEST_MODE, IGNORE_FETCH, \
    BLOB_RSS_CONTAINER, BLOB_RSS_FILENAME
from steve_blob import SteveBlob
from steve_email import SteveBulkEmail
from steve_rss import SteveRss
from steve_table import SteveTable

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')


    steve_table = SteveTable()
    
    last_succeeded_timestamp = steve_table.get_last_succeeded_timestamp()
    srss = SteveRss.from_url(rss_url="https://where-is-steve.org/rss.xml", num_retries=3)

    if IGNORE_FETCH:
        logging.info("We are ignoring site update information.")        
    elif srss.get_last_build_time() < last_succeeded_timestamp:
        steve_table.update_last_succeed_timestamp()
        logging.info("Site has not been updated since last run.")        
        return
    else:
        logging.info("Site has been updated since last run.")        


    # We've passed our first check and have decided to continue...

    # Because our timestamps are daily & not day-hour-minutely,
    # we can't distinguish between content we've seen already unless...
    # we have a cached old copy of the rss XML, which we will now retrieve.
    
    remote_rss = SteveBlob(ACCOUNT_NAME, BLOB_RSS_CONTAINER, BLOB_RSS_FILENAME, ACCOUNT_KEY)
    old_srss = SteveRss(remote_rss.read_blob_to_text())

    if TEST_MODE and IGNORE_FETCH:
        new_items = srss.get_items()[:1]
    else:   
        new_items = srss.get_items_newer_than_old(old_srss)
    
    new_item_count = len(new_items)

    if new_item_count == 0:
        logging.info("There were no new items.")
        steve_table.update_last_succeed_timestamp()
        
    recipients = steve_table.get_email_subscribers()
    sbe = SteveBulkEmail(recipients)

    if new_item_count > 1:
        sbe.set_subject("{} new updates!".format(new_item_count))
    else:
        sbe.set_subject(new_items[0].title)

    for item in new_items:
        sbe.add_item(item.title, item.date, item.text, item.link)

    sbe.finalize_contents()
    sbe.send()

    # update our cached RSS XML -- if this fails then we will have a serious ish
    remote_rss.write_blob(srss.text)
    steve_table.update_last_succeed_timestamp()


if __name__ == "__main__":
    main()