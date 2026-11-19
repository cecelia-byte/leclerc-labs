"""The ONLY place in our app that talks to OpenF1."""

import httpx
from fastapi import HTTPException

from app import config
from app.services.cache import TTLCache


class OpenF1Client:
    def __init__(self) -> None:
        self._http = httpx.Client(
            base_url=config.OPENF1_BASE_URL,
            timeout=config.OPENF1_TIMEOUT_SECONDS,
            headers={"Accept": "application/json"},
        )
        self._cache = TTLCache()

    def get(
        self,
        path: str,
        *,
        params: dict[str, str | int] | None,
        cache_key: str,
        ttl_seconds: int,
    ) -> list[dict]:
        """Fetch a JSON list from OpenF1, using the cache when possible."""
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            response = self._http.get(path, params=params)
            response.raise_for_status()
            payload = response.json()
        except httpx.TimeoutException as exc:
            raise HTTPException(status_code=504, detail="OpenF1 took too long to respond") from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                raise HTTPException(
                    status_code=503,
                    detail="OpenF1 rate limit reached. Please retry shortly.",
                ) from exc
            raise HTTPException(
                status_code=502,
                detail=f"OpenF1 returned HTTP {exc.response.status_code}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Could not reach OpenF1") from exc
        except ValueError as exc:
            raise HTTPException(status_code=502, detail="OpenF1 returned invalid JSON") from exc

        if not isinstance(payload, list):
            raise HTTPException(status_code=502, detail="Unexpected response shape from OpenF1")

        self._cache.set(cache_key, payload, ttl_seconds)
        return payload

    def get_meetings(self, year: int | None = None) -> list[dict]:
        """All meetings, or just one season when `year` is supplied."""
        return self.get(
            "/meetings",
            params={"year": year} if year is not None else None,
            cache_key=f"meetings:{year if year is not None else 'all'}",
            ttl_seconds=config.CACHE_TTL_SEASONS_SECONDS,
        )

    def get_sessions(self, meeting_key: int) -> list[dict]:
        """Every session belonging to one Grand Prix weekend."""
        return self.get(
            "/sessions",
            params={"meeting_key": meeting_key},
            cache_key=f"sessions:{meeting_key}",
            ttl_seconds=config.CACHE_TTL_SEASONS_SECONDS,
        )

    def get_sessions_by_year(self, year: int) -> list[dict]:
        """Every session in one season — one call instead of one per meeting."""
        return self.get(
            "/sessions",
            params={"year": year},
            cache_key=f"sessions:year:{year}",
            ttl_seconds=config.CACHE_TTL_SEASONS_SECONDS,
        )

    def get_session_result(self, session_key: int) -> list[dict]:
        """Official classification for one session."""
        return self.get(
            "/session_result",
            params={"session_key": session_key},
            cache_key=f"result:{session_key}",
            ttl_seconds=config.CACHE_TTL_RESULTS_SECONDS,
        )

    def get_session_results_by_meeting(self, meeting_key: int) -> list[dict]:
        """All session classifications for one weekend, including qualifying."""
        return self.get(
            "/session_result",
            params={"meeting_key": meeting_key},
            cache_key=f"result:meeting:{meeting_key}",
            ttl_seconds=config.CACHE_TTL_RESULTS_SECONDS,
        )

    def get_drivers(self, session_key: int) -> list[dict]:
        """Driver names, numbers and team colours for one session."""
        return self.get(
            "/drivers",
            params={"session_key": session_key},
            cache_key=f"drivers:{session_key}",
            ttl_seconds=config.CACHE_TTL_RESULTS_SECONDS,
        )

    def get_drivers_for_meeting(self, meeting_key: int) -> list[dict]:
        """Driver metadata for every entrant at one weekend."""
        return self.get(
            "/drivers",
            params={"meeting_key": meeting_key},
            cache_key=f"drivers:meeting:{meeting_key}",
            ttl_seconds=config.CACHE_TTL_RESULTS_SECONDS,
        )

    def get_starting_grid(self, session_key: int) -> list[dict]:
        """Starting positions, keyed by the QUALIFYING session key."""
        return self.get(
            "/starting_grid",
            params={"session_key": session_key},
            cache_key=f"grid:{session_key}",
            ttl_seconds=config.CACHE_TTL_RESULTS_SECONDS,
        )

    def get_laps(self, session_key: int) -> list[dict]:
        """Every recorded lap in one session — one call for all drivers."""
        return self.get(
            "/laps",
            params={"session_key": session_key},
            cache_key=f"laps:{session_key}",
            ttl_seconds=config.CACHE_TTL_RESULTS_SECONDS,
        )

    def get_stints(self, session_key: int) -> list[dict]:
        """Tyre stints for one session, including compound and lap range."""
        return self.get(
            "/stints",
            params={"session_key": session_key},
            cache_key=f"stints:{session_key}",
            ttl_seconds=config.CACHE_TTL_RESULTS_SECONDS,
        )

    def get_car_data(
        self,
        session_key: int,
        driver_number: int,
        date_start: str,
        date_end: str,
    ) -> list[dict]:
        """Car sensor samples for one driver inside a lap's UTC time window."""
        return self.get(
            "/car_data",
            params={
                "session_key": session_key,
                "driver_number": driver_number,
                "date>": date_start,
                "date<": date_end,
            },
            cache_key=(
                f"car_data:{session_key}:{driver_number}:{date_start}:{date_end}"
            ),
            ttl_seconds=config.CACHE_TTL_RESULTS_SECONDS,
        )


# One shared instance for the whole process, so the cache is shared too.
client = OpenF1Client()
