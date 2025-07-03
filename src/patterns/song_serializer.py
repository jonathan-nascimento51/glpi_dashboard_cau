"""Factory Method pattern example for serializing songs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Callable
import json
import xml.etree.ElementTree as ET
import yaml


@dataclass
class Song:
    title: str
    artist: str


class Serializer(Protocol):
    def __call__(self, song: Song) -> str: ...


def _serialize_to_json(song: Song) -> str:
    return json.dumps({"title": song.title, "artist": song.artist})


def _serialize_to_xml(song: Song) -> str:
    root = ET.Element("song")
    ET.SubElement(root, "title").text = song.title
    ET.SubElement(root, "artist").text = song.artist
    return ET.tostring(root, encoding="unicode")


def _serialize_to_yaml(song: Song) -> str:
    return yaml.dump({"title": song.title, "artist": song.artist})


_SERIALIZERS: dict[str, Serializer] = {
    "json": _serialize_to_json,
    "xml": _serialize_to_xml,
    "yaml": _serialize_to_yaml,
}


def get_serializer(fmt: str) -> Serializer:
    try:
        return _SERIALIZERS[fmt]
    except KeyError as exc:
        raise ValueError(f"Unsupported format: {fmt}") from exc


def serialize(song: Song, fmt: str) -> str:
    serializer = get_serializer(fmt)
    return serializer(song)
