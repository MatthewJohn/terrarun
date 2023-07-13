
export interface IngressAttributeAttribues {
    "branch": string;
    "clone-url": string;
    "commit-message": string;
    "commit-sha": string;
    "commit-url": string;
    "compare-url": string;
    "identifier": string;
    "is-pull-request": boolean;
    "on-default-branch": boolean;
    "pull-request-number": string | null;
    "pull-request-url": string | null;
    "pull-request-title": string | null;
    "pull-request-body": string | null;
    "tag": string;
    "sender-username": string;
    "sender-avatar-url": string;
    "sender-html-url": string;
}