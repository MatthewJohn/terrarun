export interface DataObject<T> {
    id: string;
    type: string;
    attributes: T;
}
