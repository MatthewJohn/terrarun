export interface ResponseObject<T> {
    id: string;
    type: string;
    attributes: T;
}

export interface TypedResponseObject<N, T> {
    id: string;
    type: N;
    attributes: T;
}

export interface ResponseObjectWithRelationships<T, R> {
    id: string;
    type: string;
    attributes: T;
    relationships: R;
}

export interface TypedResponseObjectWithRelationships<N, T, R> {
    id: string;
    type: N;
    attributes: T;
    relationships: R;
}

export interface Relationship {
    id: string;
    type: string;
}
