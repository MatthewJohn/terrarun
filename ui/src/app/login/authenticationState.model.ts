export interface AuthenticationState {
    loggedIn: boolean;
    username: string | null;
    userId: string | null;
}