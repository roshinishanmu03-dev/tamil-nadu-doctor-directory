"""Crawl permitted directory pages and read public structured doctor data."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any, Iterator
import scrapy
from bs4 import BeautifulSoup

class DoctorsSpider(scrapy.Spider):
    name = "doctors"
    allowed_domains = ["justdial.com"]
    def __init__(self, start_url: str | None = None, max_pages: str = "1", *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        if not start_url: raise ValueError("Provide one permitted listing URL: -a start_url='https://www.justdial.com/…'")
        self.start_urls=[start_url]; self.max_pages=max(1,int(max_pages)); self.pages_seen=0
    def parse(self,response: scrapy.http.Response)->Iterator[dict[str,Any]|scrapy.Request]:
        self.pages_seen+=1; soup=BeautifulSoup(response.text,"lxml"); records=list(self._json_ld_records(soup))
        if not records: self.logger.warning("No usable public JSON-LD records on %s. Inspect permitted HTML and add selectors.",response.url)
        for record in records:
            record["source_url"]=response.url; record["scraped_at_utc"]=datetime.now(timezone.utc).isoformat(); yield record
        next_link=soup.select_one('a[rel="next"]')
        if next_link and next_link.get("href") and self.pages_seen<self.max_pages: yield response.follow(next_link["href"],callback=self.parse)
    def _json_ld_records(self,soup:BeautifulSoup)->Iterator[dict[str,Any]]:
        for script in soup.select('script[type="application/ld+json"]'):
            raw=script.string or script.get_text(strip=True)
            if not raw: continue
            try: payload=json.loads(raw)
            except json.JSONDecodeError: continue
            for entity in self._walk_entities(payload):
                if not self._is_doctor_or_clinic(entity): continue
                address=entity.get("address") or {}; rating=entity.get("aggregateRating") or {}
                yield {"doctor_or_clinic_name":self._text(entity.get("name")),"specialty":self._text(entity.get("medicalSpecialty")),"address_locality":self._text(address.get("addressLocality")),"address_region":self._text(address.get("addressRegion")),"postal_code":self._text(address.get("postalCode")),"rating":self._text(rating.get("ratingValue")),"review_count":self._text(rating.get("reviewCount")),"profile_url":self._text(entity.get("url"))}
    def _walk_entities(self,value:Any)->Iterator[dict[str,Any]]:
        if isinstance(value,dict):
            yield value
            for child in value.values(): yield from self._walk_entities(child)
        elif isinstance(value,list):
            for child in value: yield from self._walk_entities(child)
    @staticmethod
    def _is_doctor_or_clinic(entity:dict[str,Any])->bool:
        types=entity.get("@type",[]); types=[types] if isinstance(types,str) else types
        return bool({"Physician","MedicalClinic","MedicalBusiness","Dentist"}.intersection(types)) and bool(entity.get("name"))
    @staticmethod
    def _text(value:Any)->str|None: return str(value).strip() if value not in (None,"") else None