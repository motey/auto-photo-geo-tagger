# comparable
from gpxpy.gpx import GPXTrackPoint


class GPXTrackPointComparable(GPXTrackPoint):
    def __eq__(self, other):
        return (
            self.time == other.time
            and self.latitude == other.latitude
            and self.longitude == other.longitude
        )

    def __hash__(self) -> int:
        return hash((self.time, self.latitude, self.longitude))

    @classmethod
    def from_GPXTrackPoint(cls, p):
        p.__class__ = cls
        return p
