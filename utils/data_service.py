import json
import os
import uuid
from datetime import datetime
from models.news import News
from models.event import Event, Location
from models.quote import Quote


class DataService:
    def __init__(self):
        self.news_file = "data/news.json"
        self.events_file = "data/events.json"
        self.quotes_file = "data/quotes.json"
        self._ensure_directories_exist()

    def _ensure_directories_exist(self):
        os.makedirs(os.path.dirname(self.news_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.events_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.quotes_file), exist_ok=True)

        if not os.path.exists(self.news_file):
            with open(self.news_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

        if not os.path.exists(self.events_file):
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

        if not os.path.exists(self.quotes_file):
            with open(self.quotes_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    # خدمات الأخبار
    def get_news(self, limit=10):
        try:
            with open(self.news_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)

            news_items = [News.from_dict(item) for item in news_data]
            news_items.sort(key=lambda x: x.date, reverse=True)

            return news_items[:limit]
        except Exception as e:
            print(f"Error loading news: {e}")
            return []

    def add_news(self, title, content, image_url=None, is_urgent=False):
        try:
            with open(self.news_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)

            news_id = str(uuid.uuid4())
            news_item = News(
                id=news_id,
                title=title,
                content=content,
                date=datetime.now(),
                image_url=image_url,
                is_urgent=is_urgent
            )

            news_data.append(news_item.to_dict())

            with open(self.news_file, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False)

            return news_item
        except Exception as e:
            print(f"Error adding news: {e}")
            return None

    # خدمات الفعاليات
    def get_events(self, limit=10):
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events_data = json.load(f)

            events = [Event.from_dict(item) for item in events_data]
            events.sort(key=lambda x: x.date)

            return events[:limit]
        except Exception as e:
            print(f"Error loading events: {e}")
            return []

    def add_event(self, title, description, date, latitude, longitude, location_name, image_url=None):
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events_data = json.load(f)

            event_id = str(uuid.uuid4())
            location = Location(latitude=latitude, longitude=longitude, name=location_name)

            event = Event(
                id=event_id,
                title=title,
                description=description,
                date=date,
                location=location,
                image_url=image_url
            )

            events_data.append(event.to_dict())

            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(events_data, f, ensure_ascii=False)

            return event
        except Exception as e:
            print(f"Error adding event: {e}")
            return None

    # خدمات الاقتباسات
    def get_daily_quote(self):
        try:
            with open(self.quotes_file, 'r', encoding='utf-8') as f:
                quotes_data = json.load(f)

            if not quotes_data:
                return None

            quotes = [Quote.from_dict(item) for item in quotes_data]
            quotes.sort(key=lambda x: x.date, reverse=True)

            return quotes[0]
        except Exception as e:
            print(f"Error loading daily quote: {e}")
            return None

    def add_quote(self, text, image_url=None):
        try:
            with open(self.quotes_file, 'r', encoding='utf-8') as f:
                quotes_data = json.load(f)

            quote_id = str(uuid.uuid4())
            quote = Quote(
                id=quote_id,
                text=text,
                date=datetime.now(),
                image_url=image_url
            )

            quotes_data.append(quote.to_dict())

            with open(self.quotes_file, 'w', encoding='utf-8') as f:
                json.dump(quotes_data, f, ensure_ascii=False)

            return quote
        except Exception as e:
            print(f"Error adding quote: {e}")
            return None