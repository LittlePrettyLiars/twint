from . import feed, get, db, output, elasticsearch
from bs4 import BeautifulSoup
import asyncio
import re
import sys

class Followers:
    def __init__(self, config):
        self.init = -1
        self.feed = [-1]
        self.count = 0
        self.config = config
        
        if self.config.Elasticsearch:
            print("[+] Indexing to Elasticsearch @ " + str(self.config.Elasticsearch))

        if self.config.Database:
            print("[+] Inserting into Database: " + str(self.config.Database))
            self.conn = db.init(self.config.Database)
            if isinstance(self.conn, str):
                print(str)
                sys.exit(1)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main())

    async def Feed(self):
        url = await get.Url(self.config, self.init).followers()
        response = await get.MobileRequest(self.config, url)
        self.feed = []
        try:
            self.feed, self.init = feed.Follow(response)
        except:
            pass

        return self.feed

    async def follower(self):
        await self.Feed()
        for f in self.feed:
            User = await output.getUser(f)
            if self.config.Database:
                db.followers(self.conn, self.config.Username, User.name)

            if self.config.Output != None:
                output.write(User.name, self.config.Output)

            if self.config.Elasticsearch:
                elasticsearch.Follow(self.config.Elasticsearch, User.name,
                        self.config.Username, self.config.Essid)

            self.count += 1
            print(User.name)

    async def main(self):
        if self.config.User_id is not None:
            self.config.Username = await get.Username(self.config)

        while True:
            if len(self.feed) > 0:
                await self.follower()
            else:
                break

            if self.config.Limit is not None and self.count >= int(self.config.Limit):
                break

        if self.config.Count:
            print("[+] Finished: Successfully collected all {0.count} users who follow @{0.config.Username}.".format(self))
