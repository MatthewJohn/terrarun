export interface TerraformVersion {
    tool: string;
    version: string;
    url: string;
    sha: string;
    deprecated: boolean;
    "deprecated-reason": string | null;
    enabled: boolean;
    beta: boolean;
    official: boolean;
}
