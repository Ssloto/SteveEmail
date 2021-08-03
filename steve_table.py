from azure.cosmosdb.table.tableservice import TableService
from steve_constants import ACCOUNT_KEY, TEST_MODE

class SteveTable():
    def __init__(self, account_key=ACCOUNT_KEY, test_mode=TEST_MODE):
        self._test_mode = test_mode
        self.service = TableService(account_name='steveemail', account_key=account_key)
        self.table_name = "SteveSubscribers"
        self.timestamp_row_key = "test" if self._test_mode else "00"

        self.pending_subscribers_partion_key = "testPendingEmail" if self._test_mode else "pendingEmail"
        self.subscribers_partition_key = "testEmail" if self._test_mode else "email"
        self.timestamp_partition_key = "lastSent"


    def get_last_succeeded_timestamp(self):
        # Hilariously, my method of marking when this succeeded last is to retrieve a single, special row of the subscriber db,
        # which contains no data, but which we will update at the end of each successful run... b.c. it updates the timestamp
        # Yes, this is dumb.
        return self.service.get_entity(self.table_name, self.timestamp_partition_key, self.timestamp_row_key)["Timestamp"]


    def update_last_succeed_timestamp(self):
        last_sent_entity = self.service.get_entity(self.table_name, self.timestamp_partition_key, self.timestamp_row_key)
        self.service.update_entity(self.table_name, last_sent_entity)


    def get_email_subscribers(self):
        # NOTE: this will not scale > 1000 emails
        # as per: https://stackoverflow.com/questions/28019437/python-querying-all-rows-of-azure-table
        subscribers = [email.RowKey for email in 
            self.service.query_entities(self.table_name, 
            filter="PartitionKey eq '{}'".format(self.subscribers_partition_key))]
        assert len(subscribers) > 0, "We must have subscribers!"
        return subscribers

    def add_pending_subscriber(self, email_address):
        self.service.insert_or_replace_entity(self.table_name, {"PartitionKey": self.pending_subscribers_partion_key, 
                                                                "RowKey": email_address})

    def add_subscriber(self, email_address):
        # check that a pending subscriber entry exists...
        # basically, this will throw if it doesn't and we'll wrap our call to add_subscriber in a try/except
        self.service.get_entity(self.table_name, self.pending_subscribers_partion_key, email_address)

        # if so, we can now add a real entry
        self.service.insert_or_replace_entity(self.table_name, {"PartitionKey": self.subscribers_partition_key, 
                                                                "RowKey": email_address})
        # and delete our pending one...
        self.service.delete_entity(self.table_name, self.pending_subscribers_partion_key, email_address)
        
        # thus blocking this from happening again


    def remove_subscriber(self, email_address):
        self.service.delete_entity(self.table_name, self.subscribers_partition_key, email_address)
