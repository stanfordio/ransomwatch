from typing import Dict, List

from sqlalchemy.orm.session import Session as SessionType

from db.database import Session
from db.models import Site, Victim
from net.proxy import Proxy

class SiteCrawler:
    # threat actor associated with the leak site
    actor: str = ""

    # url for the leak site
    url: str = ""

    # list of victims on the leak site from current scrape
    current_victims: List[Victim] = []

    # new victims on the leak site from current scrape
    new_victims: List[Victim] = []

    # is the site up? set by is_site_up()
    is_up: bool = False

    # db session, set in __init__()
    session: SessionType

    # site object from db, set in __init__()
    site: Site

    # is this the first ingest of the site? set in __init__()
    # if the first run, don't notify on new victims (b/c they are all "new")
    first_run: bool = False
    
    headers: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0"
    }

    def __init__(self, url: str):
        """
        make sure site is in db
        check if site is up
            if it is, update last_up in db
        """

        # this should be statically defined in child implementations of the class
        assert self.actor != ""

        self.url = url

        self.session = Session()

        q = self.session.query(Site).filter_by(actor=self.actor)

        if q.count() == 0:
            # site is new, init obj
            self.site = Site(actor=self.actor, url=self.url)
            self.session.add(self.site)
            self.session.commit()
            self.first_run = True
        else:
            # site exists, set obj
            self.site = q.first()

        # check if site is up
        self.is_up = self.is_site_up()

    def is_site_up(self) -> bool:
        """
        check if the site is up

        this might have specific criteria for some sites
        """

        with Proxy() as p:
            try:
                r = p.get(self.url, headers=self.headers, timeout=20)

                if r.status_code >= 400:
                    return False
            except Exception as e:
                return False

        return True

    def scrape_victims(self):
        """
        pull each listing on the site
        check if its already in the db
            if it is, update the last seen
            if it isn't, add it to the db

        store each org name in a list (self.current_victims)

        this also sets self.new_victims, which has new victims to notify with
        """
        pass

    def identify_removed_victims(self) -> List[Victim]:
        """
        check org name list against db
            if something is in the db and not in the list, alert
        """
        db_victims = self.session.query(Victim).filter_by(site=self.site).all()
        
        victims = self.current_victims.copy()
        
        for v in db_victims:
            victims.remove(v)

        return victims