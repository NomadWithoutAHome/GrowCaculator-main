"""
Pydantic models for calculator requests and responses.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PlantData(BaseModel):
    """Plant data model."""
    name: str
    base_weight: float
    base_price: int
    rarity: int


class VariantData(BaseModel):
    """Variant data model."""
    name: str
    multiplier: int


class MutationData(BaseModel):
    """Mutation data model."""
    name: str
    value_multi: int


class CalculationRequest(BaseModel):
    """Request model for plant value calculation."""
    plant_name: str = Field(..., description="Name of the plant")
    variant: str = Field(default="Normal", description="Plant variant")
    weight: float = Field(..., gt=0, description="Weight in kg")
    mutations: List[str] = Field(default=[], description="List of mutation names")
    plant_amount: int = Field(default=1, ge=1, le=10000, description="Number of plants")
    fruit_version: int = Field(default=0, ge=0, le=2, description="Fruit version (0=none, 1=capped, 2+=interpolated)")


class CalculationResponse(BaseModel):
    """Response model for plant value calculation."""
    plant_name: str
    variant: str
    weight: float
    mutations: List[str]
    mutation_multiplier: float
    base_value: float
    weight_ratio: float
    final_value: int
    plant_amount: int
    total_value: int  # final_value * plant_amount
    fruit_version: int
    uncapped_value: int  # Value before fruit version capping/interpolation
    capped_value: int  # Value after fruit version logic (for display)
    is_capped: bool  # Whether the value was affected by fruit version logic


class PlantListResponse(BaseModel):
    """Response model for plant list."""
    plants: List[str]


class VariantListResponse(BaseModel):
    """Response model for variant list."""
    variants: List[VariantData]


class MutationListResponse(BaseModel):
    """Response model for mutation list."""
    mutations: List[MutationData]


class SharedResult(BaseModel):
    """Model for shared calculation results."""
    share_id: str = Field(..., description="Unique share identifier")
    plant: str = Field(..., description="Plant name")
    variant: str = Field(..., description="Plant variant")
    mutations: List[str] = Field(default=[], description="List of mutations")
    weight: float = Field(..., description="Plant weight in kg")
    amount: int = Field(..., description="Number of plants")
    result_value: str = Field(..., description="Formatted result value")
    final_sheckles: str = Field(..., description="Final sheckles value")
    total_value: str = Field(..., description="Total value for all plants")
    total_multiplier: str = Field(..., description="Total mutation multiplier")
    mutation_breakdown: str = Field(..., description="Mutation breakdown description")
    weight_min: str = Field(..., description="Minimum weight range")
    weight_max: str = Field(..., description="Maximum weight range")
    fruit_version: int = Field(default=0, description="Fruit version used in calculation")
    uncapped_value: int = Field(default=0, description="Calculated value before fruit version capping")
    is_capped: bool = Field(default=False, description="Whether the value was capped by fruit version logic")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp (24 hours from creation)")


class BatchPlant(BaseModel):
    """Model for individual plant in batch results."""
    plant: str = Field(..., description="Plant name")
    variant: str = Field(..., description="Plant variant")
    weight: float = Field(..., description="Plant weight in kg")
    quantity: int = Field(..., description="Number of this plant")
    mutations: List[str] = Field(default=[], description="List of mutations")
    result: float = Field(..., description="Value per plant")
    total: float = Field(..., description="Total value for this plant type")


class BatchSharedResult(BaseModel):
    """Model for shared batch calculation results."""
    share_id: str = Field(..., description="Unique share identifier")
    type: str = Field(default="batch", description="Result type")
    plants: List[BatchPlant] = Field(..., description="List of plants in batch")
    total_value: float = Field(..., description="Total value of all plants")
    total_plants: int = Field(..., description="Total number of plants")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp (24 hours from creation)")


class SharedResultResponse(BaseModel):
    """Response model for shared result retrieval."""
    success: bool
    data: Optional[SharedResult] = None
    error: Optional[str] = None


class BatchSharedResultResponse(BaseModel):
    """Response model for batch shared result retrieval."""
    success: bool
    data: Optional[BatchSharedResult] = None
    error: Optional[str] = None
