import { DataItem } from "./data";
import { Relationship } from "./response";

export interface LifecycleEnvironmentAttributes {
    "environment-name": string;
}

export interface LifecycleEnvironmentRelationships {
    lifecycle: DataItem<Relationship>;
    "lifecycle-environment-group": DataItem<Relationship>;
    "environment": DataItem<Relationship>;
}
