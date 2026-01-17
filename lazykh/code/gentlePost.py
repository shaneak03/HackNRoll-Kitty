import requests
import json
import time
import argparse

def align_audio(audio_path, transcript_path, output_path, conservative=False, disfluency=False):
    """Submit form and poll until alignment completes"""
    with open(audio_path, 'rb') as audio_file, open(transcript_path, 'rb') as text_file:
        transcript_bytes = text_file.read()
        files = {'audio': audio_file}
        data = {'transcript': transcript_bytes.decode('utf-8').strip()}
        
        if conservative: data['conservative'] = 'on'
        if disfluency: data['disfluency'] = 'on'
        
        # Step 1: POST to /transcriptions (returns 302 redirect)
        print("Submitting alignment job...")
        response = requests.post(
            'http://localhost:8765/transcriptions',
            files=files,
            data=data,
            allow_redirects=False
        )
        
        # Step 2: Extract job ID from Location header
        if response.status_code != 302:
            print(f"Unexpected status: {response.status_code}")
            print(f"Response body: {response.text[:500]}")
            return False
        
        location = response.headers.get('Location')
        if not location:
            print("No redirect location found")
            return False
        
        # Build the align.json URL from the redirect location
        base_url = 'http://localhost:8765'
        if not location.endswith('/'):
            location = location + '/'
        align_json_url = f"{base_url}{location}align.json"
        
        print(f"Job ID: {location}")
        print(f"Polling: {align_json_url}")
        
        # Step 3: Poll align.json until ready
        max_attempts = 300  # 5 minutes timeout
        for attempt in range(max_attempts):
            time.sleep(1)
            
            try:
                json_response = requests.get(align_json_url)
                
                if json_response.status_code == 200:
                    result = json_response.json()
                    with open(output_path, 'w') as f:
                        json.dump(result, f, indent=2)
                    word_count = len(result.get('words', []))
                    print(f"\nAlignment complete!")
                    print(f"Aligned {word_count} words")
                    print(f"Saved to {output_path}")
                    return True
                    
                elif json_response.status_code == 404:
                    # Still processing
                    if attempt % 10 == 0 and attempt > 0:
                        print(f"Still processing... ({attempt}s elapsed)")
                    continue
                    
                else:
                    print(f"\nUnexpected status on align.json: {json_response.status_code}")
                    print(f"Response: {json_response.text[:200]}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                print(f"\nNetwork error polling: {e}")
                return False
            except json.JSONDecodeError as e:
                print(f"\nJSON decode error: {e}")
                print(f"Response text: {json_response.text[:200]}")
                return False
        
        print("\nTimeout waiting for alignment (5 minutes exceeded)")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Align audio with transcript using Gentle server')
    parser.add_argument('audio', type=str, help='Path to audio file')
    parser.add_argument('transcript', type=str, help='Path to transcript file')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output JSON file path')
    parser.add_argument('--conservative', action='store_true', help='Use conservative alignment')
    parser.add_argument('--disfluency', action='store_true', help='Include disfluencies')
    args = parser.parse_args()
    
    success = align_audio(
        audio_path=args.audio,
        transcript_path=args.transcript,
        output_path=args.output,
        conservative=args.conservative,
        disfluency=args.disfluency
    )
    
    exit(0 if success else 1)