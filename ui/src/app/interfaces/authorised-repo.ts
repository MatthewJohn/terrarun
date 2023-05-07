import { Relationship } from "./response"
import { DataItem } from "./data"

export interface AuthorisedRepo {
    "display-identifier": string;
    "name": string;
}

export interface AuthorisedRepoRelationships {
    "oauth-token": DataItem<Relationship>,
}
