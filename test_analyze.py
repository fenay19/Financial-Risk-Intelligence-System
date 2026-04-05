import sys
import asyncio
import traceback
from app.routers.analyze import analyze_query
from app.models import AnalyzeRequest

async def main():
    req = AnalyzeRequest(q="tcs", refresh=True)
    try:
        report = await analyze_query(req)
        print("Success!")
    except Exception as e:
        traceback.print_exc(file=sys.stdout)

asyncio.run(main())
