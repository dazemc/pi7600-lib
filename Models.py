from typing import Optional
from pydantic import BaseModel, ConfigDict


class Messages(BaseModel):
    id: Optional[int] = None
    message_index: Optional[str] = None
    message_type: str
    message_originating_address: Optional[str] = None
    message_destination_address: Optional[str] = None
    message_date: str
    message_time: str
    message_contents: str
    partial_key: Optional[str] = None
    partial_count: Optional[int] = None
    partial_number: Optional[int] = None
    is_partial: bool
    in_sim_memory: bool
    is_sent: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)