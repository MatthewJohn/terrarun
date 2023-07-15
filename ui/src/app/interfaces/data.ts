export interface DataItem<T> {
    data: T;
}

export interface DataList<T> {
    data: T[];
}

export interface DataItemWithIncluded<T, I> {
    data: T;
    included: I[];
}

export interface DataListWithIncluded<T, I> {
    data: T[];
    included: I[];
}
