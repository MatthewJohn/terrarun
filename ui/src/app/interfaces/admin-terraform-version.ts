export interface AdminTerraformVersion {
    version: string;
    url: string | null;
    "checksum-url": string | null;
    sha: string | null;
    deprecated: boolean;
    "deprecated-reason": string | null;
    enabled: boolean;
    // These are present in the response, but not in post data
    beta: boolean | undefined;
    official: boolean | undefined;
    usage: number | undefined;
    "created-at": string | undefined;
}
