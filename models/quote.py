from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Quote:
    id: str
    text: str
    date: datetime
    image_url: Optional[str] = None

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': self.image_url
        }

    @staticmethod
    def from_dict(data):
        return Quote(
            id=data['id'],
            text=data['text'],
            date=datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S'),
            image_url=data.get('image_url')
        )