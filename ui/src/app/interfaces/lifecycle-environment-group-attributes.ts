import { DataItem, DataList } from "./data";
import { Relationship } from "./response";

export interface LifecycleEnvironmentGroupAttributes {
    "order": number;
    "minimum-runs": number | null;
    "minimum-successful-plans": number | null;
    "minimum-successful-applies": number | null;
}

export interface LifecycleEnvironmentUpdateAttributes {
    "minimum-runs": number | null | undefined;
    "minimum-successful-plans": number | null | undefined;
    "minimum-successful-applies": number | null | undefined;
}

export interface LifecycleEnvironmentGroupRelationships {
    lifecycle: DataItem<Relationship>;
    "lifecycle-environments": DataList<Relationship>;
}
