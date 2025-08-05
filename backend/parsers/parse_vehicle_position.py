#!/usr/bin/env python3

from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToJson
import sys

def main(pb_file):
    # Create a GTFS-Realtime FeedMessage object
    feed = gtfs_realtime_pb2.FeedMessage()
    
    # Read the .pb file in binary mode
    with open(pb_file, 'rb') as f:
        feed.ParseFromString(f.read())

    # Convert the feed to JSON (without including default values)
    json_str = MessageToJson(feed)
    print(json_str)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} VehiclePosition.pb")
        sys.exit(1)
    main(sys.argv[1])
