"attributes"
import { DataItem } from "./data"
import { Relationship } from "./response"

export interface ConfigurationVersionAttributes {
    "auto-queue-runs": boolean;
    "error": string | null;
    "error-message": string | null;
    "source": string;
    "speculative": boolean;
    "status": string;
    // @TODO Fix this type
    "status-timestamps": any;
    "upload-url": string;
};

export interface ConfigurationVersionRelationships {
    "ingress-attributes": DataItem<Relationship> | {};
};
