export interface ProjectWorkspaceVcsConfigVcsChild {
    branch: string | null | undefined;
    "ingress-submodules": boolean | undefined;
    "tags-regex": string | null | undefined;
    identifier: string | null | undefined;
    "display-identifier": string | null | undefined;
    "oauth-token-id": string | null | undefined;
    "webhook-url": string | undefined;
    "repository-http-url": string | undefined;
    "service-provider": string | undefined;
}

export interface ProjectWorkspaceVcsConfig {
    "vcs-repo": ProjectWorkspaceVcsConfigVcsChild | null;
    "file-triggers-enabled": boolean | undefined;
    "trigger-prefixes": string[] | undefined;
    "trigger-patterns": string[] | undefined;
}
