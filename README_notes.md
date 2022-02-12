
## Decisions
1. Spotify authorization flow
We need to use a flow that authorizes with a user. This is because in those flows,
the access token is tied to a user. This is how hitting /api/me gives data
specific to that user. This gives the best option of authorization code flow.
The question becomes, how do we implement a way for a user to authorize on
initialization? And how do we prevent access token & refresh tokens up-to-date?
