# YouTube Transcript Extractor

A Python utility to extract transcripts and metadata from YouTube videos without needing the official YouTube API.

## Features

- ✅ Extract transcripts from any public YouTube video
- ✅ Support for multiple languages
- ✅ Save to plain text or JSON format
- ✅ Optional timestamps in output
- ✅ Error handling for videos without transcripts
- ✅ Works with YouTube URLs and video IDs

## Installation

### Prerequisites
- Python 3.7+
- pip

### Setup

```bash
# Install dependencies
pip install -r requirements-youtube.txt

# Or install directly
pip install youtube-transcript-api==0.6.2
```

## Usage

### Basic Usage

```bash
# Extract from YouTube URL
python youtube_transcript_extractor.py "https://www.youtube.com/watch?v=4v8fyeGegx4"

# Extract from short URL
python youtube_transcript_extractor.py "https://youtu.be/4v8fyeGegx4"

# Extract from video ID
python youtube_transcript_extractor.py "4v8fyeGegx4"
```

### Save to File

```bash
# Save as plain text with timestamps
python youtube_transcript_extractor.py "4v8fyeGegx4" --output transcript.txt

# Save as plain text without timestamps
python youtube_transcript_extractor.py "4v8fyeGegx4" --output transcript.txt --no-timestamps

# Save as JSON (with all metadata)
python youtube_transcript_extractor.py "4v8fyeGegx4" --json transcript.json

# Save both formats
python youtube_transcript_extractor.py "4v8fyeGegx4" --output transcript.txt --json transcript.json
```

### Language Support

```bash
# Get transcript in Spanish
python youtube_transcript_extractor.py "4v8fyeGegx4" --language es

# Get transcript in French
python youtube_transcript_extractor.py "4v8fyeGegx4" --language fr
```

### Help

```bash
python youtube_transcript_extractor.py --help
```

## Examples

**Example 1: Extract and print to console**
```bash
$ python youtube_transcript_extractor.py "https://www.youtube.com/watch?v=4v8fyeGegx4"
Extracting video ID... ✓ (4v8fyeGegx4)
Fetching transcript... ✓ (245 entries)

[00:00] Welcome to the video...
[00:15] Today we'll discuss...
[00:30] Let's get started...
```

**Example 2: Save to file**
```bash
$ python youtube_transcript_extractor.py "4v8fyeGegx4" --output my_transcript.txt
Extracting video ID... ✓ (4v8fyeGegx4)
Fetching transcript... ✓ (245 entries)
✓ Transcript saved to: my_transcript.txt
```

**Example 3: Save as JSON**
```bash
$ python youtube_transcript_extractor.py "4v8fyeGegx4" --json transcript.json
Extracting video ID... ✓ (4v8fyeGegx4)
Fetching transcript... ✓ (245 entries)
✓ Transcript (JSON) saved to: transcript.json
```

## Output Formats

### Plain Text (with timestamps)
```
[00:00] Welcome to the video
[00:15] Today we'll discuss key topics
[00:30] Let's start with the first point
```

### Plain Text (without timestamps)
```
Welcome to the video Today we'll discuss key topics Let's start with the first point
```

### JSON
```json
[
  {
    "text": "Welcome to the video",
    "start": 0.0,
    "duration": 15.0
  },
  {
    "text": "Today we'll discuss key topics",
    "start": 15.0,
    "duration": 15.0
  }
]
```

## Error Handling

The script handles several common scenarios:

- **Video not found**: Invalid video ID or URL
- **Transcripts disabled**: Video owner has disabled transcripts
- **No transcript in requested language**: Falls back to first available language
- **Network errors**: Handled gracefully with error messages

## Limitations

- Only works with public YouTube videos
- Videos must have captions/transcripts enabled by the uploader
- Auto-generated captions may have accuracy issues (typically 90-95% accurate for English)
- API rate limiting may apply for bulk operations

## Use Cases

- 📝 Convert video content to text format
- 📚 Create searchable archives of video content
- 🔍 Extract quotes or specific sections
- 📊 Analyze video content
- ♿ Create accessible transcripts
- 🌐 Generate multi-language versions

## Testing with Your Video

```bash
# Test with the example video
python youtube_transcript_extractor.py "https://youtu.be/4v8fyeGegx4?is=kDBXElAj9AXn6b4a" --output my_transcript.txt
```

## API Reference

### `extract_video_id(url_or_id: str) -> str`
Extracts the video ID from a YouTube URL or validates a direct ID.

### `get_transcript(video_id: str, language: str = 'en') -> List[Dict]`
Fetches the transcript for a given video ID.

### `format_transcript(transcript: List[Dict]) -> str`
Formats transcript entries into readable text.

### `format_transcript_with_timestamps(transcript: List[Dict]) -> str`
Formats transcript with timestamps in MM:SS format.

### `save_transcript(transcript: List[Dict], filename: str, with_timestamps: bool = True)`
Saves transcript to a text file.

### `save_json(transcript: List[Dict], filename: str)`
Saves transcript as JSON file.

## License

This utility uses the `youtube-transcript-api` library which is MIT licensed.

## Notes

- The script respects YouTube's terms of service
- It does not download video content, only metadata that YouTube makes publicly available
- For production use, consider implementing caching to reduce API calls
