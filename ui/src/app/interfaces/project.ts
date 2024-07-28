export interface ProjectAttributes {
    "allow-destroy-plan": boolean;
    "auto-apply": boolean;
    "created-at": string;
    "description": string | null;
    "execution-mode": string;
    "file-triggers-enabled": boolean;
    "global-remote-state": boolean
    "latest-change-at": string;
    "name": string;
    "operations": boolean;
    "queue-all-runs": boolean;
    "source": string;
    "source-name": string | null;
    "source-url": string | null;
    "speculative-enabled": boolean;
    "structured-run-output-enabled": boolean;
    "terraform-version": string | null;
    "trigger-prefixes": string[];
    "trigger-patterns": string[];
    "updated-at": string;
    "vcs-repo": {
        "branch": string | null;
        "ingress-submodules": string | null;
        "tags-regex": string | null;
        "identifier": string | null;
        "display-identifier": string | null;
        "oauth-token-id": string | null;
        "webhook-url": string | null;
        "repository-http-url": string | null;
        "service-provider": string | null;
    } | null;
    "vcs-repo-identifier": string | null;
    "working-directory": string | null;
    "setting-overwrites": {
        "execution-mode": string | null;
    }
}

export interface ProjectRelationships {
    "lifecycle": {
        "data": {
            "id": string;
            "type": string;
        };
    },
    "organization": {
        "data": {
            "id": string;
            "type": string;
        }
    };
    "workspaces": {
        "data": {
            "id": string;
            "type": string;
        }[];
    };
}
