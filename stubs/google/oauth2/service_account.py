from typing import Any, Iterable, Mapping, Optional


class Credentials:
    @classmethod
    def from_service_account_info(
        cls,
        info: Mapping[str, Any],
        *,
        scopes: Optional[Iterable[str]] = None,
    ) -> "Credentials":
        raise NotImplementedError
