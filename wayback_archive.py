from typing import Optional
from urllib.parse import quote


class Tools:
    def __init__(self):
        pass

    async def build_wayback_cdx_url(self, target_url: str, limit: int = 15) -> str:
        """
        Builds the Wayback Machine CDX API URL to discover available snapshots.
        Use this first when a website is blocked or returns no content.
        Returns a ready-to-use CDX search URL (JSON output).
        """
        if not target_url:
            return "Error: target_url is required"

        encoded_url = quote(target_url, safe="")
        cdx_url = (
            f"https://web.archive.org/cdx/search/cdx"
            f"?url={encoded_url}"
            f"&output=json"
            f"&limit={limit}"
            f"&filter=statuscode:200"
            f"&collapse=digest"
        )
        return cdx_url

    async def build_wayback_archive_url(self, target_url: str, timestamp: str) -> str:
        """
        Builds a direct Wayback Machine archive snapshot URL for a specific timestamp.
        Timestamp format must be YYYYMMDDHHMMSS (14 digits).
        Example: 20250412143000
        Use this after you have chosen a good timestamp from the CDX results.
        """
        if not target_url or not timestamp:
            return "Error: Both target_url and timestamp are required"

        # Clean up timestamp if user adds extra characters
        timestamp = "".join(filter(str.isdigit, timestamp))

        if len(timestamp) != 14:
            return f"Error: Timestamp must be exactly 14 digits (YYYYMMDDHHMMSS). Got: {timestamp}"

        archive_url = f"https://web.archive.org/web/{timestamp}/{target_url}"
        return archive_url

    # Optional: You can also add this helper method if you want one-call convenience
    async def get_wayback_snapshot_url(
        self, target_url: str, timestamp: Optional[str] = None
    ) -> str:
        """
        Convenience method.
        - If you provide a timestamp → returns the direct archive URL.
        - If you don't provide a timestamp → returns the CDX discovery URL instead.
        """
        if timestamp:
            return await self.build_wayback_archive_url(target_url, timestamp)
        else:
            return await self.build_wayback_cdx_url(target_url)
