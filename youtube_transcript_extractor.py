#!/usr/bin/env python3
"""
YouTube Transcript Extractor
Extracts transcripts and metadata from YouTube videos using the youtube-transcript-api library.
"""

import argparse
import json
import sys
import re
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict, List

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
except ImportError:
    print("Error: youtube-transcript-api is not installed.")
    print("Install it with: pip install youtube-transcript-api")
    sys.exit(1)


def extract_video_id(url_or_id: str) -> str:
    """
    Extract video ID from a YouTube URL or return the ID if already provided.

    Supports formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - VIDEO_ID (direct ID)
    """
    # If it looks like a direct video ID (11 characters, alphanumeric with - and _)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id

    try:
        parsed = urlparse(url_or_id)

        # Handle youtu.be short URLs
        if 'youtu.be' in parsed.netloc:
            return parsed.path.lstrip('/')

        # Handle youtube.com URLs
        if 'youtube.com' in parsed.netloc:
            return parse_qs(parsed.query).get('v', [None])[0]
    except Exception:
        pass

    raise ValueError(f"Invalid YouTube URL or video ID: {url_or_id}")


def get_transcript(video_id: str, language: str = 'en') -> List[Dict]:
    """
    Fetch transcript for a YouTube video.

    Args:
        video_id: YouTube video ID
        language: Language code (default: 'en')

    Returns:
        List of transcript entries with 'text' and 'start' timestamps
    """
    api = YouTubeTranscriptApi()
    try:
        # Use the fetch method with languages parameter
        transcript = api.fetch(video_id=video_id, languages=[language])
        return transcript
    except NoTranscriptFound:
        # Try to get available transcripts
        try:
            transcript_list = api.list(video_id)
            available = [t.language for t in transcript_list.manually_created_transcripts]
            available += [t.language for t in transcript_list.generated_transcripts]

            if available:
                print(f"Transcript not available in '{language}'.")
                print(f"Available languages: {', '.join(available)}")
                # Try first available
                transcript = api.fetch(video_id=video_id, languages=[available[0]])
                return transcript
            else:
                raise NoTranscriptFound("No transcripts available for this video")
        except Exception as e:
            raise NoTranscriptFound(f"No transcripts found: {str(e)}")
    except TranscriptsDisabled:
        raise TranscriptsDisabled("Transcripts are disabled for this video")


def format_transcript(transcript: List[Dict]) -> str:
    """Format transcript entries into readable text."""
    return ' '.join([entry['text'] for entry in transcript])


def format_transcript_with_timestamps(transcript: List[Dict]) -> str:
    """Format transcript with timestamps."""
    lines = []
    for entry in transcript:
        timestamp = format_timestamp(entry['start'])
        lines.append(f"[{timestamp}] {entry['text']}")
    return '\n'.join(lines)


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS format."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def save_transcript(transcript: List[Dict], filename: str, with_timestamps: bool = True):
    """Save transcript to file."""
    try:
        if with_timestamps:
            content = format_transcript_with_timestamps(transcript)
        else:
            content = format_transcript(transcript)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✓ Transcript saved to: {filename}")
    except Exception as e:
        print(f"✗ Error saving transcript: {e}")
        sys.exit(1)


def save_json(transcript: List[Dict], filename: str):
    """Save transcript as JSON."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
        print(f"✓ Transcript (JSON) saved to: {filename}")
    except Exception as e:
        print(f"✗ Error saving JSON: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Extract transcripts from YouTube videos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s https://www.youtube.com/watch?v=4v8fyeGegx4
  %(prog)s 4v8fyeGegx4
  %(prog)s https://youtu.be/4v8fyeGegx4 --output transcript.txt
  %(prog)s 4v8fyeGegx4 --json transcript.json
  %(prog)s 4v8fyeGegx4 --no-timestamps
        '''
    )

    parser.add_argument('url_or_id', help='YouTube URL or video ID')
    parser.add_argument('-o', '--output', help='Save transcript to file (default: print to console)')
    parser.add_argument('-j', '--json', help='Save transcript as JSON file')
    parser.add_argument('-l', '--language', default='en', help='Language code (default: en)')
    parser.add_argument('--no-timestamps', action='store_true', help='Remove timestamps from output')

    args = parser.parse_args()

    try:
        # Extract video ID
        print("Extracting video ID...", end=' ')
        video_id = extract_video_id(args.url_or_id)
        print(f"✓ ({video_id})")

        # Fetch transcript
        print("Fetching transcript...", end=' ')
        transcript = get_transcript(video_id, args.language)
        print(f"✓ ({len(transcript)} entries)")

        # Save or print
        if args.json:
            save_json(transcript, args.json)

        if args.output:
            save_transcript(transcript, args.output, with_timestamps=not args.no_timestamps)
        else:
            # Print to console
            if args.no_timestamps:
                print("\n" + format_transcript(transcript))
            else:
                print("\n" + format_transcript_with_timestamps(transcript))

    except ValueError as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    except TranscriptsDisabled:
        print(f"\n✗ Error: Transcripts are disabled for this video")
        sys.exit(1)
    except NoTranscriptFound as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
