from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwk, jwt, JWTError
import requests
import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

COGNITO_ISSUER = f"https://cognito-idp.{config.COGNITO_REGION}.amazonaws.com/{config.COGNITO_USERPOOL_ID}"
COGNITO_AUDIENCE = config.COGNITO_CLIENT_ID
ALGORITHMS = ["RS256"]

def get_cognito_public_keys():
    jwks_url = f"{COGNITO_ISSUER}/.well-known/jwks.json"
    jwks = requests.get(jwks_url).json()
    public_keys = {}
    for key in jwks['keys']:
        kid = key['kid']
        rsa_key = jwk.construct(key)
        public_keys[kid] = rsa_key
    return public_keys

COGNITO_PUBLIC_KEYS = get_cognito_public_keys()

async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        headers = jwt.get_unverified_headers(token)
        kid = headers['kid']
        rsa_key = COGNITO_PUBLIC_KEYS.get(kid)
        if rsa_key:
            payload = jwt.decode(token, rsa_key.to_dict(), algorithms=ALGORITHMS, audience=COGNITO_AUDIENCE, issuer=COGNITO_ISSUER)
            return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is invalid or expired")
