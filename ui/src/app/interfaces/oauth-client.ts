export interface OauthClient {
    "created-at": string;
    "callback-url": string;
    "connect-path": string;
    "service-provider": string;
    "service-provider-display-name": string;
    "name": string | null;
    "http-url": string | null;
    "api-url": string | null;
    "key": string | null;
    "secret": string | null;
    "rsa-public-key": string | null;
}
