export interface AdminTerraformVersion {
    version: string;
    url: string | null;
    "checksum-url": string | null;
    sha: string | null;
    deprecated: boolean;
    "deprecated-reason": string | null;
    official: boolean;
    enabled: boolean;
    beta: boolean;
    usage: number | undefined;
    "created-at": string | undefined;
}
