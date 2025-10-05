from __future__ import annotations

from dataclasses import dataclass

from supabase import Client, create_client


@dataclass(frozen=True)
class SupabaseHandle:
    client: Client
    schema: str


def make_supabase(url: str, key: str, schema: str = "public") -> SupabaseHandle:
    # Normalize to avoid double slashes in REST paths
    url = url.rstrip("/")
    client: Client = create_client(url, key)
    return SupabaseHandle(client=client, schema=schema)


