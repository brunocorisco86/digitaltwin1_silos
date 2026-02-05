from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ReferenceParam(BaseModel):
    avg: List[Optional[float]]
    lowerThresholdModerate: List[Optional[float]]
    lowerThresholdCritical: List[Optional[float]]
    upperThresholdModerate: List[Optional[float]]
    upperThresholdCritical: List[Optional[float]]
    max: Optional[List[Optional[float]]] = None # Added for ambience references
    min: Optional[List[Optional[float]]] = None # Added for ambience references

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
    value: Any # Can be str, int, float, or BatchOccurrenceValue
    batchOccurrenceId: str
    creation: int
    modified: int

class Batch(BaseModel):
    environmentId: str
    name: str
    initialDate: int
    finalDate: int
    batchDayCount: int
    batchType: str
    batchStatus: str
    batchReferences: Dict[str, Any] # This is complex, keeping as dict for now
    batchParam: Dict[str, Any]
    batchOccurrenceList: List[BatchOccurrence]
    batchTargetWeight: int
    batchId: str
    creation: int
    modified: int
    clientId: str
    clientName: str
    environmentName: str

class Geolocation(BaseModel):
    autoRefresh: bool
    cityCode: int
    city: str
    state: str
    region: str
    country: str
    latitude: float
    longitude: float
    elevation: int
    utcOffset: int
    ianaTimeZone: str
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

class SiloData(BaseModel):
    batch: Batch
    ambience: Ambience
