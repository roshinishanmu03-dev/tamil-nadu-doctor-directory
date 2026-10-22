import unittest
from scrapy.http import TextResponse
from doctor_directory.spiders.doctors import DoctorsSpider
class DoctorsSpiderTests(unittest.TestCase):
    def test_extracts_public_json_ld_fields(self):
        html='''<script type="application/ld+json">{"@type":"Physician","name":"Dr Ada","medicalSpecialty":"Cardiology","address":{"addressLocality":"Chennai","addressRegion":"TN","postalCode":"600001"},"aggregateRating":{"ratingValue":"4.8","reviewCount":"12"},"url":"https://example.org/ada"}</script>'''
        response=TextResponse("https://www.justdial.com/chennai/example",body=html.encode(),encoding="utf-8")
        results=list(DoctorsSpider(start_url="https://www.justdial.com/chennai/example").parse(response))
        self.assertEqual(len(results),1); self.assertEqual(results[0]["doctor_or_clinic_name"],"Dr Ada"); self.assertEqual(results[0]["address_locality"],"Chennai"); self.assertEqual(results[0]["review_count"],"12"); self.assertEqual(results[0]["source_url"],response.url); self.assertIsNotNone(results[0]["scraped_at_utc"])