export interface ProjectWorkspaceVcsConfigVcsChild {
    branch: string | null;
    "ingress-submodules": boolean | undefined;
    "tags-regex": string | null;
    identifier: string;
    "display-identifier": string | undefined;
    "oauth-token-id": string;
    "webhook-url": string | undefined;
    "repository-http-url": string | undefined;
    "service-provider": string | undefined;
}

export interface ProjectWorkspaceVcsConfig {
    "vcs-repo": ProjectWorkspaceVcsConfigVcsChild | null;
    "file-triggers-enabled": boolean;
    "trigger-prefixes": string[];
    "trigger-patterns": string[];
}
