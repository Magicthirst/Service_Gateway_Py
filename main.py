import traceback
from contextlib import asynccontextmanager
from typing import Callable

import grpc
import uvicorn
from fastapi import FastAPI, Body, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from fastapi.routing import APIRoute
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from httpx import ConnectError
from pydantic import create_model

import config
import control_outlet_pb2 as pb2
import control_outlet_pb2_grpc as pb2_grpc
from config import auth_url, hosts_url, sync_outlet_url, async_client, sync_main_url
from models import *


class LoggingMiddleware(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            print(f"route: {request.url}")
            print(f"body: {request.body()}")
            return await original_route_handler(request)

        return custom_route_handler


hosts_sessions: dict[str, int] = dict()
sessions_players: dict[int, set[str]] = dict()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
security = HTTPBearer()
sync_channel = grpc.insecure_channel(sync_outlet_url)
sync_stub = pb2_grpc.SyncControlOutletStub(sync_channel)


@asynccontextmanager
async def lifecycle(app: FastAPI):
    yield
    sync_channel.close()


@app.post('/hosts', summary='register')
async def register() -> Host:
    try:
        auth_response = await async_client.post(f'{auth_url}/')
    except ConnectError:
        return Response(status_code=503, content='auth')

    host_uuid = auth_response.json()['uuid']

    try:
        host_response = await async_client.post(f'{hosts_url}/{host_uuid}')
    except ConnectError:
        return Response(status_code=503, content='hosts')

    if host_response.status_code != 200:
        return Response(status_code=host_response.status_code)
    else:
        return Host(**host_response.json())


@app.get(
    '/hosts/{host}/access_token',
    summary='login by host uuid',
    responses={404: {'model': Message}}
)
async def login(host: str) -> create_model('LoginToken', token=(str, True)):
    try:
        auth_response = await async_client.get(f'{auth_url}/login/{host}')
    except ConnectError:
        return Response(status_code=503, content='auth')

    return {'token': auth_response.json()['token']}\
        if auth_response.status_code == 200\
        else Response(status_code=auth_response.status_code)


@app.get(
    '/hosts/access_token/renew',
    summary='renew token',
    responses={404: {'model': Message}}
)
async def renew(authorization: HTTPAuthorizationCredentials = Depends(security)) -> create_model('LoginToken', token=(str, True)):
    try:
        response = await async_client.get(f'{auth_url}/renew', headers={'authorisation': authorization.credentials})
    except ConnectError:
        return Response(status_code=503, content='auth')

    return {'token': response.json()}\
        if response.status_code == 200\
        else Response(status_code=response.status_code)


@app.get(
    '/hosts/{host}',
    summary='get host by uuid',
    responses={200: {'model': Host}, 404: {'model': NotFoundThisOrOther}, 401: {'model': Message}}
)
async def get(host: str, authorization: HTTPAuthorizationCredentials = Depends(security)):
    if auth_err_result := await check_access(host, authorization):
        return auth_err_result

    try:
        response = await async_client.get(f'{hosts_url}/{host}')
    except ConnectError:
        return Response(status_code=503, content='hosts')

    return Host(**response.json()) if response.status_code == 200 else JSONResponse(status_code=response.status_code, content=response.json())


@app.put(
    '/hosts/{host}/only_friends',
    summary='set is {host} welcomes only friends',
    responses={404: {'model': NotFoundThisOrOther}, 401: {'model': Message}}
)
async def set_only_friends(
        host: str,
        only_friends: bool = Body(embed=True),
        authorization: HTTPAuthorizationCredentials = Depends(security)
):
    if auth_err_result := await check_access(host, authorization):
        return auth_err_result

    try:
        response = (await async_client.put(f'{hosts_url}/{host}/only_friends', json={'only_friends': only_friends}))
    except ConnectError:
        return Response(status_code=503, content='hosts')

    return Response(status_code=response.status_code, content=response.content)


@app.put(
    '/hosts/{host}/allow_nonames',
    summary='set is {host} welcomes nonames',
    responses={404: {'model': NotFoundThisOrOther}, 401: {'model': Message}}
)
async def set_allow_nonames(
        host: str,
        allow_nonames: bool = Body(embed=True),
        authorization: HTTPAuthorizationCredentials = Depends(security)
):
    if auth_err_result := await check_access(host, authorization):
        return auth_err_result

    try:
        response = (await async_client.put(f'{hosts_url}/{host}/allow_nonames', json={'allow_nonames': allow_nonames}))
    except ConnectError:
        return Response(status_code=503, content='hosts')

    return Response(status_code=response.status_code, content=response.content)


@app.post(
    '/hosts/{host}/friends',
    summary='befriend',
    responses={404: {'model': NotFoundThisOrOther}, 401: {'model': Message}, 400: {'model': Message}}
)
async def befriend(host: str, friend: str, authorization: HTTPAuthorizationCredentials = Depends(security)):
    if auth_err_result := await check_access(host, authorization):
        return auth_err_result

    try:
        response = await async_client.post(f'{hosts_url}/{host}/friends/{friend}')
    except ConnectError:
        return Response(status_code=503, content='hosts')

    return Response(status_code=response.status_code, content=response.content)


@app.delete(
    '/hosts/{host}/friends/{former_friend}',
    summary='unfriend',
    responses={404: {'model': NotFoundThisOrOther}, 401: {'model': Message}}
)
async def unfriend(host: str, former_friend: str, authorization: HTTPAuthorizationCredentials = Depends(security)):
    if auth_err_result := await check_access(host, authorization):
        return auth_err_result

    try:
        response = await async_client.delete(f'{hosts_url}/{host}/friends/{former_friend}')
    except ConnectError:
        return Response(status_code=503, content='hosts')

    return Response(status_code=response.status_code, content=response.content)


@app.post(
    '/hosts/{host}/banlist',
    summary='ban',
    responses={404: {'model': NotFoundThisOrOther}, 401: {'model': Message}, 400: {'model': Message}}
)
async def ban(host: str, banned: str, authorization: HTTPAuthorizationCredentials = Depends(security)):
    if auth_err_result := await check_access(host, authorization):
        return auth_err_result

    try:
        response = await async_client.post(f'{hosts_url}/{host}/banlist/{banned}')
    except ConnectError:
        return Response(status_code=503, content='hosts')

    return Response(status_code=response.status_code, content=response.content)


@app.delete(
    '/hosts/{host}/banlist/{banned}',
    summary='unban',
    responses={404: {'model': NotFoundThisOrOther}, 401: {'model': Message}}
)
async def unban(host: str, banned: str, authorization: HTTPAuthorizationCredentials = Depends(security)):
    if auth_err_result := await check_access(host, authorization):
        return auth_err_result

    try:
        response = await async_client.delete(f'{hosts_url}/{host}/banlist/{banned}')
    except ConnectError:
        return Response(status_code=503, content='hosts')

    return Response(status_code=response.status_code, content=response.content)


@app.post(
    '/sessions',
    summary='launch session',
    responses={
        201: {
            'model': LaunchSessionResponse,
            'headers': {
                'Location': {
                    'description': 'URL of Sync server on which game session is hosted',
                    'schema': {'type': 'string', 'format': 'uri'}
                }
            }
        },
        404: {'model': NotFoundThisOrOther},
        401: {'model': Message},
        409: {'model': Message},
        503: {'model': Message},
        500: {'model': Message}
    }
)
async def launch_session(host: str = Body(embed=True), authorization: HTTPAuthorizationCredentials = Depends(security)):
    if auth_err_result := await check_access(host, authorization):
        return auth_err_result

    try:
        try:
            request = pb2.SessionLaunchInfo(hostId=host)
            response = sync_stub.Launch(request)
            sessions_players[response.sessionId] = [host]
            return JSONResponse(
                status_code=201,
                headers={
                    'Location': sync_main_url
                },
                content={
                    "session_id": response.sessionId,
                    "source_of_truth_key": response.sourceOfTruthKey
                }
            )
        except grpc.RpcError as e_:
            e: grpc.Call = e_
            traceback.print_exception(e)
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                return JSONResponse(
                    status_code=409,
                    content={"message": "A session by this host is already hosted"}
                )
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                raise ConnectError(e.details())
            else:
                raise Exception()
    except ConnectError as e:
        traceback.print_exception(e)
        return JSONResponse(
            status_code=503,
            content={"message": "Cannot connect to sync service."}
        )
    except Exception as e:
        traceback.print_exception(e)
        return JSONResponse(
            status_code=500,
            content={"message": "An internal server error occurred"}
        )


@app.post(
    '/sessions/players',
    summary='Join a session as a player',
    responses={
        200: {
            'model': create_model('JoinSessionResponse', session_id=(int, ...)),  # The current return content
            'description': 'Player successfully joined the session.',
            'headers': {
                'Location': {
                    'description': 'URL of the Sync server where the game session is hosted.',
                    'schema': {'type': 'string', 'format': 'uri'}
                }
            }
        },
        400: {'model': Message, 'description': 'Bad Request, e.g., guest already in session or invalid request.'},
        401: {'model': Message, 'description': 'Unauthorized: The provided authentication token is invalid.'},
        404: {'model': Message, 'description': 'Not Found: No session found for the specified host, or guest is not welcome.'},
        503: {'model': Message, 'description': 'Service Unavailable: External service (hosts or sync) is unreachable.'},
        500: {'model': Message, 'description': 'Internal Server Error: An unexpected error occurred on the server.'}
    }
)
async def join(host: str = Body(embed=True), guest: str = Body(embed=True), authorization: HTTPAuthorizationCredentials = Depends(security)):
    if auth_err_result := await check_access(guest, authorization):
        return auth_err_result

    if host not in hosts_sessions:
        return Response(status_code=404, content='no session')

    try:
        welcomes_response = await async_client.get(f'{hosts_url}/{host}/welcomes/{guest}')
        if welcomes_response.status_code == 404:
            return Response(status_code=404, content='not welcome')
        if welcomes_response.is_error:
            return Response(status_code=400)
    except ConnectError:
        return Response(status_code=503, content='hosts')

    try:
        try:
            session_id = hosts_sessions[host]
            request = pb2.WelcomeRequest(sessionId=session_id, playerId=guest)
            response = sync_stub.Welcome(request)
            return JSONResponse(
                status_code=200,
                headers={'Location': sync_main_url},
                content={'session_id': response.sessionId}
            )
        except grpc.RpcError as e_:
            e: grpc.Call = e_
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                raise ConnectError(e.details())
            else:
                raise Exception()
    except ConnectError as e:
        traceback.print_exception(e)
        return Response(status_code=503, content='sync')
    except Exception as e:
        traceback.print_exception(e)
        return Response(status_code=500)


async def check_access(host: str, authorization: HTTPAuthorizationCredentials) -> Response | None:
    token = authorization.credentials

    try:
        response = await async_client.head(f'{auth_url}/{host}', headers={'authorisation': token})
    except ConnectError:
        return Response(status_code=503, content='auth')

    if response.is_error:
        return Response(status_code=response.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    content = {'status_code': 10422, 'message': exc_str, 'data': await request.json()}
    print(422, f'{content=}')
    return JSONResponse(content=content, status_code=422)


if __name__ == '__main__':
    uvicorn.run(app, host=config.host, port=config.port, log_level='trace')
