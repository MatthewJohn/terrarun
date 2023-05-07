export interface ProjectWorkspaceVcsConfig {
    branch: string | null;
    "ingress-submodules": boolean;
    "tags-regex": string | null;
    identifier: string;
    "display-identifier": string;
    "oauth-token-id": string;
    "webhook-url": string;
    "repository-http-url": string;
    "service-provider": string;
}