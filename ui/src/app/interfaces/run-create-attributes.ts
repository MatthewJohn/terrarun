export interface RunCreateAttributes {
    "message": string | null;
    "terraform-version": string | null;
    "plan-only": boolean;
    "is-destroy": boolean;
    "refresh": boolean;
    "refresh-only": boolean;
}