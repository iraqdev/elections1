from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Location:
    latitude: float
    longitude: float
    name: str


@dataclass
class Event:
    id: str
    title: str
    description: str
    date: datetime
    location: Location
    image_url: Optional[str] = None

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'location': {
                'latitude': self.location.latitude,
                'longitude': self.location.longitude,
                'name': self.location.name
            },
            'image_url': self.image_url
        }

    @staticmethod
    def from_dict(data):
        return Event(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            date=datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S'),
            location=Location(
                latitude=data['location']['latitude'],
                longitude=data['location']['longitude'],
                name=data['location']['name']
            ),
            image_url=data.get('image_url')
        )