import sys
import asyncio

# Fix for Windows asyncio subprocess support
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from .service import Pipeline
import json

async def test(url: str):
    scanner = Pipeline(url)
    result = await scanner.run()

    # for res in result:
        # assert res.value == actual_value
        # pass

    # Convert to JSON-safe format
    safe_result = result.model_dump(mode='json')
    # Write to file
    with open("temp.result.json", "w") as f:
        json.dump(safe_result, f, indent=2, ensure_ascii=False)
    
    print("\nResults successfully saved to result.json")

if __name__ == "__main__":
    site = input("Enter site url : ").strip() or 'https://example.com'
    asyncio.run(
        test(site)
    )
