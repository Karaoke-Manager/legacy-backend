from motor.core import AgnosticClient, AgnosticClientSession, AgnosticDatabase, AgnosticCollection, AgnosticCursor, \
    AgnosticCommandCursor, AgnosticLatentCommandCursor, AgnosticChangeStream


class AsyncIOMotorClient(AgnosticClient["AsyncIOMotorSession",
                                        "AsyncIOMotorDatabase",
                                        "AsyncIOMotorCommandCursor",
                                        "AsyncIOMotorChangeStream"]):
    pass


class AsyncIOMotorClientSession(AgnosticClientSession[AsyncIOMotorClient]):
    pass


class AsyncIOMotorDatabase(AgnosticDatabase[AsyncIOMotorClientSession,
                                            AsyncIOMotorClient,
                                            "AsyncIOMotorCollection",
                                            "AsyncIOMotorCursor",
                                            "AsyncIOMotorCommandCursor",
                                            "AsyncIOMotorLatentCommandCursor",
                                            "AsyncIOMotorChangeStream"]):
    pass


class AsyncIOMotorCollection(AgnosticCollection[AsyncIOMotorClient,
                                                AsyncIOMotorDatabase,
                                                "AsyncIOMotorCursor",
                                                "AsyncIOMotorCursor",
                                                "AsyncIOMotorLatentCommandCursor",
                                                "AsyncIOMotorChangeStream"]):
    pass


class AsyncIOMotorCursor(AgnosticCursor[AsyncIOMotorClientSession, AsyncIOMotorCollection]):
    pass


class AsyncIOMotorCommandCursor(AgnosticCommandCursor[AsyncIOMotorClientSession, AsyncIOMotorCollection]):
    pass


class AsyncIOMotorLatentCommandCursor(AgnosticLatentCommandCursor[AsyncIOMotorClientSession, AsyncIOMotorCollection]):
    pass


class AsyncIOMotorChangeStream(AgnosticChangeStream[AsyncIOMotorClientSession]):
    pass

# TODO: AsyncIOMotorGridFSBucket

# TODO: AsyncIOMotorGridIn

# TODO: AsyncIOMotorGridOut

# TODO: AsyncIOMotorGridOutCursor
