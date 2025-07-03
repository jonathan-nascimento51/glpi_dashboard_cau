from dataclasses import dataclass

@dataclass
class ToolError:
    """Structured error returned by automation tools."""

    message: str
    details: str

    def dict(self) -> dict[str, str]:
        """Return a serializable representation."""
        return {"message": self.message, "details": self.details}
