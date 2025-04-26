from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class News:
    id: str
    title: str
    content: str
    date: datetime
    image_url: Optional[str] = None
    is_urgent: bool = False

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': self.image_url,
            'is_urgent': self.is_urgent
        }

    @staticmethod
    def from_dict(data):
        return News(
            id=data['id'],
            title=data['title'],
            content=data['content'],
            date=datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S'),
            image_url=data.get('image_url'),
            is_urgent=data.get('is_urgent', False)
        )