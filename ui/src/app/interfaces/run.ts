export interface RunAttributes {
    "actions": {
        "is-cancelable": boolean;
        "is-confirmable": boolean;
        "is-discardable": boolean;
        "is-force-cancelable": boolean;
    };
    "canceled-at": null | string;
    "created-at": string;
    "has-changes": boolean;
    "auto-apply": boolean;
    "allow-empty-apply": boolean;
    "is-destroy": boolean;
    "message": string | null;
    "plan-only": boolean;
    "source": string,
    // @TODO Replace 'any'
    "status-timestamps": any;
    "status": string;
    "trigger-reason": string;
    "target-addrs": null | string[];
    "permissions": {
        "can-apply": boolean;
        "can-cancel": boolean;
        "can-comment": boolean;
        "can-discard": boolean;
        "can-force-execute": boolean;
        "can-force-cancel": boolean;
        "can-override-policy-check": boolean;
    },
    "refresh": boolean;
    "refresh-only": boolean;
    "replace-addrs": string[] | null;
    // @TODO Fix this type
    "variables": any[];
}

export interface RunRelationships {
    "apply": {
        'data': {
            'id': string;
            'type': string;
        }
    } | {};
    "comments": {};
    "configuration-version": {
        'data': {
            'id': string;
            'type': string;
        }
    };
    "cost-estimate": {};
    "created-by": {
        "data": {
            "id": string;
            "type": string;
        },
        "links": {
            "related": string;
        }
    } | {};
    "input-state-version": {},
    "plan": {
        'data': {
            'id': string;
            'type': string;
        }
    } | {};
    "run-events": {};
    "policy-checks": {};
    "workspace": {
        'data': {
            'id': string;
            'type': string;
        }
    };
    "workspace-run-alerts": {};
    "task-stages": {
        "data": {
            'id': string;
            'type': string;
        }[]
    }
}