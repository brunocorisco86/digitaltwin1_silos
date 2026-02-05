from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class ReferenceParam(BaseModel):
    avg: List[Optional[float]]
    lowerThresholdModerate: List[Optional[float]]
    lowerThresholdCritical: List[Optional[float]]
    upperThresholdModerate: List[Optional[float]]
    upperThresholdCritical: List[Optional[float]]
    max: Optional[List[Optional[float]]] = None
    min: Optional[List[Optional[float]]] = None

class Reference(BaseModel):
    measure: str
    name: str
    description: Optional[str] = None
    referenceGroupId: str
    referenceType: str
    referenceCategory: str
    referenceParam: ReferenceParam
    referenceId: str
    referenceMode: str
    clientId: str
    creation: int
    modified: int

class BatchOccurrenceValue(BaseModel):
    chickenBreed: Optional[str] = None
    gender: Optional[str] = None
    averageWeight: Optional[float] = None
    amount: Optional[int] = None

class BatchOccurrence(BaseModel):
    time: int
    type: str
    value: Any # Keep as Any as it can vary widely for other occurrence types
    batchOccurrenceId: str
    creation: int
    modified: int

class Geolocation(BaseModel):
    autoRefresh: bool
    cityCode: int
    city: str
    state: str
    region: str
    country: str
    latitude: float
    longitude: float
    elevation: float
    utcOffset: int
    ianaTimeZone: Optional[str] = None
    lastModified: int

class AmbienceResultDetail(BaseModel):
    batchDay: int
    start: int
    stop: int
    time: List[int]
    percentageInBetween: List[Optional[float]]
    percentageAboveLimit: List[Optional[float]]
    percentageUnderLimit: List[Optional[float]]
    minMeasured: List[Optional[float]]
    maxMeasured: List[Optional[float]]
    avgMeasured: List[Optional[float]]
    minReference: float
    maxReference: float

class AmbienceMeasureResult(BaseModel):
    measure: str
    deviceLocation: str
    result: List[AmbienceResultDetail]

class Ambience(BaseModel):
    batchId: str
    batchName: str
    batchType: str
    clientId: str
    clientName: str
    environmentId: str
    environmentName: str
    geolocation: Geolocation
    city: str
    latitude: float
    longitude: float
    lastModified: int
    start: int
    stop: int
    result: List[AmbienceMeasureResult]

class Batch(BaseModel):
    environmentId: str
    name: str
    initialDate: int
    finalDate: int
    batchDayCount: int
    batchType: str
    batchStatus: str
    batchReferences: Dict[str, Any]
    batchParam: Dict[str, Any]
    batchOccurrenceList: List[BatchOccurrence]
    batchTargetWeight: Optional[int] = None
    batchId: str
    creation: int
    modified: int
    clientId: str
    clientName: str
    environmentName: str

# --- New Models for the top-level 'consumption' object ---
class FeedMetrics(BaseModel):
    reference: Optional[float] = None
    referencePerBird: Optional[float] = None
    manual: Optional[float] = None
    manualPerBird: Optional[float] = None
    measured: Optional[float] = None
    measuredPerBird: Optional[float] = None

class FeedDeliveryMetrics(BaseModel):
    manual: Optional[float] = None
    measured: Optional[float] = None
    measuredByChannel: Optional[List[Dict[str, Any]]] = None # List of {"channel": int, "value": float}
    numberOfDeliveriesManual: Optional[int] = None
    numberOfDeliveriesMeasured: Optional[int] = None

class GasDeliveryMetrics(BaseModel):
    measured: Optional[float] = None
    numberOfDeliveriesMeasured: Optional[int] = None

class ConsumptionItem(BaseModel): # This is for items within the "preBatchInfo" and "result" lists
    batchAge: int
    start: int
    stop: int
    feed: Optional[FeedMetrics] = None
    feedDelivery: Optional[FeedDeliveryMetrics] = None
    gasDelivery: Optional[GasDeliveryMetrics] = None
    siloEmptyTime: Optional[int] = None
    siloNoConsumptionTime: Optional[int] = None

class ConsumptionGeolocation(BaseModel):
    autoRefresh: Optional[bool] = None
    cityCode: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation: Optional[float] = None
    utcOffset: Optional[int] = None
    ianaTimeZone: Optional[str] = None
    lastModified: Optional[int] = None

class Consumption(BaseModel):
    batchId: str
    batchName: str
    batchType: str
    clientId: str
    clientName: str
    environmentId: str
    environmentName: str
    geolocation: Optional[ConsumptionGeolocation] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    lastModified: int
    start: int
    stop: int
    preBatchInfo: Optional[List[ConsumptionItem]] = Field(None, alias=", ")
    result: List[ConsumptionItem]

# Update SiloData model to include this new top-level "consumption"
class SiloData(BaseModel):
    batch: Batch
    ambience: Union[Ambience, str, None]
    consumption: Union[Consumption, str, None] = None # Allow Consumption object, string, or None