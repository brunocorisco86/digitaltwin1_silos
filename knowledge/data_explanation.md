# Data Explanation: Silo Digital Twin Data

This document describes the structure, purpose, and granularity of the JSON data files representing the digital twin of silos, specifically in a poultry farming context. Each JSON file typically represents a single "batch" of poultry farming data over a specific period.

## Overall Purpose

The data provides a comprehensive overview of a poultry farming batch, encompassing details about the batch itself, its environmental conditions, and various operational occurrences throughout its lifecycle. This data is crucial for monitoring performance, identifying anomalies, and optimizing farming processes.

## Main Sections

The JSON data is primarily divided into two main sections: `batch` and `ambience`.

### 1. `batch` Section

This section contains metadata and event-driven data related to a specific poultry farming batch.

-   **`batchId`, `name`, `environmentId`, `environmentName`**: Unique identifiers and names for the batch and its associated environment (e.g., a specific aviary).
-   **`initialDate`, `finalDate`**: Timestamps (likely Unix epoch seconds) marking the start and end of the batch's lifecycle.
-   **`batchDayCount`**: The total duration of the batch in days.
-   **`batchType`**: The type of farming activity (e.g., "poultry-farming").
-   **`batchStatus`**: The current status of the batch (e.g., "finished", "active").
-   **`batchTargetWeight`**: The target weight for the poultry in this batch.
-   **`clientId`, `clientName`**: Identifiers for the client associated with this batch.
-   **`creation`, `modified`**: Timestamps indicating when the batch record was created and last modified.
-   **`batchParam`**: A dictionary that may contain various batch-specific parameters, which can vary.

#### `batchReferences`

This sub-section provides reference data or benchmarks for various measures. These references are used to evaluate the performance or conditions against established standards.

-   **`referenceList`**: An array of reference objects, each defining parameters for a specific `measure` (e.g., "gasPerBird", "mortality", "feedConvertionRate", "poultryWeight", "waterPerBird", "dailyGain", "accumulatedGainFactor", "energyPerBird").
    -   **`measure`**: The specific metric being referenced.
    -   **`name`, `description`**: Human-readable name and description of the reference.
    -   **`referenceGroupId`, `referenceType`, `referenceCategory`, `referenceMode`, `referenceId`**: Categorization and identification for the reference.
    -   **`referenceParam`**: Contains arrays for `avg` (average), `lowerThresholdModerate`, `lowerThresholdCritical`, `upperThresholdModerate`, `upperThresholdCritical`. These arrays likely represent daily or weekly reference values over the batch duration. The values `min` and `max` are also present for some ambience-related measures.
    -   **Granularity**: These references are typically defined at a **daily or weekly granularity** across the batch's life, providing benchmarks for performance and environmental factors over time.

#### `batchOccurrenceList`

This is a critical array detailing various events and occurrences throughout the batch's lifecycle.

-   **`time`**: Timestamp of when the occurrence happened.
-   **`type`**: The type of event (e.g., "eliminated", "chickPlacement", "logbook", "mortality", "technicalGuidance", "weighing", "waterConsumption", "feedDelivery", "other").
-   **`value`**: The associated data for the event. This field's type and structure vary significantly based on the `type` of occurrence:
    -   `chickPlacement`: An object with details like `chickenBreed`, `gender`, `averageWeight`, `amount`.
    -   `logbook`, `technicalGuidance`: String descriptions.
    -   `mortality`, `waterConsumption`, `feedDelivery`: Numerical values.
    -   `weighing`: An object with `averageWeight` and `amount`.
    -   `other`: Can be a string or an object containing specific check-list items (e.g., "PoultryCheckListItem", "ConformityStatus").
-   **`batchOccurrenceId`**: Unique identifier for each occurrence.
-   **Granularity**: Each entry represents a discrete event, so the granularity is at the level of **individual events with specific timestamps**.

### 2. `ambience` Section

This section focuses on the environmental conditions and their measurements within the silo or farming environment.

-   **`batchId`, `batchName`, `batchType`, `clientId`, `clientName`, `environmentId`, `environmentName`**: Redundant identification information, mirroring the `batch` section.
-   **`geolocation`**: Detailed geographical information about the environment.
    -   **`city`, `state`, `region`, `country`, `latitude`, `longitude`, `elevation`**: Location details.
    -   **`utcOffset`, `ianaTimeZone`**: Time zone information.
    -   **`lastModified`**: Timestamp of the last modification.
-   **`start`, `stop`**: Timestamps defining the period for which ambience data is reported.
-   **`lastModified`**: Timestamp of the last modification for the ambience data.

#### `result`

This is an array containing detailed time-series data for various environmental measures.

-   **`measure`**: The specific environmental metric (e.g., "windSpeed", "nh3" (ammonia), "waterTemperature", "humidity", "thermalComfort", "co2", "soilMoisture", "temperature", "soilTemperature", "luminosity").
-   **`deviceLocation`**: The location within the environment where the measurement was taken (e.g., "back").
-   **`result` (inner array)**: An array of time-aggregated measurement results.
    -   **`batchDay`**: The day of the batch cycle.
    -   **`start`, `stop`**: Timestamps for the start and end of the measurement interval (typically hourly).
    -   **`time`**: An array of timestamps within the interval.
    -   **`percentageInBetween`, `percentageAboveLimit`, `percentageUnderLimit`**: Arrays indicating the percentage of time the measured value was within, above, or below defined reference limits during the interval.
    -   **`minMeasured`, `maxMeasured`, `avgMeasured`**: Arrays of minimum, maximum, and average measured values within the interval.
    -   **`minReference`, `maxReference`**: The lower and upper reference limits for the measure during that period.
-   **Granularity**: The data within the `ambience.result` section is typically at an **hourly granularity**, providing detailed time-series measurements and their comparison against reference ranges.

## Conclusion

This data structure supports detailed analysis of poultry farming operations, allowing for the correlation of batch events with environmental conditions and performance metrics. The varied granularity, from batch-level metadata to hourly environmental readings, enables both high-level overview and in-depth investigation of farm dynamics.
