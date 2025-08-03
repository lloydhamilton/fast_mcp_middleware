from mcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("Booking System")


@mcp.tool()
async def book_table(date: str, party_size: int, ctx: Context) -> str | None:
    """Book a table with confirmation."""
    print(ctx.request_context.request.headers)

    # Schema must only contain primitive types (str, int, float, bool)
    class ConfirmBooking(BaseModel):
        confirm: bool = Field(description="Confirm booking?")
        notes: str = Field(default="", description="Special requests")

    result = await ctx.elicit(
        message=f"Confirm booking for {party_size} on {date}?", schema=ConfirmBooking
    )

    match result:
        case AcceptedElicitation(data=data):
            if data.confirm:
                return f"Booked! Notes: {data.notes or 'None'}"
            return "Booking cancelled"
        case DeclinedElicitation():
            return "Booking declined"
        case CancelledElicitation():
            return "Booking cancelled"

    return None


if __name__ == "__main__":
    import asyncio

    asyncio.run(mcp.run_streamable_http_async())
